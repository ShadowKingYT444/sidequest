import {useEffect,useRef,useState} from 'react';
import {bridge} from './bridge';
import ProviderTiles from './ProviderTiles';
import {PROVIDERS,providerReadiness,type ProviderId,type ProviderReadinessInput} from './provider-readiness';
import './ProviderPicker.css';
interface Props {stationLabel:string;projectId?:string;onChoose:(id:ProviderId)=>void;onClose:()=>void;onConnect:()=>void}
export default function ProviderPicker({stationLabel,projectId,onChoose,onClose,onConnect}:Props){
  const [setup,setSetup]=useState<ProviderReadinessInput|null>(null),[error,setError]=useState(false);
  const panel=useRef<HTMLElement>(null),close=useRef(onClose);close.current=onClose;
  useEffect(()=>{let alive=true;Promise.all([bridge.providers(),bridge.runtime.capabilities(),bridge.runtime.snapshot()]).then(([discovery,capabilities,snapshot])=>{if(alive)setSetup({discovery,capabilities,snapshot,project:snapshot.projects?.find(project=>project.id===projectId)??snapshot.projects?.[0]});}).catch(()=>{if(alive)setError(true);});return()=>{alive=false;};},[projectId]);
  useEffect(()=>{panel.current?.focus();const key=(event:KeyboardEvent)=>{if(event.key==='Escape'){event.preventDefault();event.stopPropagation();close.current();}if(event.key==='Tab'){const controls=Array.from(panel.current?.querySelectorAll<HTMLElement>('button:not(:disabled)')??[]);const first=controls[0],last=controls.at(-1);if(event.shiftKey&&(document.activeElement===first||document.activeElement===panel.current)){event.preventDefault();last?.focus();}else if(!event.shiftKey&&(document.activeElement===last||document.activeElement===panel.current)){event.preventDefault();first?.focus();}}};document.addEventListener('keydown',key,true);return()=>document.removeEventListener('keydown',key,true);},[]);
  const ready=setup?PROVIDERS.filter(provider=>providerReadiness(provider.id,setup).available):[];
  return <section className="provider-picker" role="dialog" aria-modal="true" aria-label="Choose provider" tabIndex={-1} ref={panel}>
    <header><h2>{stationLabel}</h2><button aria-label="Close provider picker" onClick={onClose}>×</button></header>
    {!setup&&!error?<p role="status">Reading providers…</p>:<>{ready.length&&setup?<ProviderTiles {...setup} value="" onChange={onChoose} connectedOnly label="Connected providers"/>:<p>{error?'Providers unavailable':'No connected providers'}</p>}<button className="provider-connect" onClick={onConnect}>Connect provider <svg aria-hidden="true" width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4"><path d="M3 13 13 3M5 3h8v8"/></svg></button></>}
  </section>;
}
