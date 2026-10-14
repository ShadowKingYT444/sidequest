import type { ReadBridge } from './types';
async function read<T>(url: string): Promise<T> {
  const response = await fetch(url, { credentials: 'same-origin', headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error(`Local Git read failed (${response.status}). Check the host repository configuration.`);
  return response.json() as Promise<T>;
}
export const bridge: ReadBridge = window.sidequest ?? {
  snapshot: () => read('/__sidequest/snapshot'),
  diff: (id) => read(`/__sidequest/diff/${encodeURIComponent(id)}`),
};
