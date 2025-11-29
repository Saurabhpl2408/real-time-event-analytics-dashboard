/**
 * Core Tracker Engine
 * Handles event tracking, session management, and API communication
 */

class CoreTracker {
  constructor(config) {
    this.config = config;
    this.sessionId = null;
    this.userId = null;
    this.pageLoadTime = Date.now();
    this.eventQueue = [];
    this.apiUrl = config.apiUrl;
    this.schemaId = config.schemaId;
    this.containerId = config.containerId;
  }

  /**
   * Initialize tracker
   */
  init() {
    this.initSession();
    this.log('Tracker initialized', this.config);
  }

  /**
   * Initialize or restore session
   */
  initSession() {
    const stored = this.getStorage('cap_session');
    const now = Date.now();

    if (stored && stored.expires > now) {
      this.sessionId = stored.sessionId;
      this.userId = stored.userId;
    } else {
      this.sessionId = this.generateId();
      this.userId = this.getOrCreateUserId();
    }

    // Save session with 30min expiry
    this.setStorage('cap_session', {
      sessionId: this.sessionId,
      userId: this.userId,
      expires: now + (30 * 60 * 1000)
    });

    this.log('Session initialized', {
      sessionId: this.sessionId,
      userId: this.userId
    });
  }

  /**
   * Get or create persistent user ID
   */
  getOrCreateUserId() {
    let userId = this.getStorage('cap_user_id');
    
    if (!userId) {
      userId = this.generateId();
      this.setStorage('cap_user_id', userId, 365 * 24 * 60 * 60 * 1000);
    }

    return userId;
  }

  /**
   * Generate unique ID
   */
  generateId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  /**
   * Track event
   */
  track(eventType, properties = {}) {
    const event = {
      schema_id: this.schemaId,
      event_type: eventType,
      properties: {
        ...properties,
        container_id: this.containerId
      },
      user_id: this.userId,
      session_id: this.sessionId,
      timestamp: new Date().toISOString(),
      metadata: {
        user_agent: navigator.userAgent,
        screen_width: window.screen.width,
        screen_height: window.screen.height,
        viewport_width: window.innerWidth,
        viewport_height: window.innerHeight,
        language: navigator.language,
        platform: navigator.platform,
        referrer: document.referrer || null
      }
    };

    this.sendEvent(event);
  }

  /**
   * Send event to backend
   */
  sendEvent(event) {
    const url = `${this.apiUrl}/api/events/ingest`;

    // Use sendBeacon for page unload events
    if (event.event_type === 'page_duration' && navigator.sendBeacon) {
      const blob = new Blob([JSON.stringify(event)], { type: 'application/json' });
      navigator.sendBeacon(url, blob);
      this.log('Event sent (beacon)', event);
      return;
    }

    // Use fetch for other events
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(event),
      keepalive: true
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      this.log('Event sent successfully', { eventType: event.event_type, data });
    })
    .catch(error => {
      console.error('[CustomAnalytics] Failed to send event:', error);
      this.queueEvent(event);
    });
  }

  /**
   * Queue failed events for retry
   */
  queueEvent(event) {
    this.eventQueue.push(event);
    
    // Retry after 5 seconds
    setTimeout(() => {
      if (this.eventQueue.length > 0) {
        const queuedEvent = this.eventQueue.shift();
        this.sendEvent(queuedEvent);
      }
    }, 5000);
  }

  /**
   * Identify user
   */
  identify(userId, traits = {}) {
    this.userId = userId;
    this.setStorage('cap_user_id', userId, 365 * 24 * 60 * 60 * 1000);
    
    this.track('identify', {
      user_id: userId,
      traits: traits
    });

    this.log('User identified', { userId, traits });
  }

  /**
   * Storage helpers
   */
  setStorage(key, value, maxAge) {
    try {
      const data = {
        value: value,
        expires: maxAge ? Date.now() + maxAge : null
      };
      localStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
      this.log('localStorage not available', e);
    }
  }

  getStorage(key) {
    try {
      const item = localStorage.getItem(key);
      if (!item) return null;

      const data = JSON.parse(item);
      if (data.expires && data.expires < Date.now()) {
        localStorage.removeItem(key);
        return null;
      }

      return data.value;
    } catch (e) {
      return null;
    }
  }

  /**
   * Debug logging
   */
  log(...args) {
    if (this.config.debug) {
      console.log('[CustomAnalytics]', ...args);
    }
  }
}

// Export for use in container
window.CoreTracker = CoreTracker;