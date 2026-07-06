import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { join, extname } from "node:path";
import server from "./dist/server/server.js";

const port = 3000;
const BACKEND_URL = "http://tees-server-prod:5000";

const MIME_TYPES = {
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.html': 'text/html',
};

createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://${req.headers.host}`);

    // 1. Proxy API requests
    if (url.pathname.startsWith("/api") || url.pathname.startsWith("/researchers") || url.pathname.startsWith("/papers") || url.pathname.startsWith("/research-areas") || url.pathname.startsWith("/conference-papers") || url.pathname.startsWith("/advisings") || url.pathname.startsWith("/analytics") || url.pathname.startsWith("/search")) {
        const proxyRes = await fetch(`${BACKEND_URL}${url.pathname}${url.search}`, {
            method: req.method,
            headers: req.headers,
            body: req.method !== "GET" && req.method !== "HEAD" ? req : null,
        });

        res.statusCode = proxyRes.status;
        for (const [key, value] of proxyRes.headers.entries()) {
            res.setHeader(key, value);
        }
        if (proxyRes.body) {
            for await (const chunk of proxyRes.body) {
                res.write(chunk);
            }
        }
        res.end();
        return;
    }

    // 2. Try to serve static file
    const filePath = join("dist/client", url.pathname);
    try {
      const content = await readFile(filePath);
      const ext = extname(filePath);
      res.setHeader('Content-Type', MIME_TYPES[ext] || 'text/plain');
      res.end(content);
      return;
    } catch (e) {
      // File not found, fall back to SSR
    }

    // 3. SSR fallback
    const request = new Request(url.toString(), {
      method: req.method,
      headers: req.headers,
      body: req.method !== "GET" && req.method !== "HEAD" ? req : null,
    });

    const response = await server.fetch(request, {}, {});

    res.statusCode = response.status;
    for (const [key, value] of response.headers.entries()) {
      res.setHeader(key, value);
    }

    if (response.body) {
      const reader = response.body.getReader();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        res.write(value);
      }
    }
    res.end();
  } catch (error) {
    console.error("Server error:", error);
    res.statusCode = 500;
    res.end("Internal Server Error");
  }
}).listen(port, () => {
  console.log(`Server listening on http://localhost:${port}`);
});
