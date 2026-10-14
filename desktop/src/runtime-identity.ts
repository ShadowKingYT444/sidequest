import type { DiffPage, FilePage, RuntimeArtifact, RuntimeFile, TextPage } from './types';

export const validDigest=(value:unknown):value is string=>typeof value==='string'&&/^[a-f0-9]{64}$/.test(value);
export function requireFrozenArtifact(value:RuntimeArtifact,jobId:string) {
  if(value.immutable!==true||value.job_id!==jobId||!validDigest(value.sha256))throw new Error('Frozen artifact identity is unavailable.');
}
export function requireFilePage(page:FilePage,artifact:RuntimeArtifact) {
  if(page.v!==1||page.artifact_id!==artifact.id||!artifact.candidate_id||page.candidate_id!==artifact.candidate_id||!Array.isArray(page.files)||page.files.length>100)throw new Error('Manifest identity mismatch.');
}
export function requireTextPage(page:TextPage,artifact:RuntimeArtifact,file:RuntimeFile|undefined) {
  if(page.v!==1||page.artifact_id!==artifact.id||page.file_id!==file?.file_id||page.immutable!==true||!file||page.sha256!==file.sha256||!validDigest(page.sha256)||!Array.isArray(page.lines)||page.lines.length>200)throw new Error('File identity mismatch.');
}
export function requireDiffPage(page:DiffPage,diff:RuntimeArtifact,manifest:RuntimeArtifact) {
  if(page.v!==1||page.artifact_id!==diff.id||!manifest.candidate_id||page.candidate_id!==manifest.candidate_id||diff.candidate_id!==manifest.candidate_id||!Array.isArray(page.rows)||page.rows.length>200)throw new Error('Diff identity mismatch.');
}
