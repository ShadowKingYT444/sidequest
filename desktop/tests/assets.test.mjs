import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { inspectGlbFile, parseGlbBuffer } from "../scripts/inspect-assets.mjs";

function makeGlb(document, binary = Buffer.from([1, 2, 3, 4])) {
  const json = Buffer.from(JSON.stringify(document), "utf8");
  const paddedJsonLength = Math.ceil(json.byteLength / 4) * 4;
  const jsonChunk = Buffer.alloc(paddedJsonLength, 0x20);
  json.copy(jsonChunk);

  const chunks = [
    { type: 0x4e4f534a, contents: jsonChunk },
  ];
  if (binary !== null) {
    const paddedBinaryLength = Math.ceil(binary.byteLength / 4) * 4;
    const binaryChunk = Buffer.alloc(paddedBinaryLength);
    binary.copy(binaryChunk);
    chunks.push({ type: 0x004e4942, contents: binaryChunk });
  }

  const totalLength = 12 + chunks.reduce((total, chunk) => total + 8 + chunk.contents.byteLength, 0);
  const result = Buffer.alloc(totalLength);
  result.writeUInt32LE(0x46546c67, 0);
  result.writeUInt32LE(2, 4);
  result.writeUInt32LE(totalLength, 8);
  let cursor = 12;
  for (const chunk of chunks) {
    result.writeUInt32LE(chunk.contents.byteLength, cursor);
    result.writeUInt32LE(chunk.type, cursor + 4);
    chunk.contents.copy(result, cursor + 8);
    cursor += 8 + chunk.contents.byteLength;
  }
  return result;
}

function syntheticDocument() {
  return {
    asset: { version: "2.0", generator: "asset inspector fixture" },
    scene: 0,
    scenes: [{ nodes: [0] }],
    nodes: [{ mesh: 0, translation: [2, 0, 0] }],
    meshes: [{ name: "Synthetic mesh", primitives: [{ attributes: { POSITION: 0 }, material: 0 }] }],
    accessors: [
      { bufferView: 0, componentType: 5126, count: 3, type: "VEC3", min: [-1, -2, 0], max: [1, 2, 0] },
      { componentType: 5126, count: 2, type: "SCALAR", min: [0], max: [2.25] },
      { componentType: 5126, count: 2, type: "VEC3" },
    ],
    bufferViews: [{ buffer: 0, byteLength: 4 }],
    buffers: [{ byteLength: 4 }],
    images: [{ name: "Embedded synthetic image", bufferView: 0, mimeType: "image/png" }],
    textures: [{ name: "Synthetic texture", source: 0 }],
    materials: [{ name: "Synthetic material", doubleSided: true }],
    animations: [{ name: "Synthetic idle", samplers: [{ input: 1, output: 2 }], channels: [{ sampler: 0 }] }],
  };
}

test("inspects GLB manifest metadata and transformed bounds", async () => {
  const manifest = await parseGlbBuffer(makeGlb(syntheticDocument()));

  assert.equal(manifest.format, "glTF 2.0 binary");
  assert.match(manifest.sha256, /^[0-9a-f]{64}$/);
  assert.deepEqual(manifest.bounds, { min: [1, -2, 0], max: [3, 2, 0], complete: true });
  assert.equal(manifest.vertexCount, 7);
  assert.deepEqual(manifest.meshes[0], { name: "Synthetic mesh", primitiveCount: 1, materialIndexes: [0] });
  assert.equal(manifest.materials[0].name, "Synthetic material");
  assert.equal(manifest.textures[0].sourceImage, 0);
  assert.equal(manifest.animations[0].durationSeconds, 2.25);
  assert.deepEqual(manifest.externalResources, []);
});

test("rejects a GLB that references a remote buffer or image", async () => {
  const document = syntheticDocument();
  document.buffers[0].uri = "https://example.invalid/mesh.bin";

  await assert.rejects(parseGlbBuffer(makeGlb(document)), /local relative path or embedded data URI/);
});

test("allows external resources only from files inside the supplied office folder", async (t) => {
  const directory = await mkdtemp(path.join(os.tmpdir(), "sidequest-assets-"));
  t.after(() => rm(directory, { recursive: true, force: true }));
  await mkdir(path.join(directory, "data"));
  await writeFile(path.join(directory, "data", "mesh.bin"), Buffer.from([1, 2, 3, 4]));

  const document = syntheticDocument();
  document.buffers[0] = { byteLength: 4, uri: "data/mesh.bin" };
  const filePath = path.join(directory, "office.glb");
  await writeFile(filePath, makeGlb(document, null));

  const manifest = await inspectGlbFile(filePath);
  assert.equal(manifest.externalResources.length, 1);
  assert.deepEqual(manifest.externalResources[0], {
    type: "buffer",
    uri: "data/mesh.bin",
    path: "data/mesh.bin",
    byteLength: 4,
  });

  const cli = spawnSync(process.execPath, [
    fileURLToPath(new URL("../scripts/inspect-assets.mjs", import.meta.url)),
    filePath,
  ], { encoding: "utf8" });
  assert.equal(cli.status, 0, cli.stderr);
  assert.equal(JSON.parse(cli.stdout).sha256, manifest.sha256);

  document.buffers[0] = { byteLength: 4, uri: "..%2foutside.bin" };
  await assert.rejects(parseGlbBuffer(makeGlb(document, null), { baseDirectory: directory }), /escapes the local office asset directory/);
});

test("rejects malformed GLB headers and byte lengths", async () => {
  const glb = makeGlb(syntheticDocument());
  const wrongMagic = Buffer.from(glb);
  wrongMagic.writeUInt32LE(0, 0);
  await assert.rejects(parseGlbBuffer(wrongMagic), /GLB magic header/);

  const wrongLength = Buffer.from(glb);
  wrongLength.writeUInt32LE(glb.byteLength + 4, 8);
  await assert.rejects(parseGlbBuffer(wrongLength), /declared length does not match/);
});
