"""Losslessly relocate original GLB image payloads to local office resources."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
parser.add_argument("destination", type=Path)
parser.add_argument("report", type=Path)
args = parser.parse_args()
original = args.source.read_bytes()
assert hashlib.sha256(original).hexdigest() == "54525622984606b8ca0e54cc53019da780863ee94b6d4183ad200aa75e196bae"
assert struct.unpack_from("<III", original) == (0x46546C67, 2, len(original))
json_size, json_type = struct.unpack_from("<II", original, 12)
assert json_type == 0x4E4F534A
source = json.loads(original[20:20 + json_size])
document = copy.deepcopy(source)
bin_size, bin_type = struct.unpack_from("<II", original, 20 + json_size)
assert bin_type == 0x004E4942
binary = original[28 + json_size:28 + json_size + bin_size]
image_views = {image["bufferView"] for image in source["images"]}
assert all(accessor.get("bufferView") not in image_views for accessor in source["accessors"])
assert not source.get("extensionsRequired")
args.destination.parent.mkdir(parents=True, exist_ok=True)
resources = []
for index, image in enumerate(document["images"]):
    view = source["bufferViews"][image.pop("bufferView")]
    offset = view.get("byteOffset", 0)
    payload = binary[offset:offset + view["byteLength"]]
    suffix = {"image/png": "png", "image/jpeg": "jpg"}[image["mimeType"]]
    digest = hashlib.sha256(payload).hexdigest()
    relative = f"textures/{index:03d}-{digest[:12]}.{suffix}"
    path = args.destination.parent / relative
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(payload)
    image["uri"] = relative
    resources.append({"path": relative, "size_bytes": len(payload), "sha256": digest, "source_image_index": index, "source_buffer_view": source["images"][index]["bufferView"]})
mapping = {}
views = []
new_binary = bytearray()
for index, view in enumerate(source["bufferViews"]):
    if index in image_views:
        continue
    mapping[index] = len(views)
    new_binary.extend(b"\0" * ((-len(new_binary)) % 4))
    updated = copy.deepcopy(view)
    offset = view.get("byteOffset", 0)
    payload = binary[offset:offset + view["byteLength"]]
    updated["byteOffset"] = len(new_binary)
    new_binary.extend(payload)
    views.append(updated)
    assert new_binary[updated["byteOffset"]:updated["byteOffset"] + updated["byteLength"]] == payload
document["bufferViews"] = views
for accessor in document["accessors"]:
    if "bufferView" in accessor:
        accessor["bufferView"] = mapping[accessor["bufferView"]]
    if "sparse" in accessor:
        for field in ("indices", "values"):
            accessor["sparse"][field]["bufferView"] = mapping[accessor["sparse"][field]["bufferView"]]
document["buffers"][0]["byteLength"] = len(new_binary)
new_binary.extend(b"\0" * ((-len(new_binary)) % 4))
encoded = json.dumps(document, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
encoded += b" " * ((-len(encoded)) % 4)
output = struct.pack("<III", 0x46546C67, 2, 28 + len(encoded) + len(new_binary)) + struct.pack("<II", len(encoded), 0x4E4F534A) + encoded + struct.pack("<II", len(new_binary), 0x004E4942) + new_binary
args.destination.write_bytes(output)
for key in ("nodes", "meshes", "materials", "textures", "samplers", "scenes", "animations"):
    assert source.get(key) == document.get(key)
report = {"sourceSha256": hashlib.sha256(original).hexdigest(), "installedSha256": hashlib.sha256(output).hexdigest(), "sourceBytes": len(original), "installedBytes": len(output), "geometryPayloadsIdentical": True, "imagePayloadsIdentical": True, "nodesMaterialsMeshesUnchanged": True, "resources": resources}
args.report.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "resources"}))
