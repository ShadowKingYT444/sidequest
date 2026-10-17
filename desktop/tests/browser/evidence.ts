import {mkdirSync} from 'node:fs';
import path from 'node:path';

// Isolate new acceptance runs without overwriting previous screenshots or diagnostics.
export function evidenceDirectory(...parts:string[]):string {
  const directory=path.resolve(process.env.SIDEQUEST_EVIDENCE_DIR??'../evidence/desktop',...parts);
  mkdirSync(directory,{recursive:true});
  return directory;
}
