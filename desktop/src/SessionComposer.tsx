import {useEffect,useRef,useState,useSyncExternalStore} from 'react';
import {bridge} from './bridge';
import PromptComposer from './PromptComposer';
import {sessionMessageReason,sessionAttachmentReason} from './session-message-readiness';
import type {DraftOperations} from './local-drafts';
import type {SessionDraftStore} from './session-drafts';
import type {RuntimeCapabilities,RuntimeJob,RuntimeRun} from './types';
interface Props {store:SessionDraftStore;operations:DraftOperations;job?:RuntimeJob;run?:RuntimeRun;known:boolean;active:boolean;onAccepted:()=>void}
export default function SessionComposer({store,operations,job,run,known,active,onAccepted}:Props){
 const state=useSyncExternalStore(store.subscribe,store.getSnapshot),[caps,setCaps]=useState<RuntimeCapabilities>();
 const loaded=useRef(false);
 useEffect(()=>{if(!active)return;let alive=true,timer:ReturnType<typeof setTimeout>|undefined;async function read(){try{const value=await bridge.runtime.capabilities();if(alive)setCaps(value);}catch{if(alive)setCaps(undefined);}if(alive)timer=setTimeout(()=>void read(),5000);}void read();return()=>{alive=false;clearTimeout(timer);};},[active,run?.id]);
 useEffect(()=>{if(!state.loading&&!loaded.current){loaded.current=true;if(state.selection)operations.selection=state.selection;}},[state.loading,store,operations]);
 const reason=state.loading?'Restoring the saved local draft.':state.error&&state.status.startsWith('Local')?state.error:sessionMessageReason(caps,job,run,known,active)??sessionAttachmentReason(state.draft,caps);
 const canSubmit=!reason&&!state.pending&&!state.loading;
 async function send(){if(!canSubmit||!run)return;await store.send({runId:run.id,revision:0},bridge.runtime);if(!store.state.pending&&store.state.status==='Message accepted')onAccepted();}
 async function reconcile(){await store.reconcile(bridge.runtime);if(!store.state.pending&&store.state.status==='Message accepted')onAccepted();}
 async function retry(){if(reason||!run)return;await store.retry({runId:run.id,revision:0},bridge.runtime);if(!store.state.pending&&store.state.status==='Message accepted')onAccepted();}
 const inFlight=/^(Preparing|Staging |Sending |Checking )/.test(state.status);
 return <>
  <PromptComposer draft={state.draft} onChange={draft=>store.change(draft)} getCurrentDraft={()=>store.state.draft} operations={operations} canSubmit={canSubmit} onSubmit={()=>void send()} disabledReason={state.pending?'The prior send must be reconciled before another message.':reason??undefined} loading={state.loading} selection={state.selection} onSelection={selection=>store.setSelection(selection)} label="Message this session" status={state.status}/>
  {(state.pending||state.error)&&<div className="prompt-transport-status" role="status"><span>{state.error||state.status}</span>{state.pending&&<button type="button" disabled={inFlight} onClick={()=>void reconcile()}>Check send status</button>}{state.pending&&['staging','not_found'].includes(state.pending.state)&&<button type="button" disabled={!!reason||inFlight||state.pending.runId!==run?.id} onClick={()=>void retry()}>Retry same message</button>}{state.pending?.state==='rejected'&&<button type="button" onClick={()=>void store.reviewRejected()}>Review retained draft</button>}</div>}
 </>;
}
