#!/bin/bash

echo "🧪 Testing Tag Manager Serving"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "1️⃣ Creating test schema..."
SCHEMA_RESPONSE=$(curl -s -X POST http://localhost:8000/api/schemas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "portfolio",
    "description": "Portfolio website tracking",
    "properties": {
      "page_view": {"page": "string", "referrer": "string"},
      "project_click": {"project_name": "string", "project_url": "string"},
      "link_click": {"link_type": "string", "link_url": "string"}
    }
  }')

echo "✅ Schema created"
echo ""

echo "2️⃣ Creating test adaptor..."
ADAPTOR_RESPONSE=$(curl -s -X POST http://localhost:8000/api/adaptors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Portfolio Test",
    "schema_id": "portfolio",
    "website_url": "https://saurabh-lohokare-portfolio.vercel.app",
    "tracking_rules": {
      "auto_page_view": true,
      "track_clicks": true,
      "track_forms": false
    }
  }')

CONTAINER_ID=$(echo $ADAPTOR_RESPONSE | grep -o '"container_id":"[^"]*"' | cut -d'"' -f4)

echo "✅ Adaptor created"
echo "📦 Container ID: $CONTAINER_ID"
echo ""

echo "3️⃣ Testing tag script URL..."
TAG_URL="http://localhost:8000/tag/${CONTAINER_ID}.js"
echo "📍 URL: $TAG_URL"
echo ""

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $TAG_URL)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Tag script is accessible!${NC}"
    echo ""
    echo "4️⃣ Installation code:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "<script src=\"${TAG_URL}\" async></script>"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "5️⃣ Add this to your portfolio website's <head> section"
else
    echo -e "${RED}❌ Failed to access tag script (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo "✅ Test complete!"