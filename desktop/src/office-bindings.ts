export type Vector3 = [number, number, number];
export type ScreenSize = [number, number];

export interface CameraPose {
  position: Vector3;
  target: Vector3;
}

export interface OfficeStationBinding {
  id: string;
  label: string;
  workerId?: string;
  anchor: Vector3;
  rotation: Vector3;
  screenSize: ScreenSize;
  focus: CameraPose;
}

export interface OfficeBoardBinding {
  anchor: Vector3;
  rotation: Vector3;
  size: ScreenSize;
}

export interface OfficeBindings {
  modelUrl: "/office/office.glb";
  overview: CameraPose;
  stations: OfficeStationBinding[];
  board?: OfficeBoardBinding;
}

export class OfficeBindingValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "OfficeBindingValidationError";
  }
}

const OFFICE_BINDINGS_URL = "/office/bindings.json";
const OFFICE_MODEL_URL = "/office/office.glb";

function record(value: unknown, field: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new OfficeBindingValidationError(`${field} must be an object`);
  }
  return value as Record<string, unknown>;
}

function nonEmptyString(value: unknown, field: string): string {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new OfficeBindingValidationError(`${field} must be a non-empty string`);
  }
  return value;
}

function vector(value: unknown, field: string, length: 2 | 3): number[] {
  if (!Array.isArray(value) || value.length !== length) {
    throw new OfficeBindingValidationError(`${field} must contain exactly ${length} numbers`);
  }
  const result = value.map((component, index) => {
    if (typeof component !== "number" || !Number.isFinite(component)) {
      throw new OfficeBindingValidationError(`${field}[${index}] must be a finite number`);
    }
    return component;
  });
  return result;
}

function cameraPose(value: unknown, field: string): CameraPose {
  const pose = record(value, field);
  return {
    position: vector(pose.position, `${field}.position`, 3) as Vector3,
    target: vector(pose.target, `${field}.target`, 3) as Vector3,
  };
}

function positiveScreenSize(value: unknown, field: string): ScreenSize {
  const size = vector(value, field, 2) as ScreenSize;
  if (size[0] <= 0 || size[1] <= 0) {
    throw new OfficeBindingValidationError(`${field} dimensions must be greater than zero`);
  }
  return size;
}

/** Validate and copy the local, stable-ID binding table loaded by the desktop app. */
export function parseOfficeBindings(value: unknown): OfficeBindings {
  const source = record(value, "bindings");
  if (source.modelUrl !== OFFICE_MODEL_URL) {
    throw new OfficeBindingValidationError(`bindings.modelUrl must be ${OFFICE_MODEL_URL}`);
  }
  if (!Array.isArray(source.stations)) {
    throw new OfficeBindingValidationError("bindings.stations must be an array");
  }

  const ids = new Set<string>();
  const stations = source.stations.map((item, index): OfficeStationBinding => {
    const field = `bindings.stations[${index}]`;
    const station = record(item, field);
    const id = nonEmptyString(station.id, `${field}.id`);
    if (ids.has(id)) {
      throw new OfficeBindingValidationError(`duplicate station id: ${id}`);
    }
    ids.add(id);
    const workerId = station.workerId === undefined
      ? undefined
      : nonEmptyString(station.workerId, `${field}.workerId`);

    return {
      id,
      label: nonEmptyString(station.label, `${field}.label`),
      ...(workerId === undefined ? {} : { workerId }),
      anchor: vector(station.anchor, `${field}.anchor`, 3) as Vector3,
      rotation: vector(station.rotation, `${field}.rotation`, 3) as Vector3,
      screenSize: positiveScreenSize(station.screenSize, `${field}.screenSize`),
      focus: cameraPose(station.focus, `${field}.focus`),
    };
  });

  let board: OfficeBoardBinding | undefined;
  if (source.board !== undefined) {
    const value = record(source.board, "bindings.board");
    board = {
      anchor: vector(value.anchor, "bindings.board.anchor", 3) as Vector3,
      rotation: vector(value.rotation, "bindings.board.rotation", 3) as Vector3,
      size: positiveScreenSize(value.size, "bindings.board.size"),
    };
  }

  return {
    modelUrl: OFFICE_MODEL_URL,
    overview: cameraPose(source.overview, "bindings.overview"),
    stations,
    ...(board === undefined ? {} : { board }),
  };
}

/** Fetch only the explicitly allowlisted same-origin binding file. */
export async function loadOfficeBindings(
  url: string = OFFICE_BINDINGS_URL,
  fetcher: typeof fetch = fetch,
): Promise<OfficeBindings> {
  if (url !== OFFICE_BINDINGS_URL) {
    throw new OfficeBindingValidationError(`office bindings URL must be ${OFFICE_BINDINGS_URL}`);
  }

  const response = await fetcher(url, { credentials: "same-origin", cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Unable to load office bindings (${response.status} ${response.statusText})`);
  }
  let body: unknown;
  try {
    body = await response.json();
  } catch (error) {
    throw new OfficeBindingValidationError(
      `office bindings are not valid JSON: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
  return parseOfficeBindings(body);
}

/** Allow generated embedded-image blobs as well as local asset resources. */
export function validateOfficeResourceUrl(resourceUrl: string, pageUrl: string): string {
  if (resourceUrl.startsWith('data:')) return resourceUrl;
  const page = new URL(pageUrl);
  const resource = new URL(resourceUrl, new URL('/office/office.glb', page));
  if (resource.protocol === 'blob:') {
    const blobOrigin = new URL(resource.pathname);
    if (blobOrigin.protocol === page.protocol && blobOrigin.host === page.host && !blobOrigin.username && !blobOrigin.password) return resource.href;
    throw new Error('Office image blob is outside the local origin.');
  }
  let decoded: string;
  try { decoded = decodeURIComponent(resource.pathname); } catch { throw new Error('Invalid office resource path.'); }
  if (resource.protocol !== page.protocol || resource.host !== page.host || !decoded.startsWith('/office/') ||
      decoded.includes('\\') || decoded.includes('\0') || resource.username || resource.password ||
      decoded.split('/').some(part => part === '.' || part === '..') || resource.search || resource.hash) {
    throw new Error('Office resource is outside the local asset allowlist.');
  }
  return resource.href;
}
