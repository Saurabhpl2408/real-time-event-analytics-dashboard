/**
 * E-commerce Adaptor Template
 * For tracking product views, cart actions, purchases
 */

(function() {
  'use strict';

  console.log('[E-commerce Adaptor] Initializing...');

  // Track product views
  function trackProductViews() {
    const productElements = document.querySelectorAll('[data-product-id], [class*="product-card"], [class*="product-item"]');
    
    productElements.forEach(function(element) {
      // Track when product comes into view
      const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            window.CustomAnalytics.track('product_view', {
              product_id: element.getAttribute('data-product-id') || element.id,
              product_name: element.getAttribute('data-product-name') || element.textContent.trim().substring(0, 100),
              product_category: element.getAttribute('data-category'),
              price: element.getAttribute('data-price')
            });
            
            observer.unobserve(element);
          }
        });
      }, { threshold: 0.5 });

      observer.observe(element);
    });
  }

  // Track add to cart
  function trackAddToCart() {
    const cartButtons = document.querySelectorAll('[class*="add-to-cart"], button[data-action="add-cart"]');
    
    cartButtons.forEach(function(button) {
      button.addEventListener('click', function() {
        window.CustomAnalytics.track('add_to_cart', {
          product_id: button.getAttribute('data-product-id'),
          product_name: button.getAttribute('data-product-name'),
          quantity: button.getAttribute('data-quantity') || 1,
          price: button.getAttribute('data-price')
        });
      });
    });
  }

  // Track checkout
  function trackCheckout() {
    const checkoutButtons = document.querySelectorAll('[class*="checkout"], button[data-action="checkout"]');
    
    checkoutButtons.forEach(function(button) {
      button.addEventListener('click', function() {
        window.CustomAnalytics.track('checkout_started', {
          page: window.location.pathname
        });
      });
    });
  }

  // Initialize
  function init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function() {
        trackProductViews();
        trackAddToCart();
        trackCheckout();
        console.log('[E-commerce Adaptor] ✅ Tracking initialized');
      });
    } else {
      trackProductViews();
      trackAddToCart();
      trackCheckout();
      console.log('[E-commerce Adaptor] ✅ Tracking initialized');
    }
  }

  init();

})();