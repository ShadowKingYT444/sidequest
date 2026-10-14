'use strict';

const { contextBridge, ipcRenderer } = require('electron');

const FILE_ID_PATTERN = /^f_[a-f0-9]{32}$/;

contextBridge.exposeInMainWorld('sidequest', Object.freeze({
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
