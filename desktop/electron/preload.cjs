'use strict';

const { contextBridge, ipcRenderer } = require('electron');

const FILE_ID_PATTERN = /^f_[a-f0-9]{32}$/;
const runtime = Object.freeze({
  snapshot: () => ipcRenderer.invoke('sidequest:runtime', 'snapshot', []),
  capabilities: () => ipcRenderer.invoke('sidequest:runtime', 'capabilities', []),
  runInfo: id => ipcRenderer.invoke('sidequest:runtime', 'runInfo', [id]),
  runEvents: (id, afterSeq=0) => ipcRenderer.invoke('sidequest:runtime', 'runEvents', [id, afterSeq]),
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
