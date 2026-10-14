import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import { createRequire } from 'node:module';
import path from 'node:path';
const require = createRequire(import.meta.url);
const { createGitReader } = require('./electron/git-reader.cjs');
const desktopRoot = path.dirname(new URL(import.meta.url).pathname);
function localReads(): Plugin {
  return {
    name: 'sidequest-read-only-development',
    configureServer(server) {
      const reader = createGitReader(process.env.SIDEQUEST_REPO ?? path.resolve(desktopRoot, '..'), process.env.SIDEQUEST_BASE ?? 'HEAD~1');
      server.middlewares.use('/__sidequest', async (request, response) => {
        response.setHeader('Cache-Control', 'no-store');
        response.setHeader('Content-Type', 'application/json');
        response.setHeader('X-Content-Type-Options', 'nosniff');
        const host = request.headers.host;
        const origin = request.headers.origin;
        if (host !== '127.0.0.1:5173' || (origin && origin !== 'http://127.0.0.1:5173') || request.headers['sec-fetch-site'] === 'cross-site') {
          response.statusCode = 403; response.end(JSON.stringify({ error: 'Local origin required.' })); return;
        }
        if (request.method !== 'GET') { response.statusCode = 405; response.end(JSON.stringify({ error: 'Read-only endpoint.' })); return; }
        try {
          const url = request.url ?? '';
          let data: unknown;
          if (url === '/snapshot') data = await reader.snapshot();
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
  server: { host: '127.0.0.1', port: 5173, strictPort: true, fs: { strict: true, allow: [desktopRoot] }, headers: { 'X-Content-Type-Options': 'nosniff' } },
  build: { target: 'es2022' },
});
