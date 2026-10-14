/** Renderer-only drafts. File bytes and object URLs never cross the runtime bridge. */
export const LOCAL_DRAFT_LIMITS = Object.freeze({ text: 2000, files: 10, fileBytes: 10 * 1024 * 1024, totalBytes: 25 * 1024 * 1024 });

export interface LocalAttachment {
  id: string;
  file: File;
  name: string;
  size: number;
  mimeType: string;
  kind: 'image' | 'file';
  fingerprint: string;
  previewURL?: string;
}
export interface LocalDraft { text: string; attachments: LocalAttachment[] }
export interface DraftIssue { code: 'type' | 'size' | 'total' | 'count' | 'duplicate' | 'read' | 'text'; message: string; fileName?: string }
export interface DraftOperations {pending:Promise<void>;reading:number;issues:DraftIssue[];listeners:Set<()=>void>;selection?:[number,number]}
export const createDraftOperations=():DraftOperations=>({pending:Promise.resolve(),reading:0,issues:[],listeners:new Set()});
export interface LocalURLStore { createObjectURL: (blob: Blob) => string; revokeObjectURL: (url: string) => void }
export interface LocalTransfer {
  files: ArrayLike<File>;
  items?: ArrayLike<{ kind: string; getAsFile: () => File | null }>;
  getData: (format: string) => string;
}

const imageTypes: Record<string, string> = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', webp: 'image/webp' };
const textExtensions = new Set(['txt', 'md', 'markdown', 'csv', 'tsv', 'json', 'jsonl', 'yaml', 'yml', 'toml', 'xml', 'log', 'ts', 'tsx', 'js', 'jsx', 'mjs', 'cjs', 'py', 'rb', 'rs', 'go', 'java', 'c', 'h', 'cpp', 'hpp', 'cs', 'css', 'scss', 'sql', 'vue', 'svelte', 'swift', 'kt', 'diff', 'patch']);
const textTypes = new Set(['text/plain', 'text/markdown', 'text/csv', 'text/tab-separated-values', 'text/yaml', 'text/x-yaml', 'text/x-python', 'text/javascript', 'text/css', 'text/xml', 'application/json', 'application/x-ndjson', 'application/yaml', 'application/x-yaml', 'application/toml', 'application/javascript', 'application/typescript', 'application/xml']);
const issue = (code: DraftIssue['code'], message: string, fileName?: string): DraftIssue => ({ code, message, ...(fileName ? { fileName } : {}) });
const extension = (name: string) => name.split('.').at(-1)?.toLowerCase() ?? '';
const fileType = (file: File) => file.type.toLowerCase().split(';')[0].trim();
const fingerprint = (file: File) => JSON.stringify([file.name, file.size, file.lastModified, fileType(file)]);
const rasterExtension = (file: File): string | undefined => {
  const ext = extension(file.name);
  if (ext in imageTypes) return ext;
  // Some clipboard implementations name image Files "image", without a suffix.
  if (!file.name.includes('.')) return Object.entries(imageTypes).find(([, mime]) => mime === fileType(file))?.[0];
  return undefined;
};

export const createLocalDraft = (): LocalDraft => ({ text: '', attachments: [] });
export const localAttachmentBytes = (draft: LocalDraft): number => draft.attachments.reduce((sum, attachment) => sum + attachment.size, 0);
export const cleanPlainText = (text: string): string => text.replace(/\r\n?/g, '\n').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g, '');

/** Preserve existing text when a paste would exceed the coding adapter's bound. */
export function insertDraftText(text: string, pasted: string, start = text.length, end = start): { text: string; caret: number; issue?: DraftIssue } {
  start = Math.max(0, Math.min(text.length, start)); end = Math.max(start, Math.min(text.length, end));
  const clean = cleanPlainText(pasted);
  const available = Math.max(0, LOCAL_DRAFT_LIMITS.text - (text.length - (end - start)));
  const inserted = clean.slice(0, available);
  return { text: text.slice(0, start) + inserted + text.slice(end), caret: start + inserted.length, ...(clean.length > available ? { issue: issue('text', 'Prompts are limited to 2,000 characters.') } : {}) };
}

/** Metadata validation is deliberately allowlisted; unsupported files remain unattached. */
export function validateLocalFile(file: File): DraftIssue | null {
  const name = file.name;
  if (!name || name.length > 240 || /[\u0000-\u001f\u007f/\\]/.test(name)) return issue('type', 'This file name is unsupported.', name);
  if (!Number.isSafeInteger(file.size) || file.size < 0 || file.size > LOCAL_DRAFT_LIMITS.fileBytes) return issue('size', `${name} exceeds the 10 MiB file limit.`, name);
  const ext = extension(name), mime = fileType(file), raster = rasterExtension(file);
  if (raster && (!mime || mime === imageTypes[raster])) return null;
  if (ext === 'pdf' && (!mime || mime === 'application/pdf')) return null;
  if (textExtensions.has(ext) && (!mime || textTypes.has(mime))) return null;
  return issue('type', `${name}: use PNG, JPEG, GIF, WebP, PDF or a plain text/code file.`, name);
}

function rasterSignature(bytes: Uint8Array, ext: string): boolean {
  if (ext === 'png') return [137, 80, 78, 71, 13, 10, 26, 10].every((value, index) => bytes[index] === value);
  if (ext === 'jpg' || ext === 'jpeg') return bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255;
  if (ext === 'gif') return String.fromCharCode(...bytes.slice(0, 6)) === 'GIF87a' || String.fromCharCode(...bytes.slice(0, 6)) === 'GIF89a';
  if (ext === 'webp') return String.fromCharCode(...bytes.slice(0, 4)) === 'RIFF' && String.fromCharCode(...bytes.slice(8, 12)) === 'WEBP';
  return false;
}

/** Reject disguised SVG/HTML before creating a raster preview; no file is executed. */
export async function validateRasterFile(file: File): Promise<DraftIssue | null> {
  const raster = rasterExtension(file);
  if (!raster) return null;
  try {
    const bytes = new Uint8Array(await file.slice(0, 16).arrayBuffer());
    return rasterSignature(bytes, raster) ? null : issue('type', `${file.name} is not a supported raster image.`, file.name);
  } catch { return issue('read', `${file.name} could not be read. Try selecting it again.`, file.name); }
}

export async function addLocalFiles(draft: LocalDraft, files: Iterable<File>, urls: LocalURLStore = URL): Promise<{ draft: LocalDraft; issues: DraftIssue[] }> {
  const attachments = [...draft.attachments], issues: DraftIssue[] = [];
  const known = new Set(attachments.map(item => item.fingerprint));
  let bytes = localAttachmentBytes(draft);
  for (const file of files) {
    const problem = validateLocalFile(file);
    if (problem) { issues.push(problem); continue; }
    const key = fingerprint(file);
    if (known.has(key)) { issues.push(issue('duplicate', `${file.name} is already attached.`, file.name)); continue; }
    if (attachments.length >= LOCAL_DRAFT_LIMITS.files) { issues.push(issue('count', 'Attach up to 10 files.', file.name)); continue; }
    if (bytes + file.size > LOCAL_DRAFT_LIMITS.totalBytes) { issues.push(issue('total', 'Attachments exceed the 25 MiB total limit.', file.name)); continue; }
    const rasterProblem = await validateRasterFile(file);
    if (rasterProblem) { issues.push(rasterProblem); continue; }
    const kind = rasterExtension(file) ? 'image' : 'file';
    let previewURL: string | undefined;
    try { if (kind === 'image') previewURL = urls.createObjectURL(file); }
    catch { issues.push(issue('read', `${file.name} could not be previewed. Try selecting it again.`, file.name)); continue; }
    attachments.push({ id: crypto.randomUUID(), file, name: file.name, size: file.size, mimeType: fileType(file), kind, fingerprint: key, ...(previewURL ? { previewURL } : {}) });
    known.add(key); bytes += file.size;
  }
  return { draft: { text: draft.text, attachments }, issues };
}

export function removeLocalAttachment(draft: LocalDraft, id: string, urls: LocalURLStore = URL): LocalDraft {
  const attachment = draft.attachments.find(item => item.id === id);
  if (attachment?.previewURL) urls.revokeObjectURL(attachment.previewURL);
  return { ...draft, attachments: draft.attachments.filter(item => item.id !== id) };
}

/** Call only when disposing the retained draft, not when navigating away from its monitor. */
export function revokeLocalDraft(draft: LocalDraft, urls: LocalURLStore = URL): void {
  for (const attachment of draft.attachments) if (attachment.previewURL) urls.revokeObjectURL(attachment.previewURL);
}

/** Read only text/plain and real browser Files. HTML, paths, URLs and directories are ignored. */
export function extractLocalTransfer(transfer: LocalTransfer): { text: string; files: File[] } {
  const files: File[] = [], known = new Set<string>();
  const add = (file: File | null) => { if (file && !known.has(fingerprint(file))) { files.push(file); known.add(fingerprint(file)); } };
  for (const item of Array.from(transfer.items ?? [])) if (item.kind === 'file') add(item.getAsFile());
  for (const file of Array.from(transfer.files)) add(file);
  return { text: cleanPlainText(transfer.getData('text/plain')), files };
}

export function localDraftIssue(draft: LocalDraft): DraftIssue | null {
  if (draft.text.length > LOCAL_DRAFT_LIMITS.text) return issue('text', 'Prompts are limited to 2,000 characters.');
  if (draft.attachments.length > LOCAL_DRAFT_LIMITS.files) return issue('count', 'Attach up to 10 files.');
  if (localAttachmentBytes(draft) > LOCAL_DRAFT_LIMITS.totalBytes) return issue('total', 'Attachments exceed the 25 MiB total limit.');
  return draft.attachments.map(item => validateLocalFile(item.file)).find(item => item !== null) ?? null;
}
