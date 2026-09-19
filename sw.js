/* Service Worker — 🇮🇹意大利语实景会话
 * 加载效率优化：
 *  - audio/ 资源：cache-first（文件名按内容 sha1 哈希，不可变，重复播放秒开、可离线）
 *  - HTML / 导航：network-first + 缓存兜底（始终拿到最新页面，断网也能看已访问过的页）
 *  - 其它同源资源：network-first + 缓存兜底
 * 部署新内容时请把下方 CACHE 版本号 +1（如 ital-conv-v1 -> v2），旧缓存会自动清理。
 */
const CACHE = 'ital-conv-v1';
const PRECACHE = ['./', './index.html'];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(PRECACHE).catch(() => {}))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

function cachePut(cache, req, res) {
  if (res && res.ok && res.type !== 'error') {
    cache.put(req, res.clone());
  }
  return res;
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // 1) 音频：cache-first（内容哈希命名，可安全长期缓存）
  if (url.pathname.indexOf('/audio/') !== -1) {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE);
      const cached = await cache.match(req);
      if (cached) return cached;
      try {
        const res = await fetch(req);
        return cachePut(cache, req, res);
      } catch (err) {
        return cached || Response.error();
      }
    })());
    return;
  }

  // 2) 页面 HTML / 导航：network-first，断网回退缓存
  const isHtml = req.mode === 'navigate' ||
                 url.pathname.endsWith('/index.html') ||
                 url.pathname === '/' || url.pathname.endsWith('/');
  if (isHtml) {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE);
      try {
        const res = await fetch(req);
        return cachePut(cache, req, res);
      } catch (err) {
        const cached = await cache.match(req) ||
                       await cache.match('./index.html') ||
                       await cache.match('./');
        return cached || Response.error();
      }
    })());
    return;
  }

  // 3) 其它同源资源：network-first + 缓存兜底
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      const res = await fetch(req);
      return cachePut(cache, req, res);
    } catch (err) {
      return (await cache.match(req)) || Response.error();
    }
  })());
});
