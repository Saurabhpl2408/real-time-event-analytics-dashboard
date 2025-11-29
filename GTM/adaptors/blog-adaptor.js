/**
 * Blog Adaptor Template
 * For tracking article reads, comments, shares
 */

(function() {
  'use strict';

  console.log('[Blog Adaptor] Initializing...');

  // Track article read time
  let articleStartTime = Date.now();
  
  function trackReadTime() {
    const readTime = Math.round((Date.now() - articleStartTime) / 1000);
    
    window.CustomAnalytics.track('article_read', {
      article_title: document.title,
      article_url: window.location.href,
      read_time_seconds: readTime,
      words_count: document.body.textContent.split(/\s+/).length
    });
  }

  // Track comments
  function trackComments() {
    const commentForms = document.querySelectorAll('form[class*="comment"]');
    
    commentForms.forEach(function(form) {
      form.addEventListener('submit', function() {
        window.CustomAnalytics.track('comment_submitted', {
          article_title: document.title,
          article_url: window.location.href
        });
      });
    });
  }

  // Track social shares
  function trackShares() {
    const shareButtons = document.querySelectorAll('[class*="share"], [data-action="share"]');
    
    shareButtons.forEach(function(button) {
      button.addEventListener('click', function() {
        window.CustomAnalytics.track('article_shared', {
          article_title: document.title,
          share_platform: button.getAttribute('data-platform') || 'unknown'
        });
      });
    });
  }

  // Initialize
  function init() {
    trackComments();
    trackShares();
    
    // Track read time on page exit
    window.addEventListener('beforeunload', trackReadTime);
    
    console.log('[Blog Adaptor] ✅ Tracking initialized');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();