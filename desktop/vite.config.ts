import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import { createRequire } from 'node:module';
import path from 'node:path';
const require = createRequire(import.meta.url);
const { createGitReader } = require('./electron/git-reader.cjs');
const { createRuntimeClient, dispatchRuntime, runtimeInputLimit } = require('./electron/runtime-client.cjs');
const {discoverProviders}=require('./electron/provider-discovery.cjs');
const desktopRoot = path.dirname(new URL(import.meta.url).pathname);
function localReads(): Plugin {
  return {
    name: 'sidequest-read-only-development',
    configureServer(server) {
      const reader = createGitReader(process.env.SIDEQUEST_REPO ?? path.resolve(desktopRoot, '..'), process.env.SIDEQUEST_BASE ?? 'HEAD~1');
      const runtime = createRuntimeClient({url:process.env.SIDEQUEST_RUNTIME_URL, token:process.env.SIDEQUEST_RUNTIME_TOKEN, tokenFile:process.env.SIDEQUEST_API_TOKEN_FILE,repo:process.env.SIDEQUEST_REPO ?? path.resolve(desktopRoot,'..'),baseRef:process.env.SIDEQUEST_PROJECT_BASE ?? 'HEAD'});
      server.middlewares.use('/__sidequest', async (request, response) => {
        response.setHeader('Cache-Control', 'no-store');
        response.setHeader('Content-Type', 'application/json');
        response.setHeader('X-Content-Type-Options', 'nosniff');
        const host = request.headers.host;
        const origin = request.headers.origin;
        if (host !== '127.0.0.1:5173' || (origin && origin !== 'http://127.0.0.1:5173') || request.headers['sec-fetch-site'] === 'cross-site') {
          response.statusCode = 403; response.end(JSON.stringify({ error: 'Local origin required.' })); return;
        }
        const runtimeMethod = /^\/runtime\/([A-Za-z]+)$/.exec(request.url ?? '')?.[1];
        if (runtimeMethod) {
          if (request.method !== 'POST' || origin !== 'http://127.0.0.1:5173' || request.headers['content-type'] !== 'application/json') { response.statusCode=403;response.end(JSON.stringify({error:'Local JSON request required.'}));return; }
          try {
            let body='';for await (const chunk of request) {body+=chunk.toString('utf8');if(Buffer.byteLength(body)>runtimeInputLimit(runtimeMethod))throw new Error('Input limit exceeded.');}
            const data=await dispatchRuntime(runtime,runtimeMethod,JSON.parse(body));
            response.end(JSON.stringify(data));
          } catch(reason) {const failure=reason as {code?:string;status?:number};response.statusCode=Number.isInteger(failure.status)&&failure.status!>=400&&failure.status!<=599?failure.status!:503;response.end(JSON.stringify({v:1,error:{code:typeof failure.code==='string'&&/^[A-Z_]+$/.test(failure.code)?failure.code:'UNAVAILABLE',message:'Local runtime request failed. Refresh state and review the host configuration.'}}));}
          return;
        }
        if (request.method !== 'GET') { response.statusCode = 405; response.end(JSON.stringify({ error: 'Read-only endpoint.' })); return; }
        try {
          const url = request.url ?? '';
          let data: unknown;
          if (url === '/snapshot') data = await reader.snapshot();
          else if(url==='/providers')data=await discoverProviders();
          else if (/^\/diff\/f_[a-f0-9]{32}$/.test(url)) data = await reader.diff(url.slice(6));
          else { response.statusCode = 404; response.end(JSON.stringify({ error: 'Unknown read.' })); return; }
          response.end(JSON.stringify(data));
        } catch { response.statusCode = 503; response.end(JSON.stringify({ error: 'Git data is unavailable for the configured repository.' })); }
      });
    },
  };
}
export default defineConfig({
  base: './', plugins: [react(), localReads()],
  // Monaco 0.57 vendors DOMPurify 3.4.15. Replace the actual imported module,
  // as well as its npm dependency, so the shipped editor uses the patched code.
  resolve:{alias:[{find:/^\.\/dompurify\/dompurify\.js$/,replacement:path.resolve(desktopRoot,'node_modules/dompurify/dist/purify.es.mjs')}]},
  server: { host: '127.0.0.1', port: 5173, strictPort: true, fs: { strict: true, allow: [desktopRoot] }, headers: { 'X-Content-Type-Options': 'nosniff' } },
  build: { target: 'es2022' },
});
