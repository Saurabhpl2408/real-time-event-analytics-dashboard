/**
 * Container Template
 * Backend will replace {{PLACEHOLDERS}} with actual values
 */

(function(window, document) {
  'use strict';

  // Container Configuration
  const CONTAINER_CONFIG = {
    containerId: "PLACEHOLDER_CONTAINER_ID",
    schemaId: "PLACEHOLDER_SCHEMA_ID",
    apiUrl: "PLACEHOLDER_API_URL",
    trackingRules: PLACEHOLDER_TRACKING_RULES,
    debug: PLACEHOLDER_DEBUG
  };

  // Load Core Tracker
  const tracker = new window.CoreTracker(CONTAINER_CONFIG);
  tracker.init();

  // Auto-tracking setup
  if (CONTAINER_CONFIG.trackingRules.auto_page_view) {
    tracker.track('page_view', {
      page: window.location.pathname,
      page_title: document.title,
      page_url: window.location.href
    });
  }

  if (CONTAINER_CONFIG.trackingRules.track_clicks) {
    document.addEventListener('click', function(e) {
      const element = e.target;
      const tagName = element.tagName.toLowerCase();

      if (tagName === 'button' || element.getAttribute('role') === 'button') {
        tracker.track('click', {
          element_type: 'button',
          element_id: element.id || null,
          element_class: element.className || null,
          element_text: (element.textContent || '').trim().substring(0, 100),
          page: window.location.pathname
        });
      } else if (tagName === 'a') {
        tracker.track('click', {
          element_type: 'link',
          element_id: element.id || null,
          element_text: (element.textContent || '').trim().substring(0, 100),
          link_url: element.href,
          page: window.location.pathname
        });
      }
    }, true);
  }

  if (CONTAINER_CONFIG.trackingRules.track_forms) {
    document.addEventListener('submit', function(e) {
      const form = e.target;
      tracker.track('form_submit', {
        form_id: form.id || null,
        form_name: form.name || null,
        form_action: form.action || null,
        page: window.location.pathname
      });
    }, true);
  }

  window.addEventListener('beforeunload', function() {
    const duration = Math.round((Date.now() - tracker.pageLoadTime) / 1000);
    tracker.track('page_duration', {
      page: window.location.pathname,
      duration_seconds: duration
    });
  });

  // Expose tracker
  window.CustomAnalytics = {
    track: function(eventType, properties) {
      tracker.track(eventType, properties);
    },
    identify: function(userId, traits) {
      tracker.identify(userId, traits);
    }
  };

  // Custom adaptor code
  PLACEHOLDER_CUSTOM_CODE

})(window, document);