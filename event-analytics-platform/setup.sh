#!/bin/bash

echo "🚀 Real-Time Analytics Dashboard - Setup Script"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker is installed: $(docker --version)"
echo "✅ Docker Compose is installed: $(docker-compose --version)"
echo ""

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running."
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker daemon is running"
echo ""

# Create directory structure
echo "📁 Creating project structure..."
mkdir -p backend/app
mkdir -p frontend/src/components
mkdir -p frontend/public
mkdir -p event-generator

echo "✅ Project structure created"
echo ""

# Check if all required files exist
echo "🔍 Checking for required files..."
required_files=(
    "docker-compose.yml"
    ".env"
    "backend/Dockerfile"
    "backend/requirements.txt"
    "backend/app/__init__.py"
    "backend/app/main.py"
    "backend/app/consumer.py"
    "backend/app/schemas.py"
    "backend/app/utils.py"
    "backend/app/config.py"
    "event-generator/Dockerfile"
    "event-generator/requirements.txt"
    "event-generator/generator.py"
    "frontend/Dockerfile"
    "frontend/package.json"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ Missing required files:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    echo ""
    echo "Please ensure all files are created before running this script."
    exit 1
fi

echo "✅ All required files found"
echo ""

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down -v 2>/dev/null
echo "✅ Cleanup complete"
echo ""

# Build and start services
echo "🔨 Building Docker images (this may take a few minutes)..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi

echo "✅ Build complete"
echo ""

echo "🚀 Starting services..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start services. Please check the error messages above."
    exit 1
fi

echo "✅ Services started"
echo ""

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
echo ""

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running (http://localhost:8000)"
else
    echo "⚠️  Backend may not be ready yet"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running (http://localhost:3000)"
else
    echo "⚠️  Frontend may not be ready yet"
fi

echo ""
echo "================================================"
echo "🎉 Setup Complete!"
echo "================================================"
echo ""
echo "📊 Access the dashboard: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Stop services:    docker-compose down"
echo "   Restart:          docker-compose restart"
echo "   Check status:     docker-compose ps"
echo ""
echo "🐛 Troubleshooting:"
echo "   If the dashboard doesn't update, wait 30 seconds for all services to initialize"
echo "   View logs: docker-compose logs -f"
echo ""