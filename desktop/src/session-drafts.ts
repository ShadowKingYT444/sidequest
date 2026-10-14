import {createLocalDraft, localDraftIssue, validateRasterFile, revokeLocalDraft, type LocalDraft, type LocalAttachment, type LocalURLStore} from './local-drafts.ts';
import type {CommandReply} from './types.ts';

const UUID=/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/;
const ID=/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$/;
export interface StagedAttachment {id:string;run_id:string;name:string;media_type:string;size_bytes:number;sha256:string}
export interface CommandStatus {v:1;found:boolean;command?:CommandReply}
export interface SessionTransport {
 snapshot():Promise<{revision:number}>;
 stageAttachment(run:string,key:string,name:string,mime:string,base64:string):Promise<{v:1;attachment:StagedAttachment}>;
 sessionMessage(run:string,commandId:string,prompt:string,attachmentIds:string,revision:number):Promise<CommandReply>;
 commandStatus(commandId:string):Promise<CommandStatus>;
}
export interface PendingMessage {commandId:string;runId:string;text:string;localIds:string[];attachmentIds:string[];expectedRevision?:number;state:'staging'|'sending'|'uncertain'|'not_found'|'rejected'}
interface StoredAttachment {id:string;blob:Blob;name:string;lastModified:number;size:number;mimeType:string;kind:'image'|'file';fingerprint:string;stagedId?:string;stagedRunId?:string}
interface StoredDraft {v:1;text:string;attachments:StoredAttachment[];pending?:PendingMessage;selection?:[number,number]}
export interface DraftStorage {read(key:string):Promise<unknown>;write(key:string,value:StoredDraft):Promise<void>}
export interface DraftState {draft:LocalDraft;loading:boolean;saving:boolean;pending?:PendingMessage;status:string;error:string;selection?:[number,number]}

/** Only local blobs and opaque identities are stored. Host paths, credentials and object URLs are excluded. */
export function createIndexedDraftStorage(factory:IDBFactory=globalThis.indexedDB):DraftStorage {
 let opened:Promise<IDBDatabase>|undefined;
 const database=()=>opened??=new Promise((resolve,reject)=>{
  if(!factory){reject(Error('Local draft storage is unavailable.'));return;}
  const request=factory.open('sidequest-local-drafts',1);
  request.onupgradeneeded=()=>{if(!request.result.objectStoreNames.contains('drafts'))request.result.createObjectStore('drafts');};
  request.onsuccess=()=>{const db=request.result;db.onversionchange=()=>{db.close();opened=undefined;};resolve(db);};
  request.onerror=()=>reject(request.error??Error('Local draft storage could not open.'));
  request.onblocked=()=>reject(Error('Local draft storage is blocked by another window.'));
 });
 async function transact(key:string,value?:StoredDraft):Promise<unknown>{
  const db=await database();return new Promise((resolve,reject)=>{
   const tx=db.transaction('drafts',value?'readwrite':'readonly'),store=tx.objectStore('drafts');
   const request=value?store.put(value,key):store.get(key);let result:unknown;
   request.onsuccess=()=>{result=request.result;};tx.oncomplete=()=>resolve(result);tx.onabort=()=>reject(tx.error??Error('Draft storage transaction aborted.'));tx.onerror=()=>reject(tx.error??Error('Draft storage transaction failed.'));
  });
 }
 return {read:key=>transact(key),write:async(key,value)=>{await transact(key,value);}};
}

function pendingValid(value:PendingMessage):boolean {
 return !!value&&UUID.test(value.commandId)&&ID.test(value.runId)&&typeof value.text==='string'&&value.text.trim().length>0&&value.text.length<=2000&&!/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(value.text)&&Array.isArray(value.localIds)&&value.localIds.length<=10&&value.localIds.every(id=>typeof id==='string'&&UUID.test(id))&&new Set(value.localIds).size===value.localIds.length&&Array.isArray(value.attachmentIds)&&value.attachmentIds.length<=10&&value.attachmentIds.every(id=>typeof id==='string'&&ID.test(id))&&new Set(value.attachmentIds).size===value.attachmentIds.length&&['staging','sending','uncertain','not_found','rejected'].includes(value.state)&&(value.state==='staging'&&value.expectedRevision===undefined||Number.isSafeInteger(value.expectedRevision)&&value.expectedRevision!>=0);
}
const persisted=(state:DraftState):StoredDraft=>({v:1,text:state.draft.text,attachments:state.draft.attachments.map(item=>({id:item.id,blob:item.file,name:item.name,lastModified:item.file.lastModified,size:item.size,mimeType:item.mimeType,kind:item.kind,fingerprint:item.fingerprint,...(item.stagedId?{stagedId:item.stagedId,stagedRunId:item.stagedRunId}:{})})),...(state.pending?{pending:{...state.pending,localIds:[...state.pending.localIds],attachmentIds:[...state.pending.attachmentIds]}}:{}),...(state.selection?{selection:state.selection}:{})});

/** Retained across monitor navigation; network mutations require their identity to be committed locally first. */
export class SessionDraftStore {
 state:DraftState={draft:createLocalDraft(),loading:true,saving:false,status:'Restoring local draft…',error:''};
 readonly ready:Promise<void>;private queue=Promise.resolve();private busy=false;private persistenceFailed=false;private restorationFailed=false;private listeners=new Set<()=>void>();
 readonly key:string;private storage:DraftStorage;private urls:LocalURLStore;
 constructor(key:string,storage:DraftStorage=createIndexedDraftStorage(),urls:LocalURLStore=URL){this.key=key;this.storage=storage;this.urls=urls;this.ready=this.restore();}
 subscribe=(listener:()=>void)=>{this.listeners.add(listener);return()=>{this.listeners.delete(listener);};};
 getSnapshot=()=>this.state;
 private update(next:Partial<DraftState>){this.state={...this.state,...next};for(const listener of this.listeners)listener();}
 private async restore(){
  try{
   const raw=await this.storage.read(this.key);if(raw===undefined){this.update({loading:false,status:'Local draft'});return;}
   const value=raw as StoredDraft;
   if(!value||value.v!==1||typeof value.text!=='string'||!Array.isArray(value.attachments)||value.attachments.length>10||value.pending&&!pendingValid(value.pending))throw Error('Invalid draft record.');
   const attachments:LocalAttachment[]=[];
   for(const item of value.attachments){
    if(!item||typeof item.id!=='string'||!UUID.test(item.id)||!(item.blob instanceof Blob)||item.blob.size!==item.size||typeof item.name!=='string'||typeof item.mimeType!=='string'||!Number.isFinite(item.lastModified)||typeof item.fingerprint!=='string'||item.fingerprint.length>1024||!['image','file'].includes(item.kind)||item.stagedId&&(!ID.test(item.stagedId)||!item.stagedRunId||!ID.test(item.stagedRunId)))throw Error('Invalid attachment record.');
    const file=new File([item.blob],item.name,{type:item.mimeType,lastModified:item.lastModified});
    if(await validateRasterFile(file))throw Error('Invalid local image.');
    attachments.push({id:item.id,file,name:item.name,size:item.size,mimeType:item.mimeType,kind:item.kind,fingerprint:item.fingerprint,...(item.kind==='image'?{previewURL:this.urls.createObjectURL(file)}:{}),...(item.stagedId?{stagedId:item.stagedId,stagedRunId:item.stagedRunId}:{})});
   }
   const draft={text:value.text,attachments};if(localDraftIssue(draft)||new Set(attachments.map(item=>item.id)).size!==attachments.length)throw Error('Invalid stored draft.');
   let pending=value.pending;if(pending?.state==='sending')pending={...pending,state:'uncertain'};
   const selection=Array.isArray(value.selection)&&value.selection.length===2&&value.selection.every(n=>Number.isSafeInteger(n)&&n>=0&&n<=draft.text.length)?value.selection:undefined;
   this.update({draft,loading:false,pending,selection,status:pending?'Send pending · check status':'Local draft saved'});
  }catch{this.restorationFailed=true;this.persistenceFailed=true;this.update({loading:false,error:'Could not restore the local draft. Sending is blocked to protect a possibly pending message.',status:'Local storage unavailable'});}
 }
 change(draft:LocalDraft){if(this.state.loading)return;this.update({draft});if(this.restorationFailed)return;void this.save().catch(()=>{});}
 setSelection(selection:[number,number]){this.update({selection});if(this.restorationFailed)return;void this.save().catch(()=>{});}
 private save():Promise<void>{
  if(this.restorationFailed)return Promise.reject(Error('The original draft could not be safely restored.'));
  const record=persisted(this.state);this.update({saving:true});
  const result=this.queue.catch(()=>{}).then(()=>this.storage.write(this.key,record));
  this.queue=result;
  return result.then(()=>{if(this.queue===result){const recovered=this.persistenceFailed;this.persistenceFailed=false;this.update({saving:false,...(recovered?{error:''}:{}),status:this.state.pending?this.state.status:'Local draft saved'});}},()=>{this.persistenceFailed=true;this.update({saving:false,error:'Could not save the local draft. Check device storage before sending.',status:'Local save failed'});throw Error('Local draft storage failed.');});
 }
 flush=()=>this.queue;
 private accepted(reply:CommandReply,pending:PendingMessage){
  if(reply.v!==1||reply.accepted!==true||reply.command_id!==pending.commandId||!Number.isSafeInteger(reply.revision)||reply.revision<0)throw Error('The message receipt did not match this send.');
  const removed=this.state.draft.attachments.filter(item=>pending.localIds.includes(item.id));revokeLocalDraft({text:'',attachments:removed},this.urls);
  this.update({draft:{text:this.state.draft.text===pending.text?'':this.state.draft.text,attachments:this.state.draft.attachments.filter(item=>!pending.localIds.includes(item.id))},pending:undefined,status:'Message accepted',error:''});
 }
 async send(target:{runId:string;revision:number},transport:SessionTransport){
  await this.ready;if(this.busy||this.state.pending||this.persistenceFailed)return;
  if(!ID.test(target.runId)||!Number.isSafeInteger(target.revision)||target.revision<0||!this.state.draft.text.trim()||localDraftIssue(this.state.draft))return;
  this.update({pending:{commandId:crypto.randomUUID(),runId:target.runId,text:this.state.draft.text,localIds:this.state.draft.attachments.map(item=>item.id),attachmentIds:[],state:'staging'},status:'Preparing message…',error:''});
  await this.perform(target,transport);
 }
 private async perform(target:{runId:string;revision:number},transport:SessionTransport){
  if(this.busy)return;const pending=this.state.pending;if(!pending||pending.runId!==target.runId)return;this.busy=true;
  try{
   await this.save();
   if(pending.state==='staging'){
    const attachmentIds:string[]=[];
    for(const localId of pending.localIds){
     const attachment=this.state.draft.attachments.find(item=>item.id===localId);if(!attachment)throw Error('A submitted attachment was removed. Restore it before retrying.');
     let stagedId=attachment.stagedRunId===pending.runId?attachment.stagedId:undefined;
     if(!stagedId){
      this.update({status:`Staging ${attachment.name}…`});
      const bytes=new Uint8Array(await attachment.file.arrayBuffer());let binary='';for(let offset=0;offset<bytes.length;offset+=32768)binary+=String.fromCharCode(...bytes.subarray(offset,offset+32768));
      const result=await transport.stageAttachment(pending.runId,attachment.id,attachment.name,attachment.mimeType,btoa(binary));const staged=result.attachment;
      if(result.v!==1||!staged||!ID.test(staged.id)||staged.run_id!==pending.runId||staged.name!==attachment.name||staged.media_type!==attachment.mimeType||staged.size_bytes!==attachment.size||!/^[a-f0-9]{64}$/.test(staged.sha256))throw Error('Staged attachment identity did not match the local file.');
      stagedId=staged.id;
      this.update({draft:{...this.state.draft,attachments:this.state.draft.attachments.map(item=>item.id===localId?{...item,stagedId,stagedRunId:pending.runId}:item)}});await this.save();
     }
     attachmentIds.push(stagedId);
    }
    const snapshot=await transport.snapshot();if(!Number.isSafeInteger(snapshot.revision)||snapshot.revision<0)throw Error('The current runtime revision could not be verified.');
    this.update({pending:{...pending,attachmentIds,expectedRevision:snapshot.revision,state:'sending'},status:'Sending message…'});await this.save();
   }else{this.update({pending:{...pending,state:'sending'},status:'Sending message…'});await this.save();}
   const current=this.state.pending!;
   if(!Number.isSafeInteger(current.expectedRevision))throw Error('The original send revision is unavailable.');
   const result=await transport.sessionMessage(current.runId,current.commandId,current.text,JSON.stringify(current.attachmentIds),current.expectedRevision!);
   this.accepted(result,current);await this.save();this.update({status:'Message accepted'});
  }catch(reason){
   const current=this.state.pending;
   const failure=reason as {code?:string;status?:number};
   const rejected=current?.state==='sending'&&Number.isInteger(failure?.status)&&failure.status!>=400&&failure.status!<500&&['INVALID_INPUT','VERSION_CONFLICT','POLICY_DENIED','BUDGET_LIMIT','NOT_FOUND'].includes(failure.code??'');
   if(current)this.update({pending:{...current,state:current.state==='staging'?'staging':rejected?'rejected':'uncertain'},status:current.state==='staging'?'Staging incomplete':rejected?'Message rejected · review before sending':'Send pending · check status',error:this.persistenceFailed?this.state.error:reason instanceof Error?reason.message:'Sending could not be verified.'});
   if(!this.persistenceFailed)await this.save().catch(()=>{});
  }finally{this.busy=false;}
 }
 async reconcile(transport:SessionTransport){
  await this.ready;const pending=this.state.pending;if(this.busy||!pending)return;this.busy=true;this.update({status:'Checking message receipt…',error:''});
  try{
   const reply=await transport.commandStatus(pending.commandId);
   if(reply.v!==1||typeof reply.found!=='boolean')throw Error('Message receipt is unavailable.');
   if(reply.found){if(!reply.command)throw Error('Message receipt is incomplete.');this.accepted(reply.command,pending);await this.save();this.update({status:'Message accepted'});}
   else{this.update({pending:{...pending,state:pending.state==='staging'?'staging':pending.state==='rejected'?'rejected':'not_found'},status:'No message receipt yet · retry uses the same identity',error:''});await this.save();}
  }catch(reason){this.update({status:'Send pending · check status',error:reason instanceof Error?reason.message:'Message receipt is unavailable.'});}
  finally{this.busy=false;}
 }
 async reviewRejected(){await this.ready;if(this.busy||this.state.pending?.state!=='rejected')return;this.update({pending:undefined,status:'Review the retained draft before sending',error:''});await this.save().catch(()=>{});}
 async retry(target:{runId:string;revision:number},transport:SessionTransport){await this.ready;if(this.state.pending&&['staging','not_found'].includes(this.state.pending.state)&&!this.persistenceFailed)await this.perform(target,transport);}
}
