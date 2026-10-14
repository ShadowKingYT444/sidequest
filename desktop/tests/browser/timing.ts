import {test as base, expect} from '@playwright/test';
import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';

// Collect diagnostics without adding waits, retries or changing assertions.
export const test=base.extend<{timings:void}>({timings:[async({page},use,info)=>{
  const started=Date.now(), network:unknown[]=[], errors:unknown[]=[], navigations:unknown[]=[];
  page.on('requestfinished',request=>network.push({url:request.url(),at:Date.now()-started,timing:request.timing()}));
  page.on('requestfailed',request=>errors.push({url:request.url(),at:Date.now()-started,error:request.failure()}));
  page.on('pageerror',error=>errors.push({at:Date.now()-started,error:error.message}));
  page.on('console',message=>{if(message.type()==='error'||/context lost/i.test(message.text()))errors.push({at:Date.now()-started,type:message.type(),error:message.text()});});
  page.on('framenavigated',frame=>{if(frame===page.mainFrame())navigations.push({at:Date.now()-started,url:frame.url()});});
  await page.addInitScript(()=>{
    performance.setResourceTimingBufferSize(3000);
    const events:unknown[]=[];(window as unknown as {__startupEvents:unknown[]}).__startupEvents=events;
    new PerformanceObserver(list=>{for(const entry of list.getEntries())if(events.length<500)events.push(entry.toJSON());}).observe({type:'longtask',buffered:true});
    document.addEventListener('webglcontextlost',event=>events.push({type:'webglcontextlost',at:performance.now(),status:(event as WebGLContextEvent).statusMessage}),true);
    document.addEventListener('webglcontextrestored',()=>events.push({type:'webglcontextrestored',at:performance.now()}),true);
  });
  await use();
  const browser=page.isClosed()?null:await page.evaluate(()=>({
    events:(window as unknown as {__startupEvents:unknown[]}).__startupEvents,
    entries:performance.getEntries().map(entry=>({...entry.toJSON(),detail:(entry as PerformanceMark).detail})),
    actors:document.querySelector('.app-footer')?.outerHTML,
    mode:document.querySelector('main')?.getAttribute('data-mode'),
    editors:document.querySelectorAll('.diff-editor').length,
  })).catch(error=>({captureError:String(error)}));
  const directory=path.resolve('../evidence/desktop/repair-20261014',process.env.SIDEQUEST_EVIDENCE_RUN??'timings');await mkdir(directory,{recursive:true});
  const file=path.join(directory,`${info.title.replace(/[^a-z0-9]+/gi,'-')}-${info.status}.json`);
  await writeFile(file,JSON.stringify({test:info.title,status:info.status,elapsedMs:Date.now()-started,navigations,network,errors,browser},null,2));
}, {auto:true}]});
export {expect};
export type {Page} from '@playwright/test';
