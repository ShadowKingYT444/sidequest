import type { ReadBridge, RuntimeBridge } from './types';
async function read<T>(url: string): Promise<T> {
  const response = await fetch(url, { credentials: 'same-origin', headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error(`Local Git read failed (${response.status}). Check the host repository configuration.`);
  return response.json() as Promise<T>;
}
async function runtimeRequest<T>(method:string,args:(string|number)[]=[]):Promise<T> {
  const response=await fetch(`/__sidequest/runtime/${method}`,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(args)});
  if(!response.ok)throw new Error('The local runtime request failed. Refresh state and review the host configuration.');
  return response.json() as Promise<T>;
}
const runtime:RuntimeBridge={
  snapshot:()=>runtimeRequest('snapshot'),capabilities:()=>runtimeRequest('capabilities'),job:id=>runtimeRequest('job',[id]),artifacts:(id,cursor='')=>runtimeRequest('artifacts',[id,cursor]),
  runInfo:id=>runtimeRequest('runInfo',[id]),runEvents:(id,afterSeq=0)=>runtimeRequest('runEvents',[id,afterSeq]),
  artifact:id=>runtimeRequest('artifact',[id]),
  files:(id,cursor='')=>runtimeRequest('files',[id,cursor]),text:(artifact,file,startLine=1)=>runtimeRequest('text',[artifact,file,startLine]),diff:(artifact,file,cursor='')=>runtimeRequest('diff',[artifact,file,cursor]),
  register:revision=>runtimeRequest('register',[revision]),submitInspection:(project,title,revision)=>runtimeRequest('submitInspection',[project,title,revision]),run:(job,revision)=>runtimeRequest('run',[job,revision]),stop:revision=>runtimeRequest('stop',[revision]),
  refreshReadiness:revision=>runtimeRequest('refreshReadiness',[revision]),enableCoding:(project,revision)=>runtimeRequest('enableCoding',[project,revision]),submitCoding:(project,title,objective,writePrefix,budget,revision)=>runtimeRequest('submitCoding',[project,title,objective,writePrefix,budget,revision]),runCoding:(job,revision)=>runtimeRequest('runCoding',[job,revision]),
};
export const bridge: ReadBridge = window.sidequest ?? {
  snapshot: () => read('/__sidequest/snapshot'),
  diff: (id) => read(`/__sidequest/diff/${encodeURIComponent(id)}`),
  providers:()=>read('/__sidequest/providers'),
  runtime,
};
