"""Inspect every archive member before extracting preserved originals outside Git."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile

parser = argparse.ArgumentParser()
parser.add_argument("archive", type=Path)
parser.add_argument("destination", type=Path)
parser.add_argument("report", type=Path)
args = parser.parse_args()
assert args.archive.stat().st_size == 535951540
with args.archive.open("rb") as source:
    assert hashlib.file_digest(source, "sha256").hexdigest() == "f7159fbda50771486d65e1a5bd2a42d265120a422d88a686471a9bbb6fb60a95"
assert not args.destination.exists(), "Choose a fresh destination"
seen = set()
total = 0
entries = []
with tarfile.open(args.archive, "r|xz") as archive:
    for member in archive:
        path = PurePosixPath(member.name)
        assert not path.is_absolute() and ".." not in path.parts
        assert path.parts[0] == "Sidequest_Complete_Art_Kit"
        assert "\\" not in member.name and "\0" not in member.name
        assert member.isdir() or member.isreg(), "No links or special files"
        assert member.name not in seen, "No duplicate paths"
        assert 0 <= member.size <= 2 * 1024**3
        seen.add(member.name)
        total += member.size
        assert total <= 8 * 1024**3 and len(seen) <= 100000
        entries.append({"path": member.name, "bytes": member.size, "directory": member.isdir()})
args.destination.mkdir(parents=True)
with tarfile.open(args.archive, "r|xz") as archive:
    for member in archive:
        target = args.destination.joinpath(*PurePosixPath(member.name).parts)
        if member.isdir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, target.open("xb") as out:
                shutil.copyfileobj(source, out, 1024 * 1024)
            target.chmod(0o600)
args.report.write_text(json.dumps({"allPathsSafe": True, "members": len(entries), "uncompressedBytes": total, "entries": entries}, indent=2) + "\n")
print(json.dumps({"allPathsSafe": True, "members": len(entries), "uncompressedBytes": total}))
