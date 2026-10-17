#!/usr/bin/env python3
"""Safely install the existing Sidequest office GLB from its verified asset kit."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import lzma
import os
import re
import shutil
import stat
import struct
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import BinaryIO
from urllib.parse import unquote_to_bytes


EXPECTED_ARCHIVE_SIZE = 535_951_540
EXPECTED_ARCHIVE_SHA256 = "f7159fbda50771486d65e1a5bd2a42d265120a422d88a686471a9bbb6fb60a95"
ARCHIVE_PART_STEM = "Sidequest_Complete_Art_Kit_2026-10-07.tar.xz.part"
ARCHIVE_PART_NAMES = tuple(f"{ARCHIVE_PART_STEM}{index:02d}" for index in range(1, 9))
RUNTIME_GLB_NAME = "Sidequest_Runtime_Environment_Batched.glb"
OUTPUT_GLB_NAME = "office.glb"

MAX_MEMBER_COUNT = 100_000
MAX_MEMBER_SIZE = 2 * 1024 * 1024 * 1024
MAX_TOTAL_UNCOMPRESSED_SIZE = 8 * 1024 * 1024 * 1024
MAX_SELECTED_OUTPUT_SIZE = 2 * 1024 * 1024 * 1024
MAX_GLTF_JSON_SIZE = 64 * 1024 * 1024
MAX_DATA_URI_SIZE = 64 * 1024 * 1024
MAX_GLTF_RESOURCE_COUNT = 100_000
MAX_PATH_LENGTH = 4_096
COPY_CHUNK_SIZE = 1024 * 1024
MAX_TAR_STREAM_SIZE = MAX_TOTAL_UNCOMPRESSED_SIZE + MAX_MEMBER_COUNT * 512 + 1024 * 1024

GLB_MAGIC = 0x46546C67
GLB_JSON_CHUNK = 0x4E4F534A
GLB_BINARY_CHUNK = 0x004E4942


class InstallError(RuntimeError):
    """Raised when the input kit or its selected scene assets are unsafe or invalid."""


class _CappedReader:
    """Bound the decompressed tar stream, including metadata records."""

    def __init__(self, stream: BinaryIO, limit: int):
        self._stream = stream
        self._limit = limit
        self._read = 0

    def read(self, size: int = -1) -> bytes:
        remaining = self._limit - self._read
        request_size = min(COPY_CHUNK_SIZE, remaining + 1) if size is None or size < 0 else min(size, remaining + 1)
        data = self._stream.read(request_size)
        self._read += len(data)
        if self._read > self._limit:
            _fail(f"archive expands beyond the {self._limit}-byte read limit")
        return data


def _fail(message: str) -> None:
    raise InstallError(message)


def _validate_expected(expected_size: int, expected_sha256: str) -> None:
    if isinstance(expected_size, bool) or not isinstance(expected_size, int) or expected_size <= 0:
        _fail("expected archive size must be a positive integer")
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        _fail("expected archive SHA-256 must be 64 lowercase hexadecimal characters")


def _regular_file(path: Path, label: str) -> os.stat_result:
    try:
        metadata = path.lstat()
    except OSError as error:
        _fail(f"cannot read {label}: {error.strerror or error}")
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        _fail(f"{label} must be a regular file, not a link or special file")
    return metadata


def _open_regular_file(path: Path, label: str, expected_info: os.stat_result | None = None) -> BinaryIO:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        metadata = os.fstat(descriptor)
    except OSError as error:
        _fail(f"cannot safely open {label}: {error.strerror or error}")
    if not stat.S_ISREG(metadata.st_mode):
        os.close(descriptor)
        _fail(f"{label} must be a regular file, not a link or special file")
    if expected_info is not None and (
        metadata.st_dev != expected_info.st_dev
        or metadata.st_ino != expected_info.st_ino
        or metadata.st_size != expected_info.st_size
    ):
        os.close(descriptor)
        _fail(f"{label} changed while the installer was preparing it")
    return os.fdopen(descriptor, "rb", buffering=0)


def _directory(path: Path, label: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        _fail(f"cannot read {label}: {error.strerror or error}")
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        _fail(f"{label} must be a directory, not a link or special file")


def _snapshot_from_file(archive_path: Path, expected_size: int, expected_sha256: str) -> tuple[BinaryIO, str, int]:
    _validate_expected(expected_size, expected_sha256)
    source_info = _regular_file(archive_path, "archive")
    if source_info.st_size != expected_size:
        _fail(f"archive size mismatch: expected {expected_size} bytes, found {source_info.st_size}")

    snapshot = tempfile.TemporaryFile(mode="w+b")
    digest = hashlib.sha256()
    total = 0
    try:
        with _open_regular_file(archive_path, "archive", source_info) as source:
            while True:
                chunk = source.read(COPY_CHUNK_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                if total > expected_size:
                    _fail("archive grew beyond the validated size while it was being read")
                digest.update(chunk)
                snapshot.write(chunk)
        if total != expected_size:
            _fail(f"archive size mismatch while reading: expected {expected_size} bytes, found {total}")
        actual_hash = digest.hexdigest()
        if actual_hash != expected_sha256:
            _fail(f"archive SHA-256 mismatch: expected {expected_sha256}, found {actual_hash}")
        snapshot.flush()
        snapshot.seek(0)
        return snapshot, actual_hash, total
    except Exception:
        snapshot.close()
        raise


def _snapshot_from_parts(parts_directory: Path, expected_size: int, expected_sha256: str) -> tuple[BinaryIO, str, int]:
    _validate_expected(expected_size, expected_sha256)
    _directory(parts_directory, "parts directory")
    paths = [parts_directory / name for name in ARCHIVE_PART_NAMES]
    metadata = [_regular_file(path, f"archive part {path.name}") for path in paths]
    measured_size = sum(item.st_size for item in metadata)
    if measured_size != expected_size:
        _fail(f"archive parts total {measured_size} bytes; expected exactly {expected_size}")

    snapshot = tempfile.TemporaryFile(mode="w+b")
    digest = hashlib.sha256()
    total = 0
    try:
        for path, original_info in zip(paths, metadata, strict=True):
            current_info = _regular_file(path, f"archive part {path.name}")
            if current_info.st_size != original_info.st_size:
                _fail(f"archive part changed while preparing: {path.name}")
            with _open_regular_file(path, f"archive part {path.name}", original_info) as source:
                while True:
                    chunk = source.read(COPY_CHUNK_SIZE)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > expected_size:
                        _fail("archive parts grew beyond the validated size while being read")
                    digest.update(chunk)
                    snapshot.write(chunk)
        if total != expected_size:
            _fail(f"archive parts read {total} bytes; expected exactly {expected_size}")
        actual_hash = digest.hexdigest()
        if actual_hash != expected_sha256:
            _fail(f"archive SHA-256 mismatch: expected {expected_sha256}, found {actual_hash}")
        snapshot.flush()
        snapshot.seek(0)
        return snapshot, actual_hash, total
    except Exception:
        snapshot.close()
        raise


def _normalized_member_name(raw_name: str, is_directory: bool) -> str:
    if not isinstance(raw_name, str) or not raw_name:
        _fail("archive contains an empty member path")
    if len(raw_name) > MAX_PATH_LENGTH:
        _fail(f"archive member path exceeds the {MAX_PATH_LENGTH}-character limit")
    if raw_name.startswith(("/", "\\")) or "\\" in raw_name or "\0" in raw_name:
        _fail(f"archive member uses an absolute or unsupported path: {raw_name!r}")

    without_trailing = raw_name[:-1] if is_directory and raw_name.endswith("/") else raw_name
    raw_parts = without_trailing.split("/")
    if any(part == "" for part in raw_parts):
        _fail(f"archive member contains an empty path segment: {raw_name!r}")
    if any(part == ".." for part in raw_parts):
        _fail(f"archive member path traversal rejected: {raw_name!r}")
    parts = [part for part in raw_parts if part not in ("", ".")]
    if parts and re.fullmatch(r"[A-Za-z]:", parts[0]):
        _fail(f"archive member uses a drive-qualified path: {raw_name!r}")
    return "/".join(parts) if parts else "."


def _read_exact(stream: BinaryIO, size: int, label: str) -> bytes:
    if size < 0:
        _fail(f"invalid {label} length")
    chunks = bytearray()
    while len(chunks) < size:
        chunk = stream.read(min(COPY_CHUNK_SIZE, size - len(chunks)))
        if not chunk:
            _fail(f"truncated {label}")
        chunks.extend(chunk)
    return bytes(chunks)


def _discard_exact(stream: BinaryIO, size: int, label: str) -> None:
    remaining = size
    while remaining:
        chunk = stream.read(min(COPY_CHUNK_SIZE, remaining))
        if not chunk:
            _fail(f"truncated {label}")
        remaining -= len(chunk)


def _data_uri_size(uri: str, field: str) -> int:
    if len(uri) > MAX_DATA_URI_SIZE:
        _fail(f"{field} data URI exceeds the {MAX_DATA_URI_SIZE}-byte limit")
    comma = uri.find(",")
    if comma < 0:
        _fail(f"{field} contains an invalid data URI")
    metadata = uri[5:comma]
    payload = uri[comma + 1 :]
    try:
        if re.search(r"(?:^|;)base64(?:;|$)", metadata, flags=re.IGNORECASE):
            decoded = base64.b64decode(payload, validate=True)
        else:
            decoded = unquote_to_bytes(payload)
    except (ValueError, base64.binascii.Error):
        _fail(f"{field} contains an invalid data URI payload")
    if len(decoded) > MAX_DATA_URI_SIZE:
        _fail(f"{field} decoded data URI exceeds the {MAX_DATA_URI_SIZE}-byte limit")
    return len(decoded)


def _local_resource_path(uri: object, field: str) -> str | None:
    if not isinstance(uri, str) or not uri:
        _fail(f"{field} URI must be a non-empty string")
    if uri.lower().startswith("data:"):
        _data_uri_size(uri, field)
        return None
    if len(uri) > MAX_PATH_LENGTH:
        _fail(f"{field} path exceeds the {MAX_PATH_LENGTH}-character limit")
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", uri) or uri.startswith(("/", "\\")):
        _fail(f"{field} must use a local relative path or embedded data URI")
    if "\\" in uri or "?" in uri or "#" in uri or "\0" in uri:
        _fail(f"{field} contains an unsupported local resource path")
    try:
        decoded = unquote_to_bytes(uri).decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        _fail(f"{field} contains invalid UTF-8 URI escaping")
    if "\\" in decoded or "?" in decoded or "#" in decoded or "\0" in decoded:
        _fail(f"{field} contains an unsupported local resource path")
    if decoded.startswith("/") or any(part == ".." for part in decoded.split("/")):
        _fail(f"{field} escapes the office scene directory")
    parts = [part for part in decoded.split("/") if part not in ("", ".")]
    if not parts or re.fullmatch(r"[A-Za-z]:", parts[0]):
        _fail(f"{field} does not identify a local office resource")
    return "/".join(parts)


def _required_resources(document: object, binary_chunk_size: int | None) -> dict[str, dict[str, object]]:
    if not isinstance(document, dict) or not isinstance(document.get("asset"), dict):
        _fail("runtime GLB JSON is missing its asset object")
    if document["asset"].get("version") != "2.0":
        _fail("only a glTF 2.0 runtime scene is supported")

    buffers = document.get("buffers", [])
    images = document.get("images", [])
    buffer_views = document.get("bufferViews", [])
    if not isinstance(buffers, list) or not isinstance(images, list) or not isinstance(buffer_views, list):
        _fail("runtime GLB buffers, images, and bufferViews must be arrays")
    if len(buffers) + len(images) + len(buffer_views) > MAX_GLTF_RESOURCE_COUNT:
        _fail(f"runtime GLB exceeds the {MAX_GLTF_RESOURCE_COUNT}-resource limit")

    resources: dict[str, dict[str, object]] = {}

    def add_resource(uri: object, field: str, minimum_size: int = 0) -> None:
        relative_path = _local_resource_path(uri, field)
        if relative_path is None:
            return
        existing = resources.get(relative_path)
        if existing is None:
            resources[relative_path] = {"minimum_size": minimum_size, "kinds": [field.split("[", 1)[0]]}
        else:
            existing["minimum_size"] = max(int(existing["minimum_size"]), minimum_size)
            kinds = existing["kinds"]
            assert isinstance(kinds, list)
            kind = field.split("[", 1)[0]
            if kind not in kinds:
                kinds.append(kind)

    embedded_buffer_seen = False
    for index, buffer in enumerate(buffers):
        if not isinstance(buffer, dict):
            _fail(f"buffers[{index}] must be an object")
        byte_length = buffer.get("byteLength")
        if isinstance(byte_length, bool) or not isinstance(byte_length, int) or byte_length < 0 or byte_length > MAX_MEMBER_SIZE:
            _fail(f"buffers[{index}].byteLength is outside the supported size range")
        uri = buffer.get("uri")
        if uri is None:
            if index != 0 or embedded_buffer_seen or binary_chunk_size is None:
                _fail(f"buffers[{index}] has no URI or valid GLB binary chunk")
            if binary_chunk_size < byte_length or binary_chunk_size - byte_length > 3:
                _fail("runtime GLB binary chunk does not match its declared buffer length")
            embedded_buffer_seen = True
        elif isinstance(uri, str) and uri.lower().startswith("data:"):
            if _data_uri_size(uri, f"buffers[{index}]") < byte_length:
                _fail(f"buffers[{index}] data URI is shorter than its declared byteLength")
        else:
            add_resource(uri, f"buffers[{index}]", byte_length)

    for index, image in enumerate(images):
        if not isinstance(image, dict):
            _fail(f"images[{index}] must be an object")
        has_uri = image.get("uri") is not None
        has_view = image.get("bufferView") is not None
        if has_uri == has_view:
            _fail(f"images[{index}] must have exactly one of uri or bufferView")
        if has_uri:
            add_resource(image["uri"], f"images[{index}]")
        else:
            view_index = image.get("bufferView")
            if isinstance(view_index, bool) or not isinstance(view_index, int) or not 0 <= view_index < len(buffer_views):
                _fail(f"images[{index}] references a missing bufferView")
            if not isinstance(image.get("mimeType"), str) or not image["mimeType"]:
                _fail(f"images[{index}] embedded in a bufferView needs a mimeType")

    return resources


def _read_runtime_glb(stream: BinaryIO, member_size: int) -> tuple[object, int]:
    if member_size < 20 or member_size > MAX_SELECTED_OUTPUT_SIZE:
        _fail("runtime GLB size is outside the supported range")
    header = _read_exact(stream, 12, "GLB header")
    magic, version, declared_size = struct.unpack("<III", header)
    if magic != GLB_MAGIC:
        _fail("selected runtime asset does not have a GLB header")
    if version != 2:
        _fail("selected runtime asset must use GLB version 2")
    if declared_size != member_size:
        _fail("GLB declared length does not match its archive member size")

    cursor = 12
    json_document: object | None = None
    binary_chunk_size: int | None = None
    chunk_index = 0
    while cursor < declared_size:
        if cursor + 8 > declared_size:
            _fail("GLB contains a truncated chunk header")
        chunk_header = _read_exact(stream, 8, "GLB chunk header")
        chunk_length, chunk_type = struct.unpack("<II", chunk_header)
        cursor += 8
        if chunk_length % 4 or cursor + chunk_length > declared_size:
            _fail("GLB contains an invalid chunk length")
        if chunk_index == 0 and chunk_type != GLB_JSON_CHUNK:
            _fail("GLB JSON chunk must appear first")
        if chunk_type == GLB_JSON_CHUNK:
            if json_document is not None or chunk_index != 0:
                _fail("GLB JSON chunk is duplicated or misplaced")
            if chunk_length > MAX_GLTF_JSON_SIZE:
                _fail(f"GLB JSON chunk exceeds the {MAX_GLTF_JSON_SIZE}-byte limit")
            json_bytes = _read_exact(stream, chunk_length, "GLB JSON chunk")
            try:
                json_document = json.loads(json_bytes.rstrip(b" \0").decode("utf-8-sig"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                _fail(f"GLB JSON chunk is invalid: {error}")
        elif chunk_type == GLB_BINARY_CHUNK:
            if binary_chunk_size is not None or json_document is None:
                _fail("GLB binary chunk is misplaced or duplicated")
            binary_chunk_size = chunk_length
            _discard_exact(stream, chunk_length, "GLB binary chunk")
        else:
            if json_document is None:
                _fail("GLB JSON chunk must appear first")
            _discard_exact(stream, chunk_length, "GLB chunk")
        cursor += chunk_length
        chunk_index += 1

    if cursor != declared_size or json_document is None:
        _fail("GLB is missing its JSON chunk or has inconsistent length")
    resources = _required_resources(json_document, binary_chunk_size)
    return resources, member_size


def _record_archive(snapshot: BinaryIO) -> tuple[dict[str, dict[str, object]], str, dict[str, dict[str, object]]]:
    entries: dict[str, dict[str, object]] = {}
    selected_glb: str | None = None
    required_resources: dict[str, dict[str, object]] | None = None
    entry_count = 0
    total_regular_size = 0
    snapshot.seek(0)
    try:
        decoded_stream = lzma.LZMAFile(snapshot, mode="rb")
        capped_stream = _CappedReader(decoded_stream, MAX_TAR_STREAM_SIZE)
        try:
            archive_context = tarfile.open(fileobj=capped_stream, mode="r|")
        except Exception:
            decoded_stream.close()
            raise
        with archive_context as archive:
            for member in archive:
                entry_count += 1
                if entry_count > MAX_MEMBER_COUNT:
                    _fail(f"archive exceeds the {MAX_MEMBER_COUNT}-member limit")
                is_directory = member.isdir()
                normalized = _normalized_member_name(member.name, is_directory)
                if normalized in entries:
                    _fail(f"archive contains a duplicate member path: {normalized!r}")
                if is_directory:
                    if member.size != 0:
                        _fail(f"archive directory has a nonzero size: {member.name!r}")
                    entries[normalized] = {"size": 0, "directory": True, "source_name": member.name}
                    continue
                if not member.isreg():
                    _fail(f"archive contains a link or unsupported special entry: {member.name!r}")
                if member.size < 0 or member.size > MAX_MEMBER_SIZE:
                    _fail(f"archive member exceeds the {MAX_MEMBER_SIZE}-byte limit: {member.name!r}")
                total_regular_size += member.size
                if total_regular_size > MAX_TOTAL_UNCOMPRESSED_SIZE:
                    _fail(f"archive exceeds the {MAX_TOTAL_UNCOMPRESSED_SIZE}-byte uncompressed member limit")
                entries[normalized] = {"size": member.size, "directory": False, "source_name": member.name}

                parts = normalized.split("/")
                if len(parts) >= 2 and parts[-2:] == ["scene", RUNTIME_GLB_NAME]:
                    if selected_glb is not None:
                        _fail("archive contains more than one candidate runtime office GLB")
                    selected_glb = normalized
                    source = archive.extractfile(member)
                    if source is None:
                        _fail("cannot read the selected runtime GLB from the archive")
                    with source:
                        required_resources, _ = _read_runtime_glb(source, member.size)
    except InstallError:
        raise
    except (tarfile.TarError, lzma.LZMAError, EOFError, OSError) as error:
        _fail(f"archive cannot be safely parsed: {error}")
    finally:
        if "decoded_stream" in locals():
            decoded_stream.close()

    if selected_glb is None or required_resources is None:
        _fail(f"archive is missing scene/{RUNTIME_GLB_NAME}")

    for name, entry in entries.items():
        parts = PurePosixPath(name).parts
        for index in range(1, len(parts)):
            ancestor = "/".join(parts[:index])
            parent = entries.get(ancestor)
            if parent is not None and not parent["directory"]:
                _fail(f"archive member is nested under a non-directory path: {name!r}")

    selected: dict[str, dict[str, object]] = {
        selected_glb: {
            "output_path": OUTPUT_GLB_NAME,
            "kind": "runtime-glb",
            "size": int(entries[selected_glb]["size"]),
        }
    }
    selected_output_total = int(entries[selected_glb]["size"])
    scene_directory = PurePosixPath(selected_glb).parent
    for relative_path, requirements in required_resources.items():
        source_name = (scene_directory / PurePosixPath(relative_path)).as_posix()
        source_entry = entries.get(source_name)
        if source_entry is None or source_entry["directory"]:
            _fail(f"runtime GLB references a missing local asset: {relative_path}")
        if int(source_entry["size"]) < int(requirements["minimum_size"]):
            _fail(f"local GLB buffer is shorter than its declared byteLength: {relative_path}")
        selected_output_total += int(source_entry["size"])
        if selected_output_total > MAX_SELECTED_OUTPUT_SIZE:
            _fail(f"selected office assets exceed the {MAX_SELECTED_OUTPUT_SIZE}-byte output limit")
        if source_name in selected:
            prior_path = selected[source_name]["output_path"]
            if prior_path != relative_path:
                _fail(f"multiple scene resources resolve to conflicting output paths: {relative_path}")
        output_path = relative_path
        if output_path == OUTPUT_GLB_NAME:
            _fail("a referenced local resource conflicts with the office.glb output path")
        selected[source_name] = {
            "output_path": output_path,
            "kind": "local-resource",
            "size": int(source_entry["size"]),
            "minimum_size": int(requirements["minimum_size"]),
            "resource_kinds": requirements["kinds"],
        }

    return entries, selected_glb, selected


def _copy_member(stream: BinaryIO, destination: Path, expected_size: int) -> str:
    digest = hashlib.sha256()
    total = 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as output:
        while True:
            chunk = stream.read(COPY_CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
            if total > expected_size or total > MAX_MEMBER_SIZE:
                _fail(f"archive member expanded beyond its declared size: {destination.name}")
            digest.update(chunk)
            output.write(chunk)
        output.flush()
        os.fsync(output.fileno())
    if total != expected_size:
        destination.unlink(missing_ok=True)
        _fail(f"archive member size changed during extraction: {destination.name}")
    return digest.hexdigest()


def _extract_selected(snapshot: BinaryIO, entries: dict[str, dict[str, object]], selected: dict[str, dict[str, object]], stage_directory: Path) -> dict[str, dict[str, object]]:
    wanted = set(selected)
    extracted: dict[str, dict[str, object]] = {}
    snapshot.seek(0)
    try:
        decoded_stream = lzma.LZMAFile(snapshot, mode="rb")
        capped_stream = _CappedReader(decoded_stream, MAX_TAR_STREAM_SIZE)
        with tarfile.open(fileobj=capped_stream, mode="r|") as archive:
            for member in archive:
                normalized = _normalized_member_name(member.name, member.isdir())
                if normalized not in wanted:
                    continue
                entry = entries.get(normalized)
                if entry is None or member.isdir() or not member.isreg():
                    _fail(f"selected asset changed type during extraction: {normalized}")
                expected_size = int(entry["size"])
                if member.size != expected_size:
                    _fail(f"selected asset changed size during extraction: {normalized}")
                source = archive.extractfile(member)
                if source is None:
                    _fail(f"cannot read selected archive member: {normalized}")
                output_path = str(selected[normalized]["output_path"])
                target = stage_directory.joinpath(*PurePosixPath(output_path).parts)
                with source:
                    content_hash = _copy_member(source, target, expected_size)
                extracted[normalized] = {
                    "output_path": output_path,
                    "size": expected_size,
                    "sha256": content_hash,
                }
    except InstallError:
        raise
    except (tarfile.TarError, lzma.LZMAError, EOFError, OSError) as error:
        _fail(f"archive extraction failed: {error}")
    finally:
        if "decoded_stream" in locals():
            decoded_stream.close()

    missing = wanted - set(extracted)
    if missing:
        _fail(f"selected archive members disappeared during extraction: {', '.join(sorted(missing))}")
    return extracted


def _target_path(destination_directory: Path, relative_path: str) -> Path:
    parts = PurePosixPath(relative_path).parts
    if not parts or any(part in (".", "..") for part in parts) or PurePosixPath(relative_path).is_absolute():
        _fail(f"unsafe office output path: {relative_path!r}")
    target = destination_directory.joinpath(*parts)
    try:
        target.relative_to(destination_directory)
    except ValueError:
        _fail(f"office output path escapes its destination: {relative_path!r}")
    return target


def _existing_file_matches(path: Path, expected_size: int, expected_hash: str) -> bool:
    if not path.exists() and not path.is_symlink():
        return False
    info = _regular_file(path, f"existing output {path.name}")
    if info.st_size != expected_size:
        return False
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(COPY_CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest() == expected_hash


def _commit_outputs(stage_directory: Path, destination_directory: Path, outputs: dict[str, dict[str, object]]) -> None:
    parent = destination_directory.parent
    current = parent
    while True:
        if current.is_symlink():
            _fail(f"office output path contains a symlink: {current}")
        if current.parent == current:
            break
        current = current.parent
    parent.mkdir(parents=True, exist_ok=True)
    if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
        _fail("office output parent must be a real directory")
    if destination_directory.exists() or destination_directory.is_symlink():
        _directory(destination_directory, "office output directory")
    else:
        destination_directory.mkdir()

    planned: list[tuple[Path, Path, int, str]] = []
    for relative_path, metadata in outputs.items():
        staged_file = _target_path(stage_directory, relative_path)
        final_file = _target_path(destination_directory, relative_path)
        expected_size = int(metadata["size"])
        expected_hash = str(metadata["sha256"])
        if final_file.exists() or final_file.is_symlink():
            if not _existing_file_matches(final_file, expected_size, expected_hash):
                _fail(f"refusing to overwrite a different existing office asset: {final_file}")
            continue
        current = final_file.parent
        chain: list[Path] = []
        while current != destination_directory:
            chain.append(current)
            current = current.parent
        for directory in reversed(chain):
            if directory.exists() or directory.is_symlink():
                if directory.is_symlink() or not directory.is_dir():
                    _fail(f"office output path crosses a non-directory entry: {directory}")
            else:
                directory.mkdir()
        planned.append((staged_file, final_file, expected_size, expected_hash))

    created_files: list[Path] = []
    temporary_files: list[Path] = []
    try:
        for staged_file, final_file, expected_size, expected_hash in planned:
            temp_path = final_file.with_name(f".{final_file.name}.install-{os.getpid()}-{len(temporary_files)}")
            if temp_path.exists() or temp_path.is_symlink():
                _fail(f"temporary office output already exists: {temp_path.name}")
            temporary_files.append(temp_path)
            with staged_file.open("rb") as source, temp_path.open("xb") as target:
                shutil.copyfileobj(source, target, length=COPY_CHUNK_SIZE)
                target.flush()
                os.fsync(target.fileno())
            if not _existing_file_matches(temp_path, expected_size, expected_hash):
                _fail(f"staged office output failed verification: {final_file.name}")
            os.link(temp_path, final_file, follow_symlinks=False)
            created_files.append(final_file)
            temp_path.unlink()
            temporary_files.remove(temp_path)
    except Exception:
        for temp_path in temporary_files:
            temp_path.unlink(missing_ok=True)
        for created_file in created_files:
            created_file.unlink(missing_ok=True)
        raise


def _install_snapshot(snapshot: BinaryIO, archive_sha256: str, archive_size: int, destination_directory: Path) -> dict[str, object]:
    entries, source_glb, selected = _record_archive(snapshot)
    with tempfile.TemporaryDirectory(prefix="sidequest-office-stage-") as temporary_directory:
        stage_directory = Path(temporary_directory)
        extracted = _extract_selected(snapshot, entries, selected, stage_directory)
        installed_assets = []
        for source_name, metadata in selected.items():
            extracted_metadata = extracted[source_name]
            if metadata["kind"] == "local-resource":
                installed_assets.append({
                    "source_member": source_name,
                    "path": metadata["output_path"],
                    "size_bytes": extracted_metadata["size"],
                    "sha256": extracted_metadata["sha256"],
                    "resource_kinds": metadata["resource_kinds"],
                })

        glb_metadata = extracted[source_glb]
        provenance: dict[str, object] = {
            "asset_kit": "Sidequest Complete Art Kit 2026-10-07",
            "verified_archive_size_bytes": archive_size,
            "verified_archive_sha256": archive_sha256,
            "source_glb_member": source_glb,
            "installed_glb": OUTPUT_GLB_NAME,
            "installed_glb_size_bytes": glb_metadata["size"],
            "installed_glb_sha256": glb_metadata["sha256"],
            "installed_local_resources": installed_assets,
        }
        provenance_path = stage_directory / "provenance.json"
        provenance_bytes = (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8")
        provenance_path.write_bytes(provenance_bytes)
        provenance_hash = hashlib.sha256(provenance_bytes).hexdigest()

        outputs: dict[str, dict[str, object]] = {
            str(metadata["output_path"]): {
                "size": int(extracted[source_name]["size"]),
                "sha256": str(extracted[source_name]["sha256"]),
            }
            for source_name, metadata in selected.items()
        }
        outputs["provenance.json"] = {"size": len(provenance_bytes), "sha256": provenance_hash}
        _commit_outputs(stage_directory, destination_directory, outputs)
        return provenance


def install_office_archive(
    archive_path: str | os.PathLike[str],
    destination_directory: str | os.PathLike[str],
    *,
    expected_size: int = EXPECTED_ARCHIVE_SIZE,
    expected_sha256: str = EXPECTED_ARCHIVE_SHA256,
) -> dict[str, object]:
    """Install from one archive. Expected values are injectable for offline synthetic tests."""
    snapshot, archive_sha256, archive_size = _snapshot_from_file(
        Path(archive_path), expected_size, expected_sha256
    )
    try:
        return _install_snapshot(snapshot, archive_sha256, archive_size, Path(destination_directory))
    finally:
        snapshot.close()


def install_office_from_parts(
    parts_directory: str | os.PathLike[str],
    destination_directory: str | os.PathLike[str],
    *,
    expected_size: int = EXPECTED_ARCHIVE_SIZE,
    expected_sha256: str = EXPECTED_ARCHIVE_SHA256,
) -> dict[str, object]:
    """Concatenate the eight exact kit parts, then validate and install the snapshot."""
    snapshot, archive_sha256, archive_size = _snapshot_from_parts(
        Path(parts_directory), expected_size, expected_sha256
    )
    try:
        return _install_snapshot(snapshot, archive_sha256, archive_size, Path(destination_directory))
    finally:
        snapshot.close()


def _default_destination() -> Path:
    return Path(__file__).resolve().parents[1] / "public" / "office"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Install the verified Sidequest office GLB and only its referenced local resources."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--archive", type=Path, help="path to the complete .tar.xz archive")
    source.add_argument("--parts-directory", type=Path, help="directory containing the eight named .part files")
    args = parser.parse_args(argv)

    try:
        if args.archive is not None:
            provenance = install_office_archive(args.archive, _default_destination())
        else:
            provenance = install_office_from_parts(args.parts_directory, _default_destination())
    except (InstallError, OSError, tarfile.TarError, lzma.LZMAError) as error:
        print(f"office asset installation failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps({
        "installed": str(_default_destination() / OUTPUT_GLB_NAME),
        "archive_sha256": provenance["verified_archive_sha256"],
        "glb_sha256": provenance["installed_glb_sha256"],
        "local_resource_count": len(provenance["installed_local_resources"]),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
