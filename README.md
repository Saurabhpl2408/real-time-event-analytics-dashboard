# Custom Analytics Platform

> Schema-driven, multi-adaptor analytics platform with Grafana visualization

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation

1. **Clone Repository**
```bash
git clone <your-repo>
cd custom-analytics-platform
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env if needed (defaults work fine)
```

3. **Start All Services**
```bash
docker-compose up -d
```

4. **Wait for Services (30 seconds)**
```bash
docker-compose ps
# All services should show "Up"
```

### 🌐 Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Admin Dashboard** | http://localhost:3000 | - |
| **Grafana Analytics** | http://localhost:3001 | admin/admin123 |
| **Postgres** | localhost:5432 | analytics/analytics123 |

---

## 📊 Track Your First Website (Portfolio Example)

### Step 1: Create Schema
```bash
curl -X POST http://localhost:8000/api/schemas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "portfolio",
    "description": "Portfolio website tracking",
    "properties": {
      "profile_view": {
        "page": "string",
        "referrer": "string"
      },
      "project_click": {
        "project_name": "string",
        "project_url": "string"
      },
      "link_click": {
        "link_type": "string",
        "link_url": "string"
      }
    }
  }'
```

### Step 2: Create Adaptor
```bash
curl -X POST http://localhost:8000/api/adaptors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "portfolio",
    "schema_id": "portfolio",
    "website_url": "https://saurabh-lohokare-portfolio.vercel.app",
    "tracking_rules": {
      "auto_page_view": true,
      "track_clicks": true,
      "track_forms": false
    }
  }'
```

Response will include `container_id`.

### Step 3: Add Tracking to Website

Add this to your website's `<head>` section:
```html
<script src="http://localhost:8000/tag/{CONTAINER_ID}.js" async></script>
```

### Step 4: View Analytics

Open Grafana: http://localhost:3001
- Username: `admin`
- Password: `admin123`
- Navigate to: Dashboards → Portfolio Analytics

---

## 🏗️ Architecture
```
Website → Tag Manager Container → Backend API → Kafka → PostgreSQL → Grafana
```

### Data Flow
1. User interacts with website
2. Tag Manager adaptor captures event
3. Event validated against schema
4. Sent to backend API
5. Processed by Kafka
6. Stored in PostgreSQL (schema-specific table)
7. Visualized in Grafana

---

## 🔧 Configuration

### Environment Variables

Edit `.env` file:
```env
# Database
POSTGRES_USER=analytics
POSTGRES_PASSWORD=analytics123
POSTGRES_DB=analytics_db

# Backend
BACKEND_PORT=8000

# Grafana
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=admin123

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

### Custom Schemas

Schemas define what data you track. Create via API or Admin Dashboard.

**Example Schema:**
```json
{
  "name": "ecommerce",
  "properties": {
    "product_view": {
      "product_id": "string",
      "product_name": "string",
      "price": "number",
      "category": "string"
    },
    "add_to_cart": {
      "product_id": "string",
      "quantity": "number"
    },
    "purchase": {
      "order_id": "string",
      "total_amount": "number",
      "items": "array"
    }
  }
}
```

### Custom Adaptors

Adaptors contain tracking logic for specific website types.

**Example: E-commerce Adaptor**
```javascript
// Tracks product clicks
document.querySelectorAll('.product-card').forEach(el => {
  el.addEventListener('click', function() {
    track('product_view', {
      product_id: this.dataset.productId,
      product_name: this.dataset.productName,
      price: this.dataset.price
    });
  });
});
```

---

## 📊 Pre-built Dashboards

### Portfolio Dashboard
Tracks:
- Page views by section
- Project clicks (which projects are popular)
- External link clicks (LinkedIn, GitHub, Resume)
- Geographic distribution
- Device types
- Session duration

### E-commerce Dashboard (Example)
Tracks:
- Product views
- Add to cart rate
- Purchase funnel
- Revenue metrics
- Top products

---

## 🛠️ Development

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f kafka
```

### Database Access
```bash
docker exec -it postgres psql -U analytics -d analytics_db
```

### Restart Services
```bash
# Restart specific service
docker-compose restart backend

# Rebuild after code changes
docker-compose build backend
docker-compose up -d backend
```

---

## 📚 API Documentation

### Events API

**POST /api/events/ingest**
```json
{
  "schema_id": "portfolio",
  "event_type": "project_click",
  "properties": {
    "project_name": "AI Chatbot",
    "project_url": "/projects/ai-chatbot"
  },
  "user_id": "user_123",
  "session_id": "session_456",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Schemas API

**GET /api/schemas** - List all schemas
**POST /api/schemas** - Create schema
**GET /api/schemas/{id}** - Get schema
**PUT /api/schemas/{id}** - Update schema
**DELETE /api/schemas/{id}** - Delete schema

### Adaptors API

**GET /api/adaptors** - List adaptors
**POST /api/adaptors** - Create adaptor
**GET /api/adaptors/{id}** - Get adaptor
**GET /tag/{container_id}.js** - Get tracking script

---

## 🔍 Monitoring

### Health Checks
```bash
# Backend
curl http://localhost:8000/health

# Database
docker exec postgres pg_isready

# Kafka
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Metrics
- Event processing rate
- Database size
- API response times
- Error rates

---

## 🚨 Troubleshooting

### Issue: Services not starting
```bash
docker-compose down -v
docker-compose up -d
```

### Issue: Can't see data in Grafana
1. Check if events are being received: `curl http://localhost:8000/api/events/stats`
2. Verify PostgreSQL has data: `docker exec postgres psql -U analytics -d analytics_db -c "SELECT COUNT(*) FROM events;"`
3. Refresh Grafana dashboard

### Issue: Tag Manager not tracking
1. Open browser console (F12)
2. Look for errors
3. Verify container script loads: Network tab → check for `.js` file
4. Check CORS settings if different domain

---

## 🔐 Security (Production)

⚠️ **Current setup is for development only**

For production:
1. Change all passwords in `.env`
2. Enable HTTPS
3. Add authentication to backend
4. Configure CORS properly
5. Use environment-specific configs
6. Enable Grafana authentication
7. Set up backups

---

## 📈 Scaling

### Horizontal Scaling
- Add more backend replicas
- Use Kafka partitions
- Read replicas for PostgreSQL

### Data Retention
- Configure PostgreSQL partitioning
- Set up automated archival
- Implement data retention policies

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## 📝 License

MIT License

---

## 🙏 Support

- Documentation: See `/docs` folder
- Issues: GitHub Issues
- Email: your-email@example.com

---

## 🎯 Roadmap

- [x] Schema-driven architecture
- [x] Multi-adaptor support
- [x] Grafana integration
- [ ] Click fraud detection (Phase 2)
- [ ] AI insights with TOON (Phase 3)
- [ ] Real-time alerting
- [ ] Custom dashboard builder
- [ ] Mobile SDK