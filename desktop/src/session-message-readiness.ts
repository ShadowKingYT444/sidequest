import type {RuntimeCapabilities, RuntimeJob, RuntimeRun} from './types.ts';
import type {LocalDraft} from './local-drafts.ts';
const money=(value:unknown):number|null=>{if(typeof value!=='number'&&(typeof value!=='string'||!/^\d+(?:\.\d+)?$/.test(value)))return null;const amount=Number(value);return Number.isFinite(amount)&&amount>=0?amount:null;};
/** The renderer explains current availability. The host and runtime independently recheck all production gates. */
export function sessionMessageReason(caps:RuntimeCapabilities|undefined,job:RuntimeJob|undefined,run:RuntimeRun|undefined,known:boolean,active:boolean):string|null {
 if(!known)return 'Session ownership could not be verified.';
 if(!job||!run)return 'Reading this session before sending.';
 if(job.execution_profile!=='codex_session')return 'This recorded run does not accept provider messages.';
 if(!['verifying','accepted'].includes(job.state))return 'Wait for the current task to settle before sending a follow-up.';
 const task=job.tasks?.find(item=>item.id===run.task_id);
 if(job.tasks?.length&&(!task||task.attempt_id!==run.id))return 'The current session attempt could not be verified.';
 if(run.state!=='completed'||!run.ended_at)return 'Wait for this session to finish before sending a follow-up.';
 if(run.usage.uncertain!==false||money(run.usage.cost_usd)===null||money(job.spent_usd)===null||money(job.budget_usd)===null)return 'The remaining session budget could not be verified.';
 if(money(job.budget_usd)!-money(job.spent_usd)!<=0)return 'This session has no remaining approved budget.';
 if(!active)return 'Return to this session to send a message.';
 if(!caps||caps.v!==1||caps.features?.session_messages!==true)return 'This host has no verified session message transport.';
 if(caps.features.coding!==true||caps.features.codex_session!==true||caps.codex?.host_enabled!==true||caps.codex.state!=='available'||caps.codex.catalog_verified!==true||caps.worker_model?.verified!==true)return 'Provider execution readiness and host consent could not be verified.';
 if(caps.codex.usd_cost_enforced!==true)return 'This host cannot enforce the approved spending limit.';
 return null;
}
export function sessionAttachmentReason(draft:LocalDraft,caps:RuntimeCapabilities|undefined):string|null {
 if(!draft.attachments.length)return null;
 if(caps?.features.session_attachments!==true)return 'This provider does not support attachment transport.';
 if(draft.attachments.some(item=>item.name.toLowerCase().endsWith('.pdf')))return 'This provider accepts UTF-8 text and raster images. Remove the PDF before sending.';
 if(draft.attachments.reduce((sum,item)=>sum+item.size,new TextEncoder().encode(draft.text).length)>1024*1024)return 'This provider accepts up to 1 MiB of prompt and attachment content per message.';
 return null;
}
