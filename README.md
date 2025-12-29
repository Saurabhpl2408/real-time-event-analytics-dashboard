# 🚀 Real-Time Event Analytics Platform

A production-ready, self-hosted analytics platform built for tracking and analyzing user interactions in real-time. Features a modern React dashboard, event streaming with Kafka, and powerful visualization with Grafana.

![Analytics Dashboard](https://img.shields.io/badge/Analytics-Dashboard-blue)
![React](https://img.shields.io/badge/React-18.x-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192?logo=postgresql)
![Kafka](https://img.shields.io/badge/Kafka-Redpanda-FF4438)

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Why This Platform?](#-why-this-platform)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Default Credentials](#-default-credentials)
- [Project Structure](#-project-structure)
- [Usage Guide](#-usage-guide)
- [Kafka & Event Streaming](#-kafka--event-streaming)
- [API Documentation](#-api-documentation)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Analytics
- ✅ **Real-time Event Tracking** - Track user interactions with sub-second latency
- ✅ **Custom Event Schemas** - Define your own event types and properties
- ✅ **Multi-Site Support** - Track multiple websites/apps with separate adaptors
- ✅ **Session Tracking** - Automatic user and session identification
- ✅ **Event Filtering** - Filter by schema, adaptor, time range, and event type

### Dashboard
- ✅ **Modern React UI** - Beautiful, responsive dashboard with dark mode
- ✅ **Live Statistics** - Auto-refreshing stats every 5 seconds
- ✅ **Event Breakdown** - Visual charts showing event distribution
- ✅ **Clickable Cards** - Direct links to Grafana for detailed analysis
- ✅ **Schema Management** - Create, edit, and delete event schemas via UI
- ✅ **Adaptor Management** - Manage tracking scripts for multiple sites

### Data Processing
- ✅ **Event Streaming** - Kafka-powered event processing pipeline
- ✅ **Dual Storage** - Events stored in both master log and schema-specific tables
- ✅ **Schema Validation** - Automatic validation of incoming events
- ✅ **Flexible Properties** - Allow extra properties beyond schema definition

### Visualization
- ✅ **Grafana Integration** - Pre-configured dashboards for deep analysis
- ✅ **Custom Queries** - Direct PostgreSQL access for custom analytics
- ✅ **Real-time Metrics** - Track page views, clicks, sessions, and custom events

### Security & Reliability
- ✅ **JWT Authentication** - Secure API access with token-based auth
- ✅ **Role-Based Access** - Admin and viewer roles
- ✅ **CORS Protection** - Configurable cross-origin policies
- ✅ **Health Checks** - Automatic service monitoring
- ✅ **Error Handling** - Graceful degradation and error recovery

---

## 🛠 Tech Stack

### Frontend
- **React 18** - Modern UI framework
- **Vite** - Lightning-fast build tool
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **Tailwind CSS** - Utility-first styling
- **Lucide Icons** - Beautiful icon set

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy 2.0** - Async ORM
- **Pydantic** - Data validation
- **JWT** - Secure authentication
- **Uvicorn** - ASGI server

### Data Layer
- **PostgreSQL 15** - Primary database
- **Redpanda (Kafka)** - Event streaming
- **Grafana 10** - Data visualization

### Infrastructure
- **Docker & Docker Compose** - Container orchestration
- **Nginx** - Frontend web server

---

## 🏗 Architecture
```
┌─────────────────┐
│  Your Website   │
│   (Portfolio)   │
└────────┬────────┘
         │ Events
         ▼
┌─────────────────┐
│  Analytics API  │
│    (FastAPI)    │
└────────┬────────┘
         │
    ┌────┴─────┬──────────────┐
    ▼          ▼              ▼
┌────────┐ ┌────────┐  ┌──────────┐
│ Kafka  │ │PostgreSQL│ │Event Log │
│(Stream)│ │ Tables  │  │  Master  │
└────────┘ └────────┘  └──────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │  React Dashboard│
                     │    & Grafana    │
                     └─────────────────┘
```

### Event Flow

1. **Event Generation**: User interacts with your website (clicks, page views, etc.)
2. **Event Capture**: JavaScript tracking script captures the event
3. **API Ingestion**: Event sent to `/api/events/ingest` endpoint
4. **Validation**: Schema validation ensures data integrity
5. **Dual Storage**: 
   - Stored in schema-specific table (`events_portfolio_events`)
   - Logged in master event log (`event_logs`)
6. **Stream Processing**: Event pushed to Kafka for real-time processing
7. **Visualization**: Data visible in dashboard and Grafana within seconds

---

## 🎯 Why This Platform?

### Compared to Google Analytics
| Feature | This Platform | Google Analytics |
|---------|--------------|------------------|
| **Self-Hosted** | ✅ Full control | ❌ Cloud only |
| **Data Privacy** | ✅ Your data stays with you | ❌ Data sent to Google |
| **Custom Events** | ✅ Unlimited custom schemas | ⚠️ Limited custom dimensions |
| **Real-Time** | ✅ Sub-second latency | ⚠️ 24-48hr delay |
| **No Sampling** | ✅ 100% data accuracy | ❌ Sampled data on free tier |
| **Open Source** | ✅ Fully customizable | ❌ Closed source |
| **Cost** | ✅ Free (hosting only) | ⚠️ Expensive for high volume |

### Compared to Plausible/Matomo
| Feature | This Platform | Plausible/Matomo |
|---------|--------------|------------------|
| **Kafka Streaming** | ✅ Real-time event pipeline | ❌ Direct database writes |
| **Schema Flexibility** | ✅ Dynamic event schemas | ⚠️ Fixed event structure |
| **Multi-Site** | ✅ Unlimited adaptors | ⚠️ Limited on free tier |
| **API Access** | ✅ Full REST API | ⚠️ Limited API |
| **Grafana Integration** | ✅ Built-in | ❌ Requires setup |

### Unique Features
- 🎨 **Dynamic Schema Engine** - Create new event types on the fly
- 🔄 **Event Streaming Pipeline** - Kafka for scalable real-time processing
- 🎯 **Dual Storage Model** - Query optimization with schema-specific tables
- 🛡️ **Privacy First** - No cookies, no PII tracking, fully GDPR compliant
- 🚀 **Production Ready** - Health checks, error handling, and graceful degradation

---

## 📦 Prerequisites

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Node.js** 18+ (for local frontend development)
- **8GB RAM** minimum (for all services)

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/analytics-platform.git
cd analytics-platform
```

### 2. Start All Services
```bash
docker-compose up -d
```

This will start:
- ✅ PostgreSQL (port 5432)
- ✅ Kafka/Redpanda (port 19092)
- ✅ FastAPI Backend (port 8000)
- ✅ React Dashboard (port 3000)
- ✅ Grafana (port 3001)

### 3. Verify Services
```bash
# Check all services are running
docker-compose ps

# Check backend health
curl http://localhost:8000/docs

# Check dashboard
open http://localhost:3000
```

### 4. Login to Dashboard

Navigate to `http://localhost:3000` and login with:
- **Username**: `admin`
- **Password**: `admin123`

### 5. Create Your First Schema

1. Go to **Schemas** page
2. Click **"New Schema"**
3. Use this structure for web tracking:
```bash
curl -X POST http://localhost:8000/api/schemas/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "portfolio_events",
    "description": "Portfolio website tracking",
    "properties": {
      "page_view": {},
      "github_project_click": {},
      "linkedin_profile_click": {},
      "email_link_click": {},
      "navigation_click": {},
      "external_link_click": {}
    }
  }'
```

### 6. Create an Adaptor

1. Go to **Adaptors** page
2. Click **"New Adaptor"**
3. Fill in:
   - **Name**: My Portfolio
   - **Schema**: portfolio_events
   - **Website URL**: http://localhost:8080
   - **Description**: Personal website tracking

4. Copy the **Container ID** (e.g., `CAP-ABC123`)

### 7. Install Tracking Script

Add this to your website's HTML (before `</body>`):
```html
<script>
(function() {
  const CONFIG = {
    apiUrl: 'http://localhost:8000/api/events/ingest',
    schemaId: 'portfolio_events',
    containerId: 'CAP-YOUR-CONTAINER-ID' // Replace with your actual ID
  };

  function getSessionId() {
    let sessionId = sessionStorage.getItem('analytics_session');
    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('analytics_session', sessionId);
    }
    return sessionId;
  }

  function getUserId() {
    let userId = localStorage.getItem('analytics_user');
    if (!userId) {
      userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('analytics_user', userId);
    }
    return userId;
  }

  function trackEvent(eventType, properties = {}) {
    fetch(CONFIG.apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        schema_id: CONFIG.schemaId,
        event_type: eventType,
        user_id: getUserId(),
        session_id: getSessionId(),
        timestamp: new Date().toISOString(),
        properties: {
          ...properties,
          tracked_at: new Date().toISOString(),
          page_url: window.location.href,
          page_path: window.location.pathname,
          container_id: CONFIG.containerId
        },
        metadata: {}
      })
    }).catch(err => console.error('Analytics error:', err));
  }

  // Track page view
  trackEvent('page_view', { page_title: document.title });

  // Track clicks
  document.addEventListener('click', function(e) {
    const target = e.target.closest('a');
    if (!target) return;
    
    const href = target.getAttribute('href') || '';
    const text = target.textContent.trim();
    
    if (href.includes('github.com')) {
      trackEvent('github_project_click', { link_text: text });
    } else if (href.includes('linkedin')) {
      trackEvent('linkedin_profile_click', { link_text: text });
    }
  }, true);

  console.log('✅ Analytics initialized');
})();
</script>
```

### 8. View Your Data

1. **Dashboard**: http://localhost:3000 - Real-time stats
2. **Grafana**: http://localhost:3001 - Detailed visualizations
3. **API Docs**: http://localhost:8000/docs - Interactive API documentation

---

## �� Default Credentials

### Analytics Dashboard
- **URL**: http://localhost:3000
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Admin (full access)

### Grafana
- **URL**: http://localhost:3001
- **Username**: `admin`
- **Password**: `admin123`
- **Pre-configured**: PostgreSQL datasource

### PostgreSQL
- **Host**: localhost
- **Port**: 5432
- **Database**: `analytics_db`
- **Username**: `analytics`
- **Password**: `analytics123`

### API Access
```bash
# Get JWT token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 📁 Project Structure
```
analytics-platform/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # API routes
│   │   │   ├── auth.py      # Authentication
│   │   │   ├── events.py    # Event ingestion & stats
│   │   │   ├── schemas.py   # Schema management
│   │   │   └── adaptors.py  # Adaptor management
│   │   ├── core/            # Core functionality
│   │   │   ├── database.py  # Database connection
│   │   │   ├── kafka_producer.py  # Kafka integration
│   │   │   └── schema_engine.py   # Dynamic schema engine
│   │   ├── models/          # SQLAlchemy models
│   │   └── schemas_pydantic/# Pydantic schemas
│   └── Dockerfile
│
├── dashboard/               # React dashboard
│   ├── src/
│   │   ├── pages/          # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Schemas.jsx
│   │   │   ├── Adaptors.jsx
│   │   │   └── Settings.jsx
│   │   ├── components/     # Reusable components
│   │   ├── stores/         # Zustand stores
│   │   └── services/       # API services
│   └── Dockerfile
│
├── postgres/               # PostgreSQL initialization
│   └── init.sql           # Database schema
│
├── grafana/               # Grafana configuration
│   ├── provisioning/
│   └── dashboards/
│
└── docker-compose.yml     # Service orchestration
```

---

## 📖 Usage Guide

### Creating Custom Schemas

Schemas define what events you can track. Each schema can have multiple event types.

**Example: E-commerce Schema**
```json
{
  "name": "ecommerce_events",
  "description": "E-commerce tracking",
  "properties": {
    "product_view": {},
    "add_to_cart": {},
    "checkout_start": {},
    "purchase_complete": {}
  }
}
```

**Example: SaaS Schema**
```json
{
  "name": "saas_events",
  "description": "SaaS app tracking",
  "properties": {
    "signup_start": {},
    "trial_activated": {},
    "feature_used": {},
    "subscription_upgraded": {}
  }
}
```

### Tracking Custom Properties

Any properties you send are stored, even if not defined in schema:
```javascript
trackEvent('product_view', {
  product_id: 'ABC123',
  product_name: 'Amazing Widget',
  category: 'Electronics',
  price: 99.99,
  currency: 'USD',
  // Any custom properties you want
});
```

### Querying Events

**Via API:**
```bash
# Get event stats
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/events/stats?schema_id=portfolio_events&days=7"

# Get recent events
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/api/events/recent?limit=100"
```

**Via PostgreSQL:**
```sql
-- Top 10 most clicked links
SELECT 
  properties->>'link_text' as link,
  COUNT(*) as clicks
FROM events_portfolio_events
WHERE event_type LIKE '%click%'
GROUP BY properties->>'link_text'
ORDER BY clicks DESC
LIMIT 10;

-- Daily page views
SELECT 
  DATE(timestamp) as date,
  COUNT(*) as page_views
FROM events_portfolio_events
WHERE event_type = 'page_view'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

---

## 🔄 Kafka & Event Streaming

### Why Kafka?

Kafka (Redpanda) provides:
- **Decoupling** - Ingest and processing are independent
- **Buffering** - Handle traffic spikes without data loss
- **Scalability** - Process millions of events per second
- **Reliability** - Fault-tolerant message storage
- **Real-time** - Sub-millisecond event processing

### How It Works

1. **Event Ingestion** → Event received by FastAPI
2. **Validation** → Schema validation passes
3. **Database Write** → Event stored in PostgreSQL
4. **Kafka Publish** → Event sent to Kafka topic: `analytics.events`
5. **Stream Processing** → (Future: aggregations, alerts, ML)
6. **Consumers** → Multiple services can consume events independently

### Kafka Topics

- `analytics.events` - All raw events
- `analytics.pageviews` - Filtered page views (future)
- `analytics.clicks` - Filtered click events (future)

### Monitoring Kafka
```bash
# List topics
docker exec -it analytics-kafka rpk topic list

# Check topic details
docker exec -it analytics-kafka rpk topic describe analytics.events

# Consume messages
docker exec -it analytics-kafka rpk topic consume analytics.events
```

### Future Enhancements

- ✨ Real-time aggregations (windowed counts)
- ✨ Anomaly detection (ML-based)
- ✨ Custom alerts (Slack/Email notifications)
- ✨ Event replay for debugging
- ✨ Multi-datacenter replication

---

## �� API Documentation

### Authentication
```bash
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}

Response: {
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {...}
}
```

### Event Ingestion
```bash
POST /api/events/ingest
{
  "schema_id": "portfolio_events",
  "event_type": "page_view",
  "user_id": "user_123",
  "session_id": "session_abc",
  "timestamp": "2025-01-01T00:00:00Z",
  "properties": {
    "page_url": "https://example.com",
    "page_title": "Home"
  },
  "metadata": {}
}
```

### Get Statistics
```bash
GET /api/events/stats?schema_id=portfolio_events&days=7

Response: {
  "total_events": 1500,
  "page_views": 800,
  "clicks": 700,
  "unique_sessions": 250,
  "events_by_type": {
    "page_view": 800,
    "github_project_click": 150
  }
}
```

**Full API Documentation**: http://localhost:8000/docs

---

## 🗺 Roadmap

### Phase 1: Core Platform (✅ Complete)
- ✅ Event ingestion API
- ✅ Schema management
- ✅ Adaptor management
- ✅ Real-time dashboard
- ✅ Grafana integration
- ✅ Kafka streaming

### Phase 2: Advanced Analytics (🚧 In Progress)
- ⏳ Funnel analysis
- ⏳ User journey visualization
- ⏳ Cohort analysis
- ⏳ A/B testing support
- ⏳ Custom date range picker

### Phase 3: Intelligence (📋 Planned)
- 📋 Anomaly detection (ML)
- 📋 Predictive analytics
- 📋 Custom alerts & notifications
- 📋 Automated insights
- 📋 Heatmaps & session replay

### Phase 4: Enterprise (📋 Planned)
- 📋 Multi-tenancy
- 📋 SSO integration
- 📋 Advanced RBAC
- 📋 Data export & compliance
- 📋 SLA monitoring

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Backend development
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend development
cd dashboard
npm install
npm run dev
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- Redpanda for Kafka compatibility
- Grafana for powerful visualizations
- React community for excellent tooling

---

**Made with ❤️ by Saurabh Lohokare**

⭐ Star this repo if you find it useful!
