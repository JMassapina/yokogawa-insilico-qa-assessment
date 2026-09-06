import { createReadStream, existsSync } from 'node:fs';
import { createServer } from 'node:http';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const port = Number(process.env.PORT ?? 8899);

const ROUTES = {
  '/': { file: join(here, 'index.html'), type: 'text/html; charset=utf-8' },
  '/index.html': { file: join(here, 'index.html'), type: 'text/html; charset=utf-8' },
  '/escher.min.js': {
    file: join(here, '..', 'node_modules', 'escher', 'dist', 'escher.min.js'),
    type: 'text/javascript; charset=utf-8',
  },
};

const server = createServer((request, response) => {
  const url = new URL(request.url ?? '/', 'http://localhost');
  const route = ROUTES[url.pathname];

  if (!route || !existsSync(route.file)) {
    response.writeHead(404, { 'content-type': 'text/plain' });
    response.end('Not Found — Please ensure npm install was run inside web-tests');
    return;
  }

  response.writeHead(200, { 
    'content-type': route.type, 
    'cache-control': 'no-store, no-cache, must-revalidate' 
  });
  createReadStream(route.file).pipe(response);
});

server.listen(port, '127.0.0.1', () => {
  console.log(`🚀 Pinned local Escher application server listening on http://127.0.0.1:${port}`);
});
