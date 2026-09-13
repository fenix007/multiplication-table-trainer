// Service worker: кэширует приложение целиком, чтобы оно открывалось без сети.
const CACHE = 'tablica-v1';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon.svg',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png'
];

self.addEventListener('install', e => {
  // Кэшируем по одному: отсутствие какой-то иконки не должно ломать установку офлайн-режима.
  e.waitUntil(
    caches.open(CACHE).then(c => Promise.all(
      ASSETS.map(a => fetch(a).then(r => { if (r.ok) return c.put(a, r); }).catch(() => {}))
    )).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Свои файлы: сначала сеть (чтобы подхватывать обновления), при её отсутствии — кэш.
// Шрифты Google: сначала кэш, потом сеть; без сети страница просто использует системный шрифт.
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  if (url.origin === location.origin) {
    e.respondWith(
      fetch(e.request).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
        return res;
      }).catch(() => caches.match(e.request).then(r => r || caches.match('./index.html')))
    );
  } else if (url.hostname.endsWith('gstatic.com') || url.hostname.endsWith('googleapis.com')) {
    e.respondWith(
      caches.match(e.request).then(r => r || fetch(e.request).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
        return res;
      }).catch(() => new Response('', { status: 503 })))
    );
  }
});
