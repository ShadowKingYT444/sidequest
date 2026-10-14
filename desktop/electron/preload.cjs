'use strict';

const { contextBridge, ipcRenderer } = require('electron');

const sessionRuntime=(method,args)=>ipcRenderer.invoke('sidequest:runtime',method,args).then(value=>{
  if(value?.v===1&&value.error){
    const code=typeof value.error.code==='string'&&/^[A-Z_]+$/.test(value.error.code)?value.error.code:'UNAVAILABLE';
    const status=Number.isInteger(value.error.status)&&value.error.status>=400&&value.error.status<=599?value.error.status:503;
    throw Object.assign(new Error(`Local runtime request failed (${status}, ${code}).`),{code,status});
  }
  return value;
});
const FILE_ID_PATTERN = /^f_[a-f0-9]{32}$/;
const runtime = Object.freeze({
  snapshot: () => ipcRenderer.invoke('sidequest:runtime', 'snapshot', []),
  capabilities: () => ipcRenderer.invoke('sidequest:runtime', 'capabilities', []),
  runInfo: id => ipcRenderer.invoke('sidequest:runtime', 'runInfo', [id]),
  runEvents: (id, afterSeq=0) => ipcRenderer.invoke('sidequest:runtime', 'runEvents', [id, afterSeq]),
  assignSession:(station,job,run,revision)=>ipcRenderer.invoke('sidequest:runtime','assignSession',[station,job,run,revision]),
  clearSession:(station,revision)=>ipcRenderer.invoke('sidequest:runtime','clearSession',[station,revision]),
  stageAttachment:(run,key,name,mime,base64)=>sessionRuntime('stageAttachment',[run,key,name,mime,base64]),
  sessionMessage:(run,id,prompt,attachments,revision)=>sessionRuntime('sessionMessage',[run,id,prompt,attachments,revision]),
  commandStatus:id=>sessionRuntime('commandStatus',[id]),
  job: id => ipcRenderer.invoke('sidequest:runtime', 'job', [id]),
  artifact: id => ipcRenderer.invoke('sidequest:runtime', 'artifact', [id]),
  artifacts: (id, cursor = '') => ipcRenderer.invoke('sidequest:runtime', 'artifacts', [id, cursor]),
  files: (id, cursor = '') => ipcRenderer.invoke('sidequest:runtime', 'files', [id, cursor]),
  text: (artifact, file, startLine = 1) => ipcRenderer.invoke('sidequest:runtime', 'text', [artifact, file, startLine]),
  diff: (artifact, file, cursor = '') => ipcRenderer.invoke('sidequest:runtime', 'diff', [artifact, file, cursor]),
  register: revision => ipcRenderer.invoke('sidequest:runtime', 'register', [revision]),
  submitInspection: (project, title, revision) => ipcRenderer.invoke('sidequest:runtime', 'submitInspection', [project, title, revision]),
  run: (job, revision) => ipcRenderer.invoke('sidequest:runtime', 'run', [job, revision]),
  stop: revision => ipcRenderer.invoke('sidequest:runtime', 'stop', [revision]),
  refreshReadiness: revision => ipcRenderer.invoke('sidequest:runtime', 'refreshReadiness', [revision]),
  enableCoding: (project, revision) => ipcRenderer.invoke('sidequest:runtime', 'enableCoding', [project, revision]),
  submitCoding: (project, title, objective, writePrefix, budget, revision) => ipcRenderer.invoke('sidequest:runtime', 'submitCoding', [project,title,objective,writePrefix,budget,revision]),
  runCoding: (job, revision) => ipcRenderer.invoke('sidequest:runtime', 'runCoding', [job, revision]),
});

contextBridge.exposeInMainWorld('sidequest', Object.freeze({
  runtime,
  providers:()=>ipcRenderer.invoke('sidequest:providers'),
  snapshot() {
    return ipcRenderer.invoke('sidequest:snapshot');
  },
  diff(fileId) {
    if (typeof fileId !== 'string' || !FILE_ID_PATTERN.test(fileId)) {
      return Promise.reject(Object.assign(new Error('The file identifier is invalid.'), { code: 'INVALID_INPUT' }));
    }
    return ipcRenderer.invoke('sidequest:diff', fileId);
  },
}));
