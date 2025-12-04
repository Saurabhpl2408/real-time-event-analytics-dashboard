/**
 * Portfolio Adaptor - Saurabh Lohokare
 * Optimized version with single click listener
 * Custom tracking for https://saurabh-lohokare-portfolio.vercel.app
 */

(function() {
  'use strict';

  console.log('[Portfolio Adaptor] Initializing for Saurabh Lohokare Portfolio...');

  function getInnerText(element) {
    if (!element) return '';
    return (element.innerText || element.textContent || '').trim();
  }

  function trackEvent(eventType, properties = {}) {
    const standardProps = {
      ...properties,
      tracked_at: new Date().toISOString(),
      page_url: window.location.href,
      page_path: window.location.pathname
    };

    if (window.CustomAnalytics) {
      window.CustomAnalytics.track(eventType, standardProps);
      console.log(`[Portfolio Adaptor] ✓ ${eventType}`, standardProps);
    }
  }

  function extractGitHubInfo(href) {
    if (!href || !href.includes('github.com/')) {
      return null;
    }

    const parts = href.split('github.com/')[1]?.split('/').filter(p => p);
    
    if (!parts || parts.length === 0) return null;

    return {
      username: parts[0] || null,
      projectName: parts[1] || null,
      isProject: parts.length >= 2
    };
  }

  function handleClick(e) {
    const target = e.target.closest('a') || e.target;
    const href = target.getAttribute('href') || '';
    const linkText = getInnerText(target);
    const elementId = target.id || null;
    const elementClass = target.className || null;
    const tagName = target.tagName;
    const lowerHref = href.toLowerCase();

    if (tagName !== 'A') return;

    switch (true) {
      case href.startsWith('mailto:'):
        trackEvent('email_link_click', {
          email_address: href.replace('mailto:', ''),
          link_text: linkText,
          element_id: elementId,
          element_class: elementClass
        });
        break;

      case href.startsWith('tel:'):
        trackEvent('contact_number_click', {
          phone_number: href.replace('tel:', ''),
          link_text: linkText,
          element_id: elementId,
          element_class: elementClass
        });
        break;

      case (href === '#contact' && linkText.toLowerCase() === 'get in touch'):
        trackEvent('get_in_touch_click', {
          button_text: linkText,
          target_section: 'contact',
          element_id: elementId
        });
        break;

      case href === './Saurabh_Lohokare_Resume.pdf':
      case lowerHref.includes('resume.pdf'):
        trackEvent('resume_download_click', {
          file_name: href.split('/').pop() || 'Saurabh_Lohokare_Resume.pdf',
          button_text: linkText,
          element_id: elementId,
          element_class: elementClass
        });
        break;

      case lowerHref.includes('recommendations'):
        trackEvent('recommendation_link_click', {
          recommendation_url: href,
          link_text: linkText,
          platform: 'LinkedIn',
          element_id: elementId
        });
        break;

      case lowerHref.includes('linkedin'):
        trackEvent('linkedin_profile_click', {
          linkedin_url: href,
          link_text: linkText,
          element_id: elementId,
          element_class: elementClass
        });
        break;

      case lowerHref.includes('ijcrt'):
        trackEvent('publication_link_click', {
          publication_type: 'IJCRT',
          publication_url: href,
          link_text: linkText,
          element_id: elementId
        });
        break;

      case lowerHref.includes('github.com/'):
        const githubInfo = extractGitHubInfo(href);
        
        if (githubInfo) {
          if (githubInfo.isProject) {
            trackEvent('github_project_click', {
              github_username: githubInfo.username,
              project_name: githubInfo.projectName,
              project_url: href,
              link_text: linkText,
              element_id: elementId,
              element_class: elementClass
            });
          } else {
            trackEvent('github_profile_click', {
              github_username: githubInfo.username,
              github_url: href,
              link_text: linkText,
              element_id: elementId
            });
          }
        }
        break;

      case href.startsWith('#'):
        trackEvent('navigation_click', {
          section_name: href.substring(1),
          link_text: linkText,
          navigation_type: 'internal'
        });
        break;

      default:
        if (href.startsWith('http') && !href.includes(window.location.hostname)) {
          trackEvent('external_link_click', {
            link_url: href,
            link_text: linkText,
            element_id: elementId
          });
        }
        break;
    }
  }

  let maxScrollDepth = 0;
  const scrollMilestones = [25, 50, 75, 100];
  const trackedMilestones = {};

  function handleScroll() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    const scrollPercent = Math.round(((scrollTop + windowHeight) / documentHeight) * 100);
    
    if (scrollPercent > maxScrollDepth) {
      maxScrollDepth = scrollPercent;
      
      scrollMilestones.forEach(function(milestone) {
        if (maxScrollDepth >= milestone && !trackedMilestones[milestone]) {
          trackedMilestones[milestone] = true;
          
          trackEvent('scroll_depth', {
            depth_percent: milestone,
            page: window.location.pathname
          });
        }
      });
    }
  }

  let pageLoadTime = Date.now();

  function handlePageDuration() {
    const timeSpent = Math.round((Date.now() - pageLoadTime) / 1000);
    
    if (timeSpent > 5) {
      trackEvent('page_duration', {
        duration_seconds: timeSpent,
        page: window.location.pathname,
        page_title: document.title
      });
    }
  }

  function initializeTracking() {
    console.log('[Portfolio Adaptor] Setting up centralized event listener...');

    document.addEventListener('click', handleClick, true);

    let scrollTimeout;
    window.addEventListener('scroll', function() {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(handleScroll, 300);
    });

    window.addEventListener('beforeunload', handlePageDuration);
    
    document.addEventListener('visibilitychange', function() {
      if (document.visibilityState === 'hidden') {
        handlePageDuration();
      }
    });

    console.log('[Portfolio Adaptor] ✅ Tracking initialized');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTracking);
  } else {
    if (window.CoreTracker) {
      initializeTracking();
    } else {
      setTimeout(initializeTracking, 500);
    }
  }

})();