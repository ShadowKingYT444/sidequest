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
export interface RuntimeProject {id:string;name:string;base_revision:string;status:string;policy?:{allowed_actions:string[]}}
export interface RuntimeJob {id:string;project_id?:string;title:string;state:string;execution_profile?:'local_git_inspection'|'codex_session'|null;blocked_reason?:string|null;artifact_ids:string[];checks:{id:string;state:string;evidence_artifact_id?:string|null}[];events:{id:string;at:string;type:string;message:string}[];tasks?:{id:string;state:string;depends_on?:string[];worker_id?:string|null;attempt_id?:string|null}[];run_ids?:string[];budget_usd:number;spent_usd:number|null;worker_id:string|null}
export interface RuntimeRun {id:string;job_id:string;task_id:string;worker_id:string|null;attempt:number;state:string;model:string|null;effort:string|null;started_at:string|null;ended_at:string|null;usage:{input_tokens:number|null;cached_input_tokens:number|null;output_tokens:number|null;total_tokens:number|null;cost_usd:number|string|null;uncertain:boolean}}
export interface RunEvent {seq:number;at:string;type:string;message:string;artifact_id:string|null;task_id:string;job_id?:string}
export interface RunEventPage {v:1;run_id:string;items:RunEvent[];next_after_seq:number;has_more:boolean}
export interface RuntimeSnapshot {v:1;revision:number;mode:string;projects:RuntimeProject[];jobs:RuntimeJob[];stopped:boolean}
export interface RuntimeCapabilities {v:1;features:{local_git_inspection?:boolean;computer_artifacts:boolean;coding?:boolean;codex_session?:boolean};worker_model:{id:string;effort:string;verified:boolean};reasons:string[];codex?:{state:string;host_enabled?:boolean;catalog_verified?:boolean;usd_cost_enforced:boolean;reason?:string|null;subscription_quota?:{ordinary_usage_allowed:boolean|null;purchased_credits_available:boolean|null}}}
export interface RuntimeArtifact {id:string;kind:string;job_id:string;sha256:string;display_name?:string;size_bytes?:number;candidate_id?:string|null;source_revision:string;immutable?:boolean}
export interface RuntimeFile {file_id:string;path:string;status:string;binary:boolean;size_bytes:number;sha256:string|null;media_type:string}
export interface FilePage {v:1;artifact_id:string;candidate_id:string;files:RuntimeFile[];next_cursor:string|null}
export interface DiffPage {v:1;artifact_id:string;candidate_id:string;base_revision:string;candidate_revision:string;rows:{kind:string;old_line:number|null;new_line:number|null;text:string;clipped?:boolean}[];next_cursor:string|null}
export interface TextPage {v:1;artifact_id:string;file_id:string;sha256:string;immutable:boolean;lines:{number:number;text:string;clipped?:boolean}[];next_line:number|null}
export interface CommandReply {v:1;accepted:boolean;command_id:string;revision:number;result?:{job_id?:string;project_id?:string}}
export interface StationAssignment {jobId:string;projectId:string}
export interface ProviderDiscovery {v:1;observedAt:string;providers:{id:string;name:string;installed:boolean;binaryPath:string|null;version:string|null;homePath:string|null;runtime:'local'}[]}
export interface JobView {artifactId:string;fileId:string;tab:'text'|'diff';startLine:number;scrollTop:number;artifactCursors?:string[];artifactPage?:number;fileCursors?:string[];filePage?:number;diffCursors?:string[];diffPage?:number}
export interface RuntimeBridge {
  snapshot():Promise<RuntimeSnapshot>;capabilities():Promise<RuntimeCapabilities>;job(id:string):Promise<{v:1;job:RuntimeJob}>;
  runInfo(id:string):Promise<{v:1;run:RuntimeRun}>;runEvents(id:string,afterSeq?:number):Promise<RunEventPage>;
  artifact(id:string):Promise<{v:1;artifact:RuntimeArtifact;preview_text:string|null}>;
  artifacts(id:string,cursor?:string):Promise<{v:1;items:RuntimeArtifact[];next_cursor:string|null}>;files(id:string,cursor?:string):Promise<FilePage>;
  text(artifact:string,file:string,startLine?:number):Promise<TextPage>;diff(artifact:string,file:string,cursor?:string):Promise<DiffPage>;
  register(revision:number):Promise<CommandReply>;submitInspection(project:string,title:string,revision:number):Promise<CommandReply>;
  run(job:string,revision:number):Promise<CommandReply>;stop(revision:number):Promise<CommandReply>;
  refreshReadiness(revision:number):Promise<CommandReply>;enableCoding(project:string,revision:number):Promise<CommandReply>;
  submitCoding(project:string,title:string,objective:string,writePrefix:string,budget:string,revision:number):Promise<CommandReply>;runCoding(job:string,revision:number):Promise<CommandReply>;
}
export interface ReadBridge { snapshot(): Promise<Snapshot>; diff(fileId: string): Promise<GitDiff>;providers():Promise<ProviderDiscovery>;runtime:RuntimeBridge }
declare global { interface Window { sidequest?: ReadBridge } }
