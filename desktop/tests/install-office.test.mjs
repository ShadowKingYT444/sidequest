import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const PYTHON = process.env.PYTHON ?? "python3";
const INSTALLER_PATH = fileURLToPath(new URL("../scripts/install-office.py", import.meta.url));
const PART_STEM = "Sidequest_Complete_Art_Kit_2026-10-07.tar.xz.part";
const RUNTIME_GLB = "Sidequest_Runtime_Environment_Batched.glb";

const TAR_BUILDER = String.raw`
import base64, json, sys, tarfile
archive_path = sys.argv[1]
members = json.loads(sys.argv[2])
with tarfile.open(archive_path, mode="w:xz", preset=0) as archive:
    for member in members:
        info = tarfile.TarInfo(member["name"])
        kind = member.get("kind", "file")
        if kind == "symlink":
            info.type = tarfile.SYMTYPE
            info.linkname = member.get("linkname", "target")
            info.size = 0
            archive.addfile(info)
        elif kind == "hardlink":
            info.type = tarfile.LNKTYPE
            info.linkname = member.get("linkname", "target")
            info.size = 0
            archive.addfile(info)
        elif kind == "fifo":
            info.type = tarfile.FIFOTYPE
            info.size = 0
            archive.addfile(info)
        else:
            data = base64.b64decode(member["data"])
            info.size = len(data)
            archive.addfile(info, __import__("io").BytesIO(data))
`;

const INSTALL_DRIVER = String.raw`
import importlib.util, json, sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("install_office", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
archive_path, destination, expected_size, expected_sha = sys.argv[2:6]
mode = sys.argv[6] if len(sys.argv) > 6 else "archive"
try:
    if mode == "parts":
        result = module.install_office_from_parts(parts_directory=archive_path, destination_directory=destination, expected_size=int(expected_size), expected_sha256=expected_sha)
    else:
        result = module.install_office_archive(archive_path=archive_path, destination_directory=destination, expected_size=int(expected_size), expected_sha256=expected_sha)
    print(json.dumps({"result": result}, sort_keys=True))
except Exception as error:
    print(json.dumps({"error": str(error)}, sort_keys=True))
`;

function makeGlb(document) {
  const json = Buffer.from(JSON.stringify(document), "utf8");
  const jsonLength = Math.ceil(json.byteLength / 4) * 4;
  const jsonChunk = Buffer.alloc(jsonLength, 0x20);
  json.copy(jsonChunk);
  const totalLength = 12 + 8 + jsonChunk.byteLength;
  const output = Buffer.alloc(totalLength);
  output.writeUInt32LE(0x46546c67, 0);
  output.writeUInt32LE(2, 4);
  output.writeUInt32LE(totalLength, 8);
  output.writeUInt32LE(jsonChunk.byteLength, 12);
  output.writeUInt32LE(0x4e4f534a, 16);
  jsonChunk.copy(output, 20);
  return output;
}

function glbWithImageUri(uri) {
  return makeGlb({ asset: { version: "2.0" }, buffers: [], images: [{ uri }] });
}

async function createArchive(archivePath, members) {
  const serialized = JSON.stringify(members.map((member) => ({
    ...member,
    ...(member.data === undefined ? {} : { data: Buffer.from(member.data).toString("base64") }),
  })));
  const result = spawnSync(PYTHON, ["-c", TAR_BUILDER, archivePath, serialized], { encoding: "utf8" });
  assert.equal(result.status, 0, result.stderr);
  return readFile(archivePath);
}

function runInstaller(archivePath, destination, archiveBytes, mode = "archive") {
  const digest = createHash("sha256").update(archiveBytes).digest("hex");
  const result = spawnSync(PYTHON, [
    "-c",
    INSTALL_DRIVER,
    INSTALLER_PATH,
    archivePath,
    destination,
    String(archiveBytes.byteLength),
    digest,
    mode,
  ], { encoding: "utf8" });
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(result.stdout);
}

async function makeTemp(t) {
  const directory = await mkdtemp(path.join(os.tmpdir(), "sidequest-office-installer-"));
  t.after(() => rm(directory, { recursive: true, force: true }));
  return directory;
}

test("installs only the runtime GLB and its referenced local resource with provenance", async (t) => {
  const directory = await makeTemp(t);
  const archivePath = path.join(directory, "kit.tar.xz");
  const destination = path.join(directory, "public", "office");
  const glb = glbWithImageUri("textures/panel.png");
  const image = Buffer.from("synthetic test texture bytes");
  const archiveBytes = await createArchive(archivePath, [
    { name: `kit-prefix/scene/${RUNTIME_GLB}`, data: glb },
    { name: "kit-prefix/scene/textures/panel.png", data: image },
    { name: "kit-prefix/scene/unreferenced.bin", data: Buffer.from("do not install") },
    { name: "kit-prefix/scene/Sidequest_Office_Master.blend", data: Buffer.from("test-only archive marker") },
  ]);

  const outcome = runInstaller(archivePath, destination, archiveBytes);
  assert.equal(outcome.error, undefined);
  const installedGlb = await readFile(path.join(destination, "office.glb"));
  const installedImage = await readFile(path.join(destination, "textures", "panel.png"));
  const provenance = JSON.parse(await readFile(path.join(destination, "provenance.json"), "utf8"));
  assert.deepEqual(installedGlb, glb);
  assert.deepEqual(installedImage, image);
  assert.equal(provenance.source_glb_member, `kit-prefix/scene/${RUNTIME_GLB}`);
  assert.equal(provenance.installed_glb_sha256, createHash("sha256").update(glb).digest("hex"));
  assert.equal(provenance.installed_local_resources.length, 1);
  assert.equal(provenance.installed_local_resources[0].path, "textures/panel.png");
  assert.deepEqual((await readdir(path.join(destination, "textures"))).sort(), ["panel.png"]);
  assert.equal((await readdir(destination)).includes("bindings.json"), false);
  assert.equal((await readdir(destination)).includes("Sidequest_Office_Master.blend"), false);
});

test("the parts route concatenates the exact eight names without changing source parts", async (t) => {
  const directory = await makeTemp(t);
  const archivePath = path.join(directory, "kit.tar.xz");
  const partsDirectory = path.join(directory, "parts");
  const destination = path.join(directory, "office");
  const archiveBytes = await createArchive(archivePath, [
    { name: `scene/${RUNTIME_GLB}`, data: glbWithImageUri("textures/wood.png") },
    { name: "scene/textures/wood.png", data: Buffer.from("synthetic wood texture") },
  ]);
  await mkdir(partsDirectory);
  const expectedParts = [];
  for (let index = 0; index < 8; index += 1) {
    const start = Math.floor((archiveBytes.byteLength * index) / 8);
    const end = Math.floor((archiveBytes.byteLength * (index + 1)) / 8);
    const part = archiveBytes.subarray(start, end);
    expectedParts.push(Buffer.from(part));
    await writeFile(path.join(partsDirectory, `${PART_STEM}${String(index + 1).padStart(2, "0")}`), part);
  }

  const outcome = runInstaller(partsDirectory, destination, archiveBytes, "parts");
  assert.equal(outcome.error, undefined);
  assert.deepEqual(await readFile(path.join(destination, "textures", "wood.png")), Buffer.from("synthetic wood texture"));
  const actualParts = await Promise.all(Array.from({ length: 8 }, (_, index) =>
    readFile(path.join(partsDirectory, `${PART_STEM}${String(index + 1).padStart(2, "0")}`))));
  assert.deepEqual(actualParts, expectedParts);
});

test("rejects traversal, links, remote resources, and a mismatched archive hash before writing outputs", async (t) => {
  const directory = await makeTemp(t);
  const destination = path.join(directory, "office");

  const traversalArchivePath = path.join(directory, "traversal.tar.xz");
  const traversalBytes = await createArchive(traversalArchivePath, [
    { name: `scene/${RUNTIME_GLB}`, data: glbWithImageUri("textures/panel.png") },
    { name: "scene/textures/panel.png", data: Buffer.from("test") },
    { name: "../escaped.txt", data: Buffer.from("test") },
  ]);
  assert.match(runInstaller(traversalArchivePath, destination, traversalBytes).error, /path traversal rejected/);
  assert.equal(await readdir(directory).then((entries) => entries.includes("office")), false);

  const linkArchivePath = path.join(directory, "link.tar.xz");
  const linkBytes = await createArchive(linkArchivePath, [
    { name: `scene/${RUNTIME_GLB}`, data: glbWithImageUri("textures/panel.png") },
    { name: "scene/textures/panel.png", kind: "symlink", linkname: "../../outside" },
  ]);
  assert.match(runInstaller(linkArchivePath, destination, linkBytes).error, /link or unsupported special entry/);

  for (const [filename, kind] of [["hardlink.tar.xz", "hardlink"], ["fifo.tar.xz", "fifo"]]) {
    const specialArchivePath = path.join(directory, filename);
    const specialBytes = await createArchive(specialArchivePath, [
      { name: `scene/${RUNTIME_GLB}`, data: glbWithImageUri("textures/panel.png") },
      { name: "scene/textures/panel.png", kind, linkname: "scene/other.png" },
    ]);
    assert.match(runInstaller(specialArchivePath, destination, specialBytes).error, /link or unsupported special entry/);
  }

  const absoluteArchivePath = path.join(directory, "absolute.tar.xz");
  const absoluteBytes = await createArchive(absoluteArchivePath, [
    { name: `scene/${RUNTIME_GLB}`, data: glbWithImageUri("textures/panel.png") },
    { name: "/tmp/escaped.txt", data: Buffer.from("test") },
  ]);
  assert.match(runInstaller(absoluteArchivePath, destination, absoluteBytes).error, /absolute or unsupported path/);

  const resourceTraversalPath = path.join(directory, "resource-traversal.tar.xz");
  const resourceTraversalBytes = await createArchive(resourceTraversalPath, [
    { name: `scene/${RUNTIME_GLB}`, data: glbWithImageUri("textures/../../outside.png") },
  ]);
  assert.match(runInstaller(resourceTraversalPath, destination, resourceTraversalBytes).error, /escapes the office scene directory/);

  const remoteArchivePath = path.join(directory, "remote.tar.xz");
  const remoteBytes = await createArchive(remoteArchivePath, [
    { name: `scene/${RUNTIME_GLB}`, data: glbWithImageUri("https://example.invalid/panel.png") },
  ]);
  assert.match(runInstaller(remoteArchivePath, destination, remoteBytes).error, /local relative path or embedded data URI/);

  const hashDriver = String.raw`
import importlib.util, json, sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("install_office", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
try:
    module.install_office_archive(sys.argv[2], sys.argv[3], expected_size=len(open(sys.argv[2], "rb").read()), expected_sha256="0" * 64)
except Exception as error:
    print(str(error))
`;
  const badHash = spawnSync(PYTHON, ["-c", hashDriver, INSTALLER_PATH, remoteArchivePath, destination], { encoding: "utf8" });
  assert.equal(badHash.status, 0, badHash.stderr);
  assert.match(badHash.stdout, /SHA-256 mismatch/);
  assert.equal(await readdir(directory).then((entries) => entries.includes("office")), false);
});

test("production CLI does not accept a test hash override", async (t) => {
  const directory = await makeTemp(t);
  const archivePath = path.join(directory, "synthetic.tar.xz");
  const archiveBytes = await createArchive(archivePath, [
    { name: `scene/${RUNTIME_GLB}`, data: glbWithImageUri("data:image/png;base64,AQID") },
  ]);
  const result = spawnSync(PYTHON, [INSTALLER_PATH, "--archive", archivePath], { encoding: "utf8" });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /archive size mismatch/);
  assert.ok(archiveBytes.byteLength < 535_951_540);
});
