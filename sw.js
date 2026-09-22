/* Service Worker — 🇮🇹意大利语实景会话
 * 性能策略（v2）：
 *  - 只接管 /audio/*.mp3：CacheFirst + 后台缓存（文件名按内容 sha1 哈希、不可变，重复播放秒开、可离线）
 *  - 命中缓存时兼容 <audio> 的 Range 请求，返回 206 + Content-Range（否则部分浏览器/Safari 会绕过缓存重新请求）
 *  - 其余资源（html/js/css）一律不拦截，直接走网络 —— 站点改版永远不会被旧缓存挡住
 * 部署新内容时请把下方 CACHE 版本号 +1（如 ital-conv-v2 -> v3），旧缓存会自动清理。
 */
const CACHE = 'ital-conv-v2';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // 同源 + 仅音频
  if (url.origin !== self.location.origin) return;
  if (url.pathname.indexOf('/audio/') === -1) return;

  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const cached = await cache.match(req);
    if (cached) {
      // 满足 Range 请求：从缓存的整文件中切片返回 206
      const range = req.headers.get('Range');
      if (range) {
        const buf = await cached.arrayBuffer();
        const total = buf.byteLength;
        const m = /bytes=(\d*)-(\d*)/.exec(range);
        const start = m && m[1] ? parseInt(m[1], 10) : 0;
        const end = m && m[2] ? parseInt(m[2], 10) : total - 1;
        if (start > end || start >= total) {
          return new Response('', { status: 416, headers: { 'Content-Range': 'bytes */' + total } });
        }
        const slice = buf.slice(start, end + 1);
        return new Response(slice, {
          status: 206,
          headers: {
            'Content-Type': 'audio/mpeg',
            'Content-Range': 'bytes ' + start + '-' + end + '/' + total,
            'Accept-Ranges': 'bytes',
            'Content-Length': String(slice.byteLength),
          },
        });
      }
      return cached;
    }
    // 未缓存：取完整文件（忽略 Range，便于整文件缓存），再按需切片返回
    try {
      const fullReq = new Request(req.url, { method: 'GET', headers: {} });
      const res = await fetch(fullReq);
      if (res && res.ok) {
        cache.put(req.url, res.clone()); // 后台缓存整文件，不阻塞响应
      }
      if (!res || !res.ok) return cached || Response.error();
      const range = req.headers.get('Range');
      if (range) {
        const buf = await res.arrayBuffer();
        const total = buf.byteLength;
        const m = /bytes=(\d*)-(\d*)/.exec(range);
        const start = m && m[1] ? parseInt(m[1], 10) : 0;
        const end = m && m[2] ? parseInt(m[2], 10) : total - 1;
        if (start > end || start >= total) {
          return new Response('', { status: 416, headers: { 'Content-Range': 'bytes */' + total } });
        }
        const slice = buf.slice(start, end + 1);
        return new Response(slice, {
          status: 206,
          headers: {
            'Content-Type': 'audio/mpeg',
            'Content-Range': 'bytes ' + start + '-' + end + '/' + total,
            'Accept-Ranges': 'bytes',
            'Content-Length': String(slice.byteLength),
          },
        });
      }
      return res;
    } catch (err) {
      return cached || Response.error();
    }
  })());
});
