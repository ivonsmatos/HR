/**
 * Service Worker for Worksuite Clone PWA
 * Handles offline support, caching, and background sync
 */

const CACHE_PREFIX = "worksuite-cache";
const CACHE_VERSION = "v1";
const CACHE_NAME = `${CACHE_PREFIX}-${CACHE_VERSION}`;

// Static assets to cache on install
const STATIC_ASSETS = [
  "/",
  "/static/css/style.css",
  "/static/js/app.js",
  "/static/js/pwa.js",
  "/offline/",
  "/api/pwa/metadata/",
];

// API endpoints that should be cached
const API_CACHE_ROUTES = [
  "/api/v1/core/users/",
  "/api/v1/core/companies/",
  "/api/v1/hrm/employees/",
  "/api/v1/work/projects/",
  "/api/v1/finance/invoices/",
  "/api/v1/crm/clients/",
];

// Install event - cache essential files
self.addEventListener("install", (event) => {
  console.log("[Service Worker] Installing...");

  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[Service Worker] Caching static assets");
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn("[Service Worker] Failed to cache some assets:", err);
      });
    })
  );

  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  console.log("[Service Worker] Activating...");

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (
            cacheName.startsWith(CACHE_PREFIX) &&
            cacheName !== CACHE_NAME
          ) {
            console.log("[Service Worker] Deleting old cache:", cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );

  self.clients.claim();
});

// Fetch event - implement network-first or cache-first strategy
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip cross-origin requests
  if (url.origin !== self.location.origin) {
    return;
  }

  // Skip non-GET requests
  if (request.method !== "GET") {
    return;
  }

  // HTML pages - Network first, fall back to cache
  if (request.headers.get("accept")?.includes("text/html")) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // API requests - Cache first (if available), fall back to network
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(cacheFirstStrategy(request));
    return;
  }

  // Static assets - Cache first
  if (
    url.pathname.match(
      /\.(js|css|png|jpg|jpeg|svg|gif|webp|woff|woff2|ttf|eot)$/
    )
  ) {
    event.respondWith(cacheFirstStrategy(request));
    return;
  }

  // Default - Network first
  event.respondWith(networkFirstStrategy(request));
});

/**
 * Network first strategy
 * Try network first, fall back to cache, then offline page
 */
function networkFirstStrategy(request) {
  return fetch(request)
    .then((response) => {
      // Cache successful responses
      if (response.status === 200) {
        const cache = caches.open(CACHE_NAME);
        cache.then((c) => c.put(request, response.clone()));
      }
      return response;
    })
    .catch(() => {
      // Try cache on network failure
      return caches
        .match(request)
        .then((response) => {
          if (response) {
            return response;
          }

          // Return offline page for HTML requests
          if (request.headers.get("accept")?.includes("text/html")) {
            return caches.match("/offline/");
          }

          // Return offline JSON response for API requests
          if (request.url.includes("/api/")) {
            return new Response(
              JSON.stringify({
                status: "offline",
                error: "Network unavailable",
              }),
              {
                status: 503,
                headers: { "Content-Type": "application/json" },
              }
            );
          }

          return new Response("Offline - Resource not available", {
            status: 503,
          });
        })
        .catch(() => {
          // Final fallback
          return new Response("Offline - Service Worker Error", {
            status: 503,
          });
        });
    });
}

/**
 * Cache first strategy
 * Try cache first, fall back to network
 */
function cacheFirstStrategy(request) {
  return caches
    .match(request)
    .then((response) => {
      if (response) {
        // Return from cache but update in background
        updateCacheInBackground(request);
        return response;
      }

      // Not in cache, try network
      return fetch(request)
        .then((response) => {
          // Cache successful responses
          if (response.status === 200) {
            const cache = caches.open(CACHE_NAME);
            cache.then((c) => c.put(request, response.clone()));
          }
          return response;
        })
        .catch(() => {
          // Return offline response
          return new Response(
            JSON.stringify({
              status: "offline",
              error: "Resource not available offline",
            }),
            {
              status: 503,
              headers: { "Content-Type": "application/json" },
            }
          );
        });
    });
}

/**
 * Update cache in background
 * Fetch new data and update cache without blocking response
 */
function updateCacheInBackground(request) {
  return fetch(request).then((response) => {
    if (response.status === 200) {
      caches.open(CACHE_NAME).then((cache) => {
        cache.put(request, response.clone());
        // Notify all clients of update
        self.clients.matchAll().then((clients) => {
          clients.forEach((client) => {
            client.postMessage({
              type: "CACHE_UPDATED",
              url: request.url,
            });
          });
        });
      });
    }
  });
}

// Background Sync for offline actions
self.addEventListener("sync", (event) => {
  console.log("[Service Worker] Background sync event:", event.tag);

  if (event.tag === "sync-offline-queue") {
    event.waitUntil(syncOfflineQueue());
  }
});

/**
 * Sync offline queue
 * Send queued requests when connection is restored
 */
function syncOfflineQueue() {
  return openDB().then((db) => {
    const objectStore = db
      .transaction("offline-queue", "readonly")
      .objectStore("offline-queue");
    return objectStore.getAll();
  });
}

/**
 * Open IndexedDB for offline storage
 */
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("WorsuiteDB", 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains("offline-queue")) {
        db.createObjectStore("offline-queue", {
          keyPath: "id",
          autoIncrement: true,
        });
      }
      if (!db.objectStoreNames.contains("sync-logs")) {
        db.createObjectStore("sync-logs", { keyPath: "id", autoIncrement: true });
      }
    };
  });
}

// Handle messages from clients
self.addEventListener("message", (event) => {
  console.log("[Service Worker] Message received:", event.data);

  if (event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }

  if (event.data.type === "CLEAR_CACHE") {
    caches.delete(CACHE_NAME);
  }

  if (event.data.type === "CACHE_FIRST_URL") {
    const request = new Request(event.data.url);
    caches.open(CACHE_NAME).then((cache) => {
      cache.add(request);
    });
  }
});
