/**
 * Portfolio Adaptor
 * Specifically designed for tracking portfolio websites
 * URL: https://saurabh-lohokare-portfolio.vercel.app/
 */

(function() {
  'use strict';

  console.log('[Portfolio Adaptor] Initializing...');

  // Track project clicks
  function trackProjectClicks() {
    // Find all project links/cards
    const projectElements = document.querySelectorAll('[class*="project"], [class*="Project"], a[href*="/project"], a[href*="github.com"]');
    
    projectElements.forEach(function(element) {
      element.addEventListener('click', function(e) {
        const projectName = element.getAttribute('data-project') || 
                          element.getAttribute('title') || 
                          element.textContent.trim().substring(0, 50);
        
        const projectUrl = element.href || element.getAttribute('data-url') || '';

        window.CustomAnalytics.track('project_click', {
          project_name: projectName,
          project_url: projectUrl,
          element_id: element.id || null,
          page_section: getPageSection(element)
        });

        console.log('[Portfolio Adaptor] Project clicked:', projectName);
      });
    });
  }

  // Track external link clicks (LinkedIn, GitHub, Resume, etc.)
  function trackExternalLinks() {
    const externalLinks = document.querySelectorAll('a[href*="linkedin.com"], a[href*="github.com"], a[href*=".pdf"], a[href^="mailto:"]');
    
    externalLinks.forEach(function(link) {
      link.addEventListener('click', function(e) {
        let linkType = 'external';
        const href = link.href.toLowerCase();

        if (href.includes('linkedin.com')) {
          linkType = 'linkedin';
        } else if (href.includes('github.com')) {
          linkType = 'github';
        } else if (href.includes('.pdf') || link.textContent.toLowerCase().includes('resume')) {
          linkType = 'resume';
        } else if (href.startsWith('mailto:')) {
          linkType = 'email';
        }

        window.CustomAnalytics.track('link_click', {
          link_type: linkType,
          link_url: link.href,
          link_text: link.textContent.trim().substring(0, 50)
        });

        console.log('[Portfolio Adaptor] External link clicked:', linkType);
      });
    });
  }

  // Track skills/tech stack interactions
  function trackSkillInteractions() {
    const skillElements = document.querySelectorAll('[class*="skill"], [class*="tech"], [class*="tag"]');
    
    skillElements.forEach(function(skill) {
      skill.addEventListener('click', function() {
        window.CustomAnalytics.track('skill_interaction', {
          skill_name: skill.textContent.trim(),
          skill_category: skill.getAttribute('data-category') || 'uncategorized'
        });
      });
    });
  }

  // Track contact form interactions
  function trackContactForm() {
    const contactForms = document.querySelectorAll('form[class*="contact"], form#contact, form[action*="contact"]');
    
    contactForms.forEach(function(form) {
      const inputs = form.querySelectorAll('input, textarea');
      
      inputs.forEach(function(input) {
        input.addEventListener('focus', function() {
          window.CustomAnalytics.track('contact_form', {
            action: 'focus',
            field: input.name || input.id || 'unknown',
            form_id: form.id || 'contact'
          });
        });
      });

      form.addEventListener('submit', function() {
        window.CustomAnalytics.track('contact_form', {
          action: 'submit',
          form_id: form.id || 'contact'
        });
      });
    });
  }

  // Track scroll depth
  let maxScrollDepth = 0;
  function trackScrollDepth() {
    const scrollDepth = Math.round((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight * 100);
    
    if (scrollDepth > maxScrollDepth) {
      maxScrollDepth = scrollDepth;
      
      // Track at 25%, 50%, 75%, 100% milestones
      if ([25, 50, 75, 100].includes(maxScrollDepth)) {
        window.CustomAnalytics.track('scroll_depth', {
          depth_percent: maxScrollDepth,
          page: window.location.pathname
        });
      }
    }
  }

  // Get page section from element position
  function getPageSection(element) {
    const rect = element.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    
    if (rect.top < viewportHeight * 0.33) {
      return 'top';
    } else if (rect.top < viewportHeight * 0.66) {
      return 'middle';
    } else {
      return 'bottom';
    }
  }

  // Initialize all trackers
  function init() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function() {
        setupTracking();
      });
    } else {
      setupTracking();
    }
  }

  function setupTracking() {
    trackProjectClicks();
    trackExternalLinks();
    trackSkillInteractions();
    trackContactForm();
    
    // Scroll tracking with throttle
    let scrollTimeout;
    window.addEventListener('scroll', function() {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(trackScrollDepth, 500);
    });

    console.log('[Portfolio Adaptor] ✅ All tracking initialized');
  }

  // Start
  init();

})();