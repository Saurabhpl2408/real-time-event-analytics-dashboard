/**
 * Portfolio Adaptor - Saurabh Lohokare
 * Click tracking only - no scroll tracking
 */

(function() {
  'use strict';

  console.log('[Portfolio Adaptor] Initializing...');

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
    if (!href || !href.includes('github.com/')) return null;
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

  function initializeTracking() {
    console.log('[Portfolio Adaptor] Setting up click tracking...');
    document.addEventListener('click', handleClick, true);
    console.log('[Portfolio Adaptor] ✅ Click tracking active (no scroll tracking)');
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