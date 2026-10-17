"""Copy the supplied rigged humans, fit caps, identity caps and attachment data."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys

source = Path(sys.argv[1])
root = Path(__file__).resolve().parents[3]
office = root / "desktop/public/office"
evidence = root / "evidence/desktop/original-office"
resources = []

def copy(relative, destination):
    src = source / relative
    dst = office / destination
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    assert hashlib.sha256(dst.read_bytes()).hexdigest() == digest
    resources.append({"source_member": "Sidequest_Complete_Art_Kit/" + relative, "path": destination, "size_bytes": dst.stat().st_size, "sha256": digest})
    return "/office/" + destination

def glb_document(relative):
    b = (source / relative).read_bytes()
    assert struct.unpack_from("<III", b) == (0x46546C67, 2, len(b))
    return json.loads(b[20:20 + struct.unpack_from("<I", b, 12)[0]])

workers = []
for file in sorted((source / "characters/game").glob("SQ_HUMAN*.glb")):
    relative = file.relative_to(source).as_posix()
    doc = glb_document(relative)
    clips = [{"name": a["name"], "durationSeconds": max(doc["accessors"][s["input"]]["max"][0] for s in a["samplers"])} for a in doc["animations"]]
    assert {c["name"] for c in clips} == {"Idle", "Typing", "Walk", "Point"}
    assert len(doc["skins"]) == 1 and len(doc["skins"][0]["joints"]) == 17
    workers.append({"assetId": file.stem, "url": copy(relative, "actors/" + file.name), "jointCount": 17, "clips": clips, "capReady": file.stem.endswith("__CAP_READY")})
caps = []
for file in sorted((source / "providers/glb").glob("SQ_CAP*.glb")):
    relative = file.relative_to(source).as_posix()
    doc = glb_document(relative)
    caps.append({"assetId": file.stem, "url": copy(relative, "caps/" + file.name), "jointCount": len(doc.get("skins", [{}])[0].get("joints", [])), "materials": [m.get("name") for m in doc.get("materials", [])]})
identities = []
for file in sorted((source / "providers/textures").glob("*_cap_RGBA.png")):
    identities.append({"assetId": file.stem, "url": copy(file.relative_to(source).as_posix(), "caps/textures/" + file.name)})
profile_url = copy("providers/attachment_profiles.json", "caps/attachment-profiles.json")
layout = json.loads((source / "manifests/world_layout.json").read_text())
instances = []
for actor in layout["staged_actors"]:
    reconstruction = actor["reconstruction"]
    accessory = reconstruction.get("head_accessory")
    if accessory:
        accessory["fitBaseUrl"] = "/office/caps/" + Path(accessory["fit_base_glb"]).name
        accessory["identityTextureUrl"] = "/office/caps/textures/" + Path(accessory["identity_rgba"]).name
        accessory["attachmentProfilesUrl"] = profile_url
    instances.append({"sceneId": actor["id"], "stationId": actor.get("parent_id"), "assetUrl": "/office/actors/" + Path(reconstruction["actor_glb"]).name, "worldMatrixGltfRows": reconstruction["actor_instance_world_matrix_gltf_rows"], "poseHint": actor.get("pose_hint"), "clipHint": reconstruction.get("clip_hint"), "headAccessory": accessory, "runtimeConnected": False})
manifest = {"schema": "sidequest-original-actors-v1", "units": "metres", "axes": "glTF Y-up; original transforms already converted", "workers": workers, "caps": caps, "identityTextures": identities, "attachmentProfilesUrl": profile_url, "stagedReferenceInstances": instances, "renderPolicy": "The static office.glb excludes staged actors. Spawn from these unchanged original assets using a shared original skeleton and source transforms. Authored scene IDs and pose hints are visual references, not backend worker ownership or live job status."}
(office / "actors.json").write_text(json.dumps(manifest, indent=2) + "\n")
provenance = json.loads((office / "provenance.json").read_text())
lossless = json.loads((evidence / "lossless-resource-verification.json").read_text())
provenance["original_runtime_glb_sha256"] = lossless["sourceSha256"]
provenance["original_runtime_glb_size_bytes"] = lossless["sourceBytes"]
provenance["installed_glb_sha256"] = lossless["installedSha256"]
provenance["installed_glb_size_bytes"] = lossless["installedBytes"]
provenance["runtime_resource_relocation"] = "Original image bytes relocated from GLB bufferViews to local texture files; original geometry payloads, nodes, meshes, materials and texture indices unchanged."
provenance["installed_local_resources"] = lossless["resources"]
provenance["additional_original_resources"] = resources
provenance["source_drive_folder"] = "https://drive.google.com/drive/folders/1J69rRCIT03-AFo9A0WqwEc7CQswM4rlY"
(office / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
(evidence / "actor-import-verification.json").write_text(json.dumps({"unchangedSourceCopies": True, "humanVariants": len(workers), "capAssets": len(caps), "clipsPerHuman": 4, "jointsPerHuman": 17, "resources": resources}, indent=2) + "\n")
print("Imported", len(workers), "unchanged rigged humans and", len(caps), "unchanged caps")
