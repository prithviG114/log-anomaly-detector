#!/bin/bash

echo "🚀 Starting Log Anomaly Detector..."
echo ""

# Build and start all services
docker-compose -f ../docker/docker-compose.yml up --build -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 15

# Initialize Cassandra database
echo ""
echo "📊 Initializing Cassandra database..."
docker exec cassandra cqlsh -e "CREATE KEYSPACE IF NOT EXISTS logs WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};" 2>/dev/null || true
docker exec cassandra cqlsh -e "USE logs; CREATE TABLE IF NOT EXISTS logs_table (id uuid PRIMARY KEY, service_name text, message text, timestamp bigint, is_anomaly boolean, score double);" 2>/dev/null || true

echo ""
echo "✅ All services started successfully!"
echo ""
echo "📍 Access the application:"
echo "   Frontend:    http://localhost:3000"
echo "   Backend API: http://localhost:8080"
echo "   Swagger UI:  http://localhost:8080/q/swagger-ui"
echo "   ML Analyzer: http://localhost:5001/health"
echo ""
echo "📝 View logs: docker-compose -f docker/docker-compose.yml logs -f"
echo "🛑 Stop all:  docker-compose -f docker/docker-compose.yml down"
echo ""
