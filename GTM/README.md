# Tag Manager

Custom analytics tag manager with adaptor system.

## Structure

- **core/** - Core tracking engine and container loader
- **adaptors/** - Pre-built adaptors for different website types

## Adaptors

### Portfolio Adaptor
Tracks:
- Project clicks
- External links (LinkedIn, GitHub, Resume)
- Skills interactions
- Contact form
- Scroll depth

### E-commerce Adaptor
Tracks:
- Product views
- Add to cart
- Checkout started

### Blog Adaptor
Tracks:
- Article read time
- Comments
- Social shares

## Creating Custom Adaptors

See examples in `adaptors/` folder. Each adaptor should:
1. Use `window.CustomAnalytics.track()` for events
2. Match event types defined in your schema
3. Include error handling
4. Log initialization for debugging