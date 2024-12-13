const CACHE_NAME = 'static-v1';
const STATIC_FILES = [
    '/',
    '/static/js/dashboard.js',
    '/static/images/logowhitebg.png',
    // Add other necessary files
];

self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installing Service Worker...', event);
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[Service Worker] Caching App Shell');
            return cache.addAll(STATIC_FILES).catch((error) => {
                console.error('[Service Worker] Failed to cache:', error);
            });
        })
    );
});

self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Activating Service Worker...', event);
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        console.log('[Service Worker] Removing old cache:', cache);
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', (event) => {
    console.log('[Service Worker] Fetching:', event.request.url);
    event.respondWith(
        caches.match(event.request).then((response) => {
            if (response) {
                console.log('[Service Worker] Serving from cache:', event.request.url);
                return response;
            }
            console.log('[Service Worker] Fetching from network:', event.request.url);
            return fetch(event.request)
                .then((response) => {
                    if (event.request.url.startsWith('http')) {
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, response.clone());
                        });
                    }
                    return response;
                })
                .catch((error) => {
                    console.error('[Service Worker] Fetch failed:', error);
                   
                });
        })
    );
});
