import type { DiffPage, FilePage, RuntimeArtifact, RuntimeFile, TextPage, OfficeSession, RuntimeSnapshot } from './types';

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

const id=(value:unknown):value is string=>typeof value==='string'&&/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$/.test(value);
export function requireOfficeSessions(snapshot:RuntimeSnapshot):OfficeSession[]{
  if(snapshot.v!==1||!Number.isSafeInteger(snapshot.revision)||snapshot.revision<0||!Array.isArray(snapshot.jobs)||snapshot.jobs.length>20||snapshot.jobs.some(job=>!job||!id(job.id)||typeof job.title!=='string'||job.title.length>200))throw new Error('Runtime session state is unavailable.');
  const rows=snapshot.office_sessions??[];
  if(!Array.isArray(rows)||rows.length>24)throw new Error('Office session state is invalid.');
  const stations=new Set(),runs=new Set(),workers=new Set();
  for(const row of rows){
    if(!row||!/^parent_(?:00[1-9]|01[0-9]|02[0-4])$/.test(row.station_id)||![row.job_id,row.run_id,row.worker_id,row.project_id].every(id)||typeof row.assigned_at!=='string'||row.assigned_at.length>128||!Number.isFinite(Date.parse(row.assigned_at))||stations.has(row.station_id)||runs.has(row.run_id)||workers.has(row.worker_id))throw new Error('Office session identity is invalid.');
    stations.add(row.station_id);runs.add(row.run_id);workers.add(row.worker_id);
  }
  return rows;
}
