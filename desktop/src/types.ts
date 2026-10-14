export interface GitFile { id: string; path: string; status: string; binary?: boolean; additions?: number; deletions?: number }
export interface Snapshot {
  v: 1; mode: 'local-git'; project: { name: string; branch: string; rootLabel: string };
  baseRevision: string; candidateRevision: string; files: GitFile[];
  agent: { state: 'unavailable'; message: string };
}
export interface GitDiff {
  id: string; path: string; original: string; modified: string; language: string;
  binary: boolean; unavailableReason?: string; baseRevision: string; candidateRevision: string; readOnly: true;
}
export interface ReadBridge { snapshot(): Promise<Snapshot>; diff(fileId: string): Promise<GitDiff> }
declare global { interface Window { sidequest?: ReadBridge } }
