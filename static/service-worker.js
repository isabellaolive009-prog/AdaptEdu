const CACHE_NAME = "adaptedu-static-v1";
const ARQUIVOS = [
  "/static/style.css",
  "/static/manifest.json",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
  "/static/icons/icon-512-maskable.png",
  "/static/offline.html"
];

self.addEventListener("install", (evento) => {
  evento.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ARQUIVOS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (evento) => {
  evento.waitUntil(
    caches.keys().then((nomes) =>
      Promise.all(nomes.filter((nome) => nome !== CACHE_NAME).map((nome) => caches.delete(nome)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (evento) => {
  const url = new URL(evento.request.url);

  // Não armazena páginas com login, dados de professores ou publicações.
  if (evento.request.method !== "GET" || url.origin !== self.location.origin) return;

  if (url.pathname.startsWith("/static/")) {
    evento.respondWith(
      caches.match(evento.request).then((resposta) =>
        resposta || fetch(evento.request).then((rede) => {
          if (rede.ok) {
            const copia = rede.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(evento.request, copia));
          }
          return rede;
        })
      )
    );
    return;
  }

  if (evento.request.mode === "navigate") {
    evento.respondWith(
      fetch(evento.request).catch(() => caches.match("/static/offline.html"))
    );
  }
});
