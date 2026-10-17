import { createHash } from "node:crypto";
import { readFile, realpath, stat } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const GLB_MAGIC = 0x46546c67;
const JSON_CHUNK = 0x4e4f534a;
const BIN_CHUNK = 0x004e4942;

function fail(message) {
  throw new Error(message);
}

function isRecord(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function integerAtLeast(value, minimum, field) {
  if (!Number.isInteger(value) || value < minimum) {
    fail(`${field} must be an integer greater than or equal to ${minimum}`);
  }
  return value;
}

function decodeDataUri(uri, field) {
  const comma = uri.indexOf(",");
  if (comma < 0) fail(`${field} is not a valid data URI`);
  const metadata = uri.slice(5, comma);
  const payload = uri.slice(comma + 1);
  try {
    if (/(?:^|;)base64(?:;|$)/i.test(metadata)) {
      if (!/^[A-Za-z0-9+/]*={0,2}$/.test(payload) || payload.length % 4 === 1) {
        fail(`${field} contains invalid base64 data`);
      }
      return Buffer.from(payload, "base64");
    }
    return Buffer.from(decodeURIComponent(payload), "utf8");
  } catch (error) {
    if (error instanceof Error && error.message.startsWith(`${field} `)) throw error;
    fail(`${field} contains an invalid data URI payload`);
  }
}

function resolveLocalUri(uri, field, baseDirectory) {
  if (typeof uri !== "string" || uri.length === 0) fail(`${field} URI must be a non-empty string`);
  if (uri.startsWith("data:")) {
    const bytes = decodeDataUri(uri, field);
    return { embedded: true, byteLength: bytes.byteLength };
  }
  if (/^[a-z][a-z\d+.-]*:/i.test(uri) || uri.startsWith("/") || uri.startsWith("\\")) {
    fail(`${field} must use a local relative path or embedded data URI`);
  }
  if (uri.includes("\\") || uri.includes("?") || uri.includes("#") || uri.includes("\0")) {
    fail(`${field} contains an unsupported local path character`);
  }

  let decoded;
  try {
    decoded = decodeURIComponent(uri);
  } catch {
    fail(`${field} contains invalid URI escaping`);
  }
  if (decoded.includes("\\") || decoded.includes("?") || decoded.includes("#") || decoded.includes("\0")) {
    fail(`${field} contains an unsupported local path character`);
  }
  const normalized = path.posix.normalize(decoded);
  if (normalized === "." || normalized === ".." || normalized.startsWith("../") || path.posix.isAbsolute(normalized)) {
    fail(`${field} escapes the local office asset directory`);
  }

  if (!baseDirectory) {
    return { embedded: false, path: normalized, byteLength: null };
  }

  const absoluteBase = path.resolve(baseDirectory);
  const absoluteFile = path.resolve(absoluteBase, ...normalized.split("/"));
  const relativeFile = path.relative(absoluteBase, absoluteFile);
  if (relativeFile === ".." || relativeFile.startsWith(`..${path.sep}`) || path.isAbsolute(relativeFile)) {
    fail(`${field} escapes the local office asset directory`);
  }

  return realpath(absoluteFile).then(async (realFile) => {
    const realBase = await realpath(absoluteBase);
    const realRelative = path.relative(realBase, realFile);
    if (realRelative === ".." || realRelative.startsWith(`..${path.sep}`) || path.isAbsolute(realRelative)) {
      fail(`${field} resolves outside the local office asset directory`);
    }
    const info = await stat(realFile);
    if (!info.isFile()) fail(`${field} does not resolve to a local file`);
    return { embedded: false, path: normalized, byteLength: info.size };
  });
}

function multiplyMatrices(left, right) {
  const output = new Array(16).fill(0);
  for (let column = 0; column < 4; column += 1) {
    for (let row = 0; row < 4; row += 1) {
      for (let index = 0; index < 4; index += 1) {
        output[column * 4 + row] += left[index * 4 + row] * right[column * 4 + index];
      }
    }
  }
  return output;
}

function nodeMatrix(node, field) {
  if (node.matrix !== undefined) {
    if (!Array.isArray(node.matrix) || node.matrix.length !== 16 || !node.matrix.every(Number.isFinite)) {
      fail(`${field}.matrix must contain 16 finite numbers`);
    }
    return node.matrix;
  }
  const translation = node.translation ?? [0, 0, 0];
  const rotation = node.rotation ?? [0, 0, 0, 1];
  const scale = node.scale ?? [1, 1, 1];
  if (!Array.isArray(translation) || translation.length !== 3 || !translation.every(Number.isFinite)) {
    fail(`${field}.translation must contain 3 finite numbers`);
  }
  if (!Array.isArray(rotation) || rotation.length !== 4 || !rotation.every(Number.isFinite)) {
    fail(`${field}.rotation must contain 4 finite numbers`);
  }
  if (!Array.isArray(scale) || scale.length !== 3 || !scale.every(Number.isFinite)) {
    fail(`${field}.scale must contain 3 finite numbers`);
  }
  const [x, y, z, w] = rotation;
  const [sx, sy, sz] = scale;
  const x2 = x + x;
  const y2 = y + y;
  const z2 = z + z;
  const xx = x * x2;
  const xy = x * y2;
  const xz = x * z2;
  const yy = y * y2;
  const yz = y * z2;
  const zz = z * z2;
  const wx = w * x2;
  const wy = w * y2;
  const wz = w * z2;
  return [
    (1 - (yy + zz)) * sx, (xy + wz) * sx, (xz - wy) * sx, 0,
    (xy - wz) * sy, (1 - (xx + zz)) * sy, (yz + wx) * sy, 0,
    (xz + wy) * sz, (yz - wx) * sz, (1 - (xx + yy)) * sz, 0,
    translation[0], translation[1], translation[2], 1,
  ];
}

function transformPoint(matrix, point) {
  const [x, y, z] = point;
  return [
    matrix[0] * x + matrix[4] * y + matrix[8] * z + matrix[12],
    matrix[1] * x + matrix[5] * y + matrix[9] * z + matrix[13],
    matrix[2] * x + matrix[6] * y + matrix[10] * z + matrix[14],
  ];
}

function summarizeBounds(document) {
  const accessors = document.accessors ?? [];
  const nodes = document.nodes ?? [];
  const meshes = document.meshes ?? [];
  let minimum = [Infinity, Infinity, Infinity];
  let maximum = [-Infinity, -Infinity, -Infinity];
  let complete = true;
  let includedPositions = 0;

  const includeMesh = (meshIndex, worldMatrix) => {
    const mesh = meshes[meshIndex];
    if (!mesh) return;
    for (const [primitiveIndex, primitive] of (mesh.primitives ?? []).entries()) {
      const positionAccessorIndex = primitive.attributes?.POSITION;
      if (!Number.isInteger(positionAccessorIndex)) continue;
      const accessor = accessors[positionAccessorIndex];
      if (!accessor || !Array.isArray(accessor.min) || !Array.isArray(accessor.max) || accessor.min.length !== 3 || accessor.max.length !== 3) {
        complete = false;
        continue;
      }
      if (![...accessor.min, ...accessor.max].every(Number.isFinite)) {
        complete = false;
        continue;
      }
      includedPositions += 1;
      for (let mask = 0; mask < 8; mask += 1) {
        const corner = [
          mask & 1 ? accessor.max[0] : accessor.min[0],
          mask & 2 ? accessor.max[1] : accessor.min[1],
          mask & 4 ? accessor.max[2] : accessor.min[2],
        ];
        const point = transformPoint(worldMatrix, corner);
        for (let axis = 0; axis < 3; axis += 1) {
          minimum[axis] = Math.min(minimum[axis], point[axis]);
          maximum[axis] = Math.max(maximum[axis], point[axis]);
        }
      }
      void primitiveIndex;
    }
  };

  if (nodes.length === 0) {
    meshes.forEach((_, index) => includeMesh(index, identityMatrix()));
  } else {
    const parents = new Set();
    nodes.forEach((node) => (node.children ?? []).forEach((child) => parents.add(child)));
    const roots = document.scenes?.[document.scene ?? 0]?.nodes ?? nodes
      .map((_, index) => index)
      .filter((index) => !parents.has(index));
    const visit = (nodeIndex, parentMatrix, ancestors = new Set()) => {
      if (!Number.isInteger(nodeIndex) || nodeIndex < 0 || nodeIndex >= nodes.length) return;
      if (ancestors.has(nodeIndex)) return;
      const node = nodes[nodeIndex];
      const worldMatrix = multiplyMatrices(parentMatrix, nodeMatrix(node, `nodes[${nodeIndex}]`));
      if (Number.isInteger(node.mesh)) includeMesh(node.mesh, worldMatrix);
      const nextAncestors = new Set(ancestors);
      nextAncestors.add(nodeIndex);
      for (const child of node.children ?? []) visit(child, worldMatrix, nextAncestors);
    };
    for (const root of roots) visit(root, identityMatrix());
  }

  if (includedPositions === 0) return null;
  return { min: minimum, max: maximum, complete };
}

function identityMatrix() {
  return [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
}

function validateDocumentShape(document) {
  if (!isRecord(document) || !isRecord(document.asset) || document.asset.version !== "2.0") {
    fail("GLB JSON must contain an asset.version of 2.0");
  }
  for (const key of ["buffers", "bufferViews", "accessors", "images", "textures", "materials", "meshes", "nodes", "scenes", "animations"]) {
    if (document[key] !== undefined && !Array.isArray(document[key])) fail(`GLB JSON ${key} must be an array`);
  }
  for (const [index, node] of (document.nodes ?? []).entries()) {
    if (!isRecord(node)) fail(`nodes[${index}] must be an object`);
    if (node.mesh !== undefined) integerAtLeast(node.mesh, 0, `nodes[${index}].mesh`);
    if (node.children !== undefined && (!Array.isArray(node.children) || node.children.some((child) => !Number.isInteger(child) || child < 0))) {
      fail(`nodes[${index}].children must contain non-negative integer node indexes`);
    }
  }
}

async function parseResources(document, binaryChunk, baseDirectory) {
  const buffers = document.buffers ?? [];
  const bufferViews = document.bufferViews ?? [];
  const actualLengths = [];
  const externalResources = new Map();

  for (const [index, buffer] of buffers.entries()) {
    if (!isRecord(buffer)) fail(`buffers[${index}] must be an object`);
    const declaredLength = integerAtLeast(buffer.byteLength, 0, `buffers[${index}].byteLength`);
    if (buffer.uri === undefined) {
      if (index !== 0 || binaryChunk === null) fail(`buffers[${index}] has no URI or embedded GLB binary chunk`);
      if (binaryChunk.byteLength < declaredLength || binaryChunk.byteLength - declaredLength > 3) {
        fail(`embedded buffer byteLength does not match buffers[${index}].byteLength`);
      }
      actualLengths.push(binaryChunk.byteLength);
      continue;
    }
    const resource = await resolveLocalUri(buffer.uri, `buffers[${index}]`, baseDirectory);
    let byteLength = resource.byteLength;
    if (resource.embedded) {
      byteLength = decodeDataUri(buffer.uri, `buffers[${index}]`).byteLength;
    } else if (byteLength === null) {
      byteLength = declaredLength;
    } else {
      externalResources.set(buffer.uri, { type: "buffer", uri: buffer.uri, path: resource.path, byteLength });
    }
    if (byteLength < declaredLength) fail(`buffers[${index}] is shorter than its declared byteLength`);
    actualLengths.push(byteLength);
  }

  for (const [index, view] of bufferViews.entries()) {
    if (!isRecord(view)) fail(`bufferViews[${index}] must be an object`);
    const bufferIndex = integerAtLeast(view.buffer, 0, `bufferViews[${index}].buffer`);
    if (bufferIndex >= actualLengths.length) fail(`bufferViews[${index}] references a missing buffer`);
    const offset = view.byteOffset === undefined ? 0 : integerAtLeast(view.byteOffset, 0, `bufferViews[${index}].byteOffset`);
    const length = integerAtLeast(view.byteLength, 0, `bufferViews[${index}].byteLength`);
    if (offset + length > actualLengths[bufferIndex]) fail(`bufferViews[${index}] exceeds its buffer`);
  }

  for (const [index, image] of (document.images ?? []).entries()) {
    if (!isRecord(image)) fail(`images[${index}] must be an object`);
    const hasUri = image.uri !== undefined;
    const hasView = image.bufferView !== undefined;
    if (hasUri === hasView) fail(`images[${index}] must have exactly one of uri or bufferView`);
    if (hasUri) {
      const resource = await resolveLocalUri(image.uri, `images[${index}]`, baseDirectory);
      if (!resource.embedded && resource.byteLength !== null) {
        externalResources.set(image.uri, { type: "image", uri: image.uri, path: resource.path, byteLength: resource.byteLength });
      }
    } else {
      const viewIndex = integerAtLeast(image.bufferView, 0, `images[${index}].bufferView`);
      if (viewIndex >= bufferViews.length) fail(`images[${index}] references a missing bufferView`);
      if (typeof image.mimeType !== "string" || image.mimeType.length === 0) fail(`images[${index}] needs a mimeType when embedded`);
    }
  }

  return { externalResources: [...externalResources.values()], actualLengths };
}

function arrayOrEmpty(value) {
  return Array.isArray(value) ? value : [];
}

function summarizeDocument(document, hash, fileSize, resources) {
  const accessors = document.accessors ?? [];
  return {
    format: "glTF 2.0 binary",
    sha256: hash,
    fileSizeBytes: fileSize,
    bounds: summarizeBounds(document),
    vertexCount: accessors.reduce((total, accessor) => total + (Number.isInteger(accessor.count) ? accessor.count : 0), 0),
    meshes: arrayOrEmpty(document.meshes).map((mesh, index) => ({
      name: mesh.name ?? `mesh-${index}`,
      primitiveCount: arrayOrEmpty(mesh.primitives).length,
      materialIndexes: [...new Set(arrayOrEmpty(mesh.primitives).map((primitive) => primitive.material).filter(Number.isInteger))],
    })),
    materials: arrayOrEmpty(document.materials).map((material, index) => ({
      name: material.name ?? `material-${index}`,
      alphaMode: material.alphaMode ?? "OPAQUE",
      doubleSided: material.doubleSided === true,
      extensions: Object.keys(material.extensions ?? {}),
    })),
    textures: arrayOrEmpty(document.textures).map((texture, index) => ({
      name: texture.name ?? `texture-${index}`,
      sourceImage: texture.source ?? texture.extensions?.KHR_texture_basisu?.source ?? null,
      sampler: texture.sampler ?? null,
    })),
    animations: arrayOrEmpty(document.animations).map((animation, index) => {
      const samplerIndexes = arrayOrEmpty(animation.samplers).map((sampler) => sampler.input);
      const times = samplerIndexes
        .map((accessorIndex) => accessors[accessorIndex]?.max?.[0])
        .filter((time) => Number.isFinite(time));
      return {
        name: animation.name ?? `animation-${index}`,
        durationSeconds: times.length > 0 ? Math.max(...times) : null,
        channelCount: arrayOrEmpty(animation.channels).length,
      };
    }),
    externalResources: resources.externalResources,
  };
}

/** Parse and validate an in-memory GLB without fetching any external resources. */
export async function parseGlbBuffer(input, { baseDirectory } = {}) {
  const buffer = Buffer.isBuffer(input) ? input : Buffer.from(input);
  if (buffer.byteLength < 20) fail("GLB file is too short");
  if (buffer.readUInt32LE(0) !== GLB_MAGIC) fail("file does not have the GLB magic header");
  if (buffer.readUInt32LE(4) !== 2) fail("only GLB version 2 is supported");
  const declaredTotalLength = buffer.readUInt32LE(8);
  if (declaredTotalLength !== buffer.byteLength) fail("GLB declared length does not match file size");

  let cursor = 12;
  let jsonBuffer = null;
  let binaryChunk = null;
  while (cursor < buffer.byteLength) {
    if (cursor + 8 > buffer.byteLength) fail("GLB contains a truncated chunk header");
    const chunkLength = buffer.readUInt32LE(cursor);
    const chunkType = buffer.readUInt32LE(cursor + 4);
    cursor += 8;
    if (chunkLength % 4 !== 0 || cursor + chunkLength > buffer.byteLength) fail("GLB contains an invalid chunk length");
    const chunk = buffer.subarray(cursor, cursor + chunkLength);
    cursor += chunkLength;
    if (chunkType === JSON_CHUNK) {
      if (jsonBuffer !== null || binaryChunk !== null) fail("GLB JSON chunk must be first and appear once");
      jsonBuffer = chunk;
    } else if (chunkType === BIN_CHUNK) {
      if (jsonBuffer === null || binaryChunk !== null) fail("GLB binary chunk is misplaced or duplicated");
      binaryChunk = chunk;
    }
  }
  if (jsonBuffer === null) fail("GLB is missing its JSON chunk");

  let document;
  try {
    document = JSON.parse(jsonBuffer.toString("utf8").replace(/[\u0000 ]+$/g, ""));
  } catch (error) {
    fail(`GLB JSON chunk is invalid: ${error instanceof Error ? error.message : String(error)}`);
  }
  validateDocumentShape(document);
  const resources = await parseResources(document, binaryChunk, baseDirectory);
  const hash = createHash("sha256").update(buffer).digest("hex");
  return summarizeDocument(document, hash, buffer.byteLength, resources);
}

export async function inspectGlbFile(filePath) {
  const absoluteFile = path.resolve(filePath);
  const fileBuffer = await readFile(absoluteFile);
  const info = await stat(absoluteFile);
  if (!info.isFile()) fail("input path is not a file");
  return {
    fileName: path.basename(absoluteFile),
    ...await parseGlbBuffer(fileBuffer, { baseDirectory: path.dirname(absoluteFile) }),
  };
}

async function main() {
  const filePath = process.argv[2];
  if (!filePath) fail("usage: node scripts/inspect-assets.mjs <office.glb>");
  const manifest = await inspectGlbFile(filePath);
  process.stdout.write(`${JSON.stringify(manifest, null, 2)}\n`);
}

const calledDirectly = process.argv[1] && pathToFileURL(path.resolve(process.argv[1])).href === import.meta.url;
if (calledDirectly) {
  main().catch((error) => {
    process.stderr.write(`asset inspection failed: ${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  });
}
