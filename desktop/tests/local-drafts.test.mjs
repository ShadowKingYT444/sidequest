import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {LOCAL_DRAFT_LIMITS,createLocalDraft,cleanPlainText,insertDraftText,validateLocalFile,addLocalFiles,removeLocalAttachment,revokeLocalDraft,extractLocalTransfer,localDraftIssue} from '../src/local-drafts.ts';

const text = (name='notes.txt',size=3,type='text/plain') => new File([new Uint8Array(size)],name,{type,lastModified:1});
const png = (name='image.png') => new File([new Uint8Array([137,80,78,71,13,10,26,10,0,0,0,0])],name,{type:'image/png',lastModified:1});
function urlStore(){const created=[],revoked=[];return {created,revoked,createObjectURL(blob){created.push(blob);return `blob:local-${created.length}`;},revokeObjectURL(url){revoked.push(url);}};}

test('plain paste is inert, normalizes controls and retains text around a bounded selection',()=>{
  assert.equal(cleanPlainText('<script>x</script>\r\nhello\0\x01\tworld'),'<script>x</script>\nhello\tworld');
  assert.deepEqual(insertDraftText('before after','local',7,7),{text:'before localafter',caret:12});
  const result=insertDraftText('a'.repeat(1998),'BCDE',100,100);
  assert.equal(result.text.length,2000);assert.equal(result.text.slice(100,102),'BC');assert.equal(result.issue.code,'text');
  assert.deepEqual(createLocalDraft(),{text:'',attachments:[]});
});

test('allowlist rejects executable/SVG/HTML, MIME confusion and unsafe names; text/code/PDF stay inert',()=>{
  for(const file of [text('x.svg',3,'image/svg+xml'),text('x.exe',3,'application/octet-stream'),text('x.html',3,'text/html'),text('x.png',3,'image/svg+xml'),text('../notes.txt'),text('bad\0name.txt')])assert.equal(validateLocalFile(file).code,'type');
  for(const file of [text('notes.md',3,''),text('code.ts',3,'text/plain'),text('report.pdf',3,'application/pdf'),text('config.json',3,'application/json')])assert.equal(validateLocalFile(file),null);
  assert.equal(validateLocalFile(text('big.txt',LOCAL_DRAFT_LIMITS.fileBytes+1)).code,'size');
});

test('count, per-file and total byte bounds preserve the existing valid local draft',async()=>{
  const urls=urlStore();
  const counted=await addLocalFiles(createLocalDraft(),Array.from({length:11},(_,index)=>text(`note-${index}.txt`)),urls);
  assert.equal(counted.draft.attachments.length,10);assert.equal(counted.issues[0].code,'count');assert.equal(urls.created.length,0);
  const over=await addLocalFiles(createLocalDraft(),[text('oversize.txt',LOCAL_DRAFT_LIMITS.fileBytes+1)],urls);
  assert.equal(over.draft.attachments.length,0);assert.equal(over.issues[0].code,'size');
  const totals=await addLocalFiles(createLocalDraft(),[text('a.txt',10*1024*1024),text('b.txt',10*1024*1024),text('c.txt',6*1024*1024)],urls);
  assert.equal(totals.draft.attachments.length,2);assert.equal(totals.issues[0].code,'total');assert.equal(localDraftIssue(totals.draft),null);
});

test('deduplication is stable across picker/paste metadata and rejected additions do not allocate URLs',async()=>{
  const urls=urlStore(),file=png();
  const added=await addLocalFiles({text:'kept',attachments:[]},[file,file,text('image.png',12,'image/svg+xml')],urls);
  assert.equal(added.draft.text,'kept');assert.equal(added.draft.attachments.length,1);assert.deepEqual(added.issues.map(item=>item.code),['duplicate','type']);
  assert.equal(added.draft.attachments[0].file,file);assert.equal(added.draft.attachments[0].kind,'image');assert.equal(urls.created.length,1);
  const again=await addLocalFiles(added.draft,[new File([await file.arrayBuffer()],file.name,{type:file.type,lastModified:file.lastModified})],urls);
  assert.equal(again.issues[0].code,'duplicate');assert.equal(urls.created.length,1);
});

test('raster previews require matching magic bytes; only local image URLs are created and revoked explicitly',async()=>{
  const urls=urlStore();
  const disguised=new File(['<svg xmlns="http://www.w3.org/2000/svg"><script/></svg>'],'hidden.png',{type:'image/png'});
  const added=await addLocalFiles(createLocalDraft(),[disguised,png(),text('readme.txt')],urls);
  assert.equal(added.issues[0].code,'type');assert.equal(added.draft.attachments.length,2);assert.equal(urls.created.length,1);
  assert.equal(added.draft.attachments[1].previewURL,undefined);
  const retained={...added.draft};assert.equal(urls.revoked.length,0);
  const removed=removeLocalAttachment(retained,retained.attachments[0].id,urls);
  assert.equal(removed.attachments.length,1);assert.deepEqual(urls.revoked,['blob:local-1']);
  revokeLocalDraft(removed,urls);assert.equal(urls.revoked.length,1);
  revokeLocalDraft(retained,urls);assert.deepEqual(urls.revoked,['blob:local-1','blob:local-1']);
});

test('clipboard images without suffixes get verified raster previews without accepting disguised extensions',async()=>{
  const urls=urlStore();
  const raw=png();
  const file=new File([await raw.arrayBuffer()],'image',{type:'image/png'});
  const result=await addLocalFiles(createLocalDraft(),[file,new File([await raw.arrayBuffer()],'image.svg',{type:'image/png'})],urls);
  assert.equal(result.draft.attachments.length,1);assert.equal(result.draft.attachments[0].kind,'image');assert.equal(urls.created.length,1);assert.equal(result.issues[0].code,'type');
});

test('clipboard/drop extraction reads only plain text and File objects, ignores HTML/paths/directories and deduplicates',()=>{
  const file=text(),formats=[];
  const extracted=extractLocalTransfer({files:[file],items:[{kind:'string',getAsFile(){throw Error('must not call');}},{kind:'file',getAsFile:()=>file},{kind:'file',getAsFile:()=>null}],getData(format){formats.push(format);return format==='text/plain'?'plain\r\n<em>literal</em>':'https://do-not-fetch.invalid';}});
  assert.deepEqual(formats,['text/plain']);assert.equal(extracted.text,'plain\n<em>literal</em>');assert.deepEqual(extracted.files,[file]);
});

test('draft helpers and composer contain no upload, bridge or dispatch path',async()=>{
  const sources=await Promise.all(['../src/local-drafts.ts','../src/PromptComposer.tsx'].map(path=>readFile(new URL(path,import.meta.url),'utf8')));
  for(const source of sources){assert.doesNotMatch(source,/\bfetch\s*\(|XMLHttpRequest|FormData\s*\(|bridge\.runtime|electron|sendBeacon\s*\(/);assert.doesNotMatch(source,/dangerouslySetInnerHTML|innerHTML\s*=/);}
});
