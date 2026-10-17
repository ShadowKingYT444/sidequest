'use strict';

const fs = require('node:fs');
const path = require('node:path');

function isInside(parent, target) {
  const relative = path.relative(parent, target);
  return relative === '' || (!relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative));
}

function contentTypeFor(filePath) {
  const extension = path.extname(filePath).toLowerCase();
  return ({
    '.css': 'text/css; charset=utf-8', '.html': 'text/html; charset=utf-8',
    '.ico': 'image/x-icon', '.js': 'text/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8', '.png': 'image/png',
    '.svg': 'image/svg+xml', '.webp': 'image/webp', '.woff': 'font/woff',
    '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg', '.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json',
    '.wasm': 'application/wasm',
  })[extension] || 'application/octet-stream';
}

function createStaticAssetHandler(distRoot) {
  const root = path.resolve(distRoot);
  return async function serveAppRequest(request) {
    if (request.method !== 'GET') return new Response('Method not allowed', { status: 405 });
    let parsed;
    try {
      parsed = new URL(request.url);
    } catch {
      return new Response('Not found', { status: 404 });
    }
    if (parsed.protocol !== 'app:' || parsed.hostname !== 'sidequest' || parsed.username || parsed.password) {
      return new Response('Not found', { status: 404 });
    }
    let relative;
    try {
      relative = decodeURIComponent(parsed.pathname).replace(/^\/+/, '') || 'index.html';
    } catch {
      return new Response('Not found', { status: 404 });
    }
    if (relative.includes('\\') || relative.includes('\0') || relative.split('/').some((part) => part === '.' || part === '..')) {
      return new Response('Not found', { status: 404 });
    }

    let distRealPath;
    try {
      distRealPath = await fs.promises.realpath(root);
    } catch {
      return new Response('Not found', { status: 404 });
    }
    let resolved;
    let stat;
    const candidates = [path.resolve(root, relative), path.resolve(root, 'public', relative)];
    for (const candidate of candidates) {
      if (!isInside(root, candidate)) continue;
      try {
        const possible = await fs.promises.realpath(candidate);
        if (!isInside(distRealPath, possible)) continue;
        const possibleStat = await fs.promises.stat(possible);
        if (!possibleStat.isFile() || possibleStat.size > 64 * 1024 * 1024) continue;
        resolved = possible;
        stat = possibleStat;
        break;
      } catch {
        // Try the copied public-asset root after the regular Vite output path.
      }
    }
    if (!resolved || !stat) return new Response('Not found', { status: 404 });
    let body;
    try {
      body = await fs.promises.readFile(resolved);
    } catch {
      return new Response('Not found', { status: 404 });
    }
    return new Response(body, {
      status: 200,
      headers: {
        'Content-Type': contentTypeFor(resolved),
        'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; worker-src 'self' blob:; frame-src 'none'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
        'X-Content-Type-Options': 'nosniff',
        'Referrer-Policy': 'no-referrer',
        'Cache-Control': 'no-store',
      },
    });
  };
}

module.exports = { createStaticAssetHandler };
