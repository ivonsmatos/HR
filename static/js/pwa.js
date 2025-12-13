/**
 * PWA Client - Frontend PWA integration
 * Handles service worker registration, offline detection, and PWA interactions
 */

class WorksuitePWA {
  constructor() {
    this.swRegistration = null;
    this.deferredPrompt = null;
    this.isOnline = navigator.onLine;
    this.offlineQueue = [];

    this.init();
  }

  /**
   * Initialize PWA
   */
  async init() {
    console.log("[PWA] Initializing...");

    // Register service worker
    if ("serviceWorker" in navigator) {
      this.registerServiceWorker();
    }

    // Monitor online/offline status
    window.addEventListener("online", () => this.handleOnline());
    window.addEventListener("offline", () => this.handleOffline());

    // Capture install prompt
    window.addEventListener("beforeinstallprompt", (e) => {
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallPrompt();
    });

    // Handle app installed
    window.addEventListener("appinstalled", () => {
      console.log("[PWA] App installed!");
      this.deferredPrompt = null;
    });

    // Initialize UI updates
    await this.initializeUI();
  }

  /**
   * Register Service Worker
   */
  async registerServiceWorker() {
    try {
      console.log("[PWA] Registering service worker...");

      const registration = await navigator.serviceWorker.register(
        "/service-worker.js",
        {
          scope: "/",
        }
      );

      this.swRegistration = registration;
      console.log("[PWA] Service Worker registered successfully");

      // Check for updates periodically
      setInterval(() => {
        registration.update();
      }, 60000); // Check every 1 minute

      // Handle service worker updates
      registration.addEventListener("updatefound", () => {
        const newWorker = registration.installing;
        newWorker.addEventListener("statechange", () => {
          if (
            newWorker.state === "activated" &&
            navigator.serviceWorker.controller
          ) {
            this.notifyUpdate();
          }
        });
      });
    } catch (error) {
      console.error("[PWA] Service Worker registration failed:", error);
    }
  }

  /**
   * Handle online status
   */
  handleOnline() {
    console.log("[PWA] Online!");
    this.isOnline = true;

    // Update UI
    this.updateOnlineIndicator(true);

    // Sync offline queue
    if (this.offlineQueue.length > 0) {
      this.syncOfflineQueue();
    }

    // Trigger background sync
    if ("serviceWorker" in navigator && "SyncManager" in window) {
      navigator.serviceWorker.ready.then((registration) => {
        registration.sync.register("sync-offline-queue");
      });
    }
  }

  /**
   * Handle offline status
   */
  handleOffline() {
    console.log("[PWA] Offline!");
    this.isOnline = false;

    // Update UI
    this.updateOnlineIndicator(false);
  }

  /**
   * Update online indicator UI
   */
  updateOnlineIndicator(online) {
    const indicator = document.getElementById("online-indicator");
    if (!indicator) {
      this.createOnlineIndicator(online);
      return;
    }

    if (online) {
      indicator.classList.remove("offline");
      indicator.classList.add("online");
      indicator.textContent = "🟢 Online";
    } else {
      indicator.classList.remove("online");
      indicator.classList.add("offline");
      indicator.textContent = "🔴 Offline";
    }
  }

  /**
   * Create online indicator in DOM
   */
  createOnlineIndicator(online) {
    const indicator = document.createElement("div");
    indicator.id = "online-indicator";
    indicator.className = online ? "online" : "offline";
    indicator.textContent = online ? "🟢 Online" : "🔴 Offline";
    indicator.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: bold;
      z-index: 9999;
      background: ${online ? "#10b981" : "#ef4444"};
      color: white;
    `;
    document.body.appendChild(indicator);
  }

  /**
   * Show install prompt
   */
  showInstallPrompt() {
    const button = document.getElementById("install-app-btn");
    if (button) {
      button.style.display = "block";
      button.addEventListener("click", () => this.installApp());
    }
  }

  /**
   * Install PWA
   */
  async installApp() {
    if (!this.deferredPrompt) {
      console.warn("[PWA] Install prompt not available");
      return;
    }

    this.deferredPrompt.prompt();
    const choice = await this.deferredPrompt.userChoice;

    if (choice.outcome === "accepted") {
      console.log("[PWA] App installation accepted");
    } else {
      console.log("[PWA] App installation rejected");
    }

    this.deferredPrompt = null;
  }

  /**
   * Notify user of app update
   */
  notifyUpdate() {
    const container = document.getElementById("pwa-notification");
    if (!container) return;

    const notification = document.createElement("div");
    notification.className = "pwa-update-notification";
    notification.innerHTML = `
      <div style="display: flex; align-items: center; gap: 12px;">
        <span>🔄 Novo update disponível</span>
        <button id="update-app-btn" style="padding: 4px 12px; cursor: pointer;">
          Recarregar
        </button>
      </div>
    `;

    container.appendChild(notification);

    document.getElementById("update-app-btn").addEventListener("click", () => {
      window.location.reload();
    });
  }

  /**
   * Queue request while offline
   */
  queueRequest(method, url, data = null) {
    const request = {
      method,
      url,
      data,
      timestamp: new Date().toISOString(),
    };

    this.offlineQueue.push(request);
    this.saveOfflineQueueToStorage();

    console.log("[PWA] Request queued for later:", request);
  }

  /**
   * Sync offline queue
   */
  async syncOfflineQueue() {
    if (this.offlineQueue.length === 0) {
      console.log("[PWA] Offline queue is empty");
      return;
    }

    console.log("[PWA] Syncing offline queue...");

    const queue = [...this.offlineQueue];

    for (const request of queue) {
      try {
        const response = await fetch(request.url, {
          method: request.method,
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${this.getAuthToken()}`,
          },
          body: request.data ? JSON.stringify(request.data) : null,
        });

        if (response.ok) {
          // Remove from queue
          this.offlineQueue = this.offlineQueue.filter(
            (r) => r.timestamp !== request.timestamp
          );
          console.log("[PWA] Request synced successfully:", request.url);
        } else {
          console.warn("[PWA] Request failed with status:", response.status);
        }
      } catch (error) {
        console.error("[PWA] Failed to sync request:", error);
      }
    }

    this.saveOfflineQueueToStorage();
  }

  /**
   * Save offline queue to localStorage
   */
  saveOfflineQueueToStorage() {
    try {
      localStorage.setItem("worksuite-offline-queue", JSON.stringify(this.offlineQueue));
    } catch (error) {
      console.warn("[PWA] Failed to save offline queue:", error);
    }
  }

  /**
   * Load offline queue from localStorage
   */
  loadOfflineQueueFromStorage() {
    try {
      const stored = localStorage.getItem("worksuite-offline-queue");
      if (stored) {
        this.offlineQueue = JSON.parse(stored);
      }
    } catch (error) {
      console.warn("[PWA] Failed to load offline queue:", error);
    }
  }

  /**
   * Get authentication token
   */
  getAuthToken() {
    return localStorage.getItem("auth_token") || "";
  }

  /**
   * Initialize UI elements
   */
  async initializeUI() {
    // Update online indicator
    this.updateOnlineIndicator(this.isOnline);

    // Get PWA metadata from server
    try {
      const response = await fetch("/api/pwa/metadata/");
      const data = await response.json();
      console.log("[PWA] Metadata loaded:", data);
    } catch (error) {
      console.warn("[PWA] Failed to load metadata:", error);
    }
  }

  /**
   * Check if app is installed
   */
  isAppInstalled() {
    return (
      window.navigator.standalone === true ||
      window.matchMedia("(display-mode: standalone)").matches
    );
  }

  /**
   * Get display mode
   */
  getDisplayMode() {
    if (window.navigator.standalone) return "standalone";
    if (window.matchMedia("(display-mode: standalone)").matches) return "standalone";
    if (window.matchMedia("(display-mode: minimal-ui)").matches) return "minimal-ui";
    if (window.matchMedia("(display-mode: fullscreen)").matches) return "fullscreen";
    if (window.matchMedia("(display-mode: browser)").matches) return "browser";
    return "browser";
  }

  /**
   * Request notification permission
   */
  async requestNotificationPermission() {
    if (!("Notification" in window)) {
      console.warn("[PWA] Notifications not supported");
      return;
    }

    if (Notification.permission === "granted") {
      return;
    }

    if (Notification.permission !== "denied") {
      const permission = await Notification.requestPermission();
      if (permission === "granted") {
        console.log("[PWA] Notification permission granted");
      }
    }
  }

  /**
   * Send notification
   */
  sendNotification(title, options = {}) {
    if (Notification.permission === "granted") {
      if ("serviceWorker" in navigator && "ServiceWorkerContainer" in window) {
        navigator.serviceWorker.ready.then((registration) => {
          registration.showNotification(title, {
            icon: "/static/images/icons/icon-192x192.png",
            badge: "/static/images/icons/icon-96x96.png",
            ...options,
          });
        });
      } else {
        new Notification(title, options);
      }
    }
  }
}

// Initialize PWA on DOM ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    window.workSuitePWA = new WorksuitePWA();
  });
} else {
  window.workSuitePWA = new WorksuitePWA();
}

// Export for module systems
if (typeof module !== "undefined" && module.exports) {
  module.exports = WorksuitePWA;
}
