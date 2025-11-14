# Log Anomaly Detector

AI-powered log anomaly detection system for microservices using machine learning and real-time visualization.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Java](https://img.shields.io/badge/Java-21-orange.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![React](https://img.shields.io/badge/React-18-61dafb.svg)

## 🚀 Features

- **ML-Powered Detection**: Hybrid approach combining keyword-based rules and Isolation Forest algorithm
- **Real-Time Visualization**: Interactive charts showing anomaly trends, categories, and service-wise density
- **Severity Classification**: Automatic classification (Critical, Severe, Moderate, Low, Normal)
- **Rare Word Detection**: Identifies unknown error patterns automatically
- **Microservice Ready**: Designed for Docker and Kubernetes environments
- **Scalable Architecture**: Cassandra for storage, Quarkus for API, Flask for ML

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│  Quarkus API │────▶│  Cassandra  │
│   (React)   │     │   (Java 21)  │     │  Database   │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ ML Analyzer  │
                    │  (Flask)     │
                    └──────────────┘
```

## 📋 Prerequisites

- Docker & Docker Compose
- Java 21 (for local development)
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- Maven 3.8+

## 🚀 Quick Start

### One-Command Startup (Recommended)

**Linux/Mac:**
```bash
git clone https://github.com/prithviG114/log-anomaly-detector.git
cd log-anomaly-detector/scripts
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
git clone https://github.com/prithviG114/log-anomaly-detector.git
cd log-anomaly-detector/scripts
start.bat
```

That's it! The script will:
- Build all Docker images
- Start all services (Cassandra, ML Analyzer, Backend, Frontend)
- Initialize the database automatically
- Show you the access URLs

### Manual Docker Compose

If you prefer manual control:

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up --build -d

# Initialize database (wait 15 seconds first)
docker exec cassandra cqlsh -e "CREATE KEYSPACE IF NOT EXISTS logs WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};"
docker exec cassandra cqlsh -e "USE logs; CREATE TABLE IF NOT EXISTS logs_table (id uuid PRIMARY KEY, service_name text, message text, timestamp bigint, is_anomaly boolean, score double);"

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop all services
docker-compose -f docker/docker-compose.yml down
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **Swagger UI**: http://localhost:8080/q/swagger-ui
- **ML Analyzer**: http://localhost:5001/health

### Local Development

#### Backend (Quarkus)
```bash
./mvnw quarkus:dev
```

#### ML Analyzer
```bash
python ml-service/ml_analyzer.py
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Log Simulator (Generate Test Data)
```bash
python simulator/log_generator.py
```

#### Log Collectors (Fetch logs from Docker/K8s)
```bash
# Install dependencies
pip install -r requirements.txt

# Collect from Docker containers
python ingestion/docker/docker_collector.py

# Collect from Kubernetes pods
python ingestion/kubernetes/k8s_collector.py
```

## 📊 ML Model Features

The anomaly detection uses 6 features:

1. **Message Length** - Length of log message
2. **Service Hash** - Service identifier
3. **Error Severity Score** (0-10) - Keyword-based severity:
   - 10: Critical (crashed, fatal, panic)
   - 8: Severe (error, failed, exception)
   - 6: High (timeout, deadlock, unavailable)
   - 4: Medium (warning, retry)
   - 2: Low (deprecated, slow)
4. **Digit Ratio** - Percentage of numeric characters
5. **Word Count** - Number of words in message
6. **Rare Word Score** - Statistical rarity of vocabulary

## 🎨 Frontend Features

- **About Page**: Live stats and recent log activity
- **Visualizations Page**: 
  - Line chart: Anomalies over time
  - Pie chart: Anomaly categories
  - Bar chart: Service-wise anomaly density
- **Interactive**: Click on charts to filter logs
- **Modal Details**: Click on logs to see full details
- **Severity Badges**: Color-coded severity indicators

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
# Cassandra
CASSANDRA_HOST=localhost
CASSANDRA_PORT=9042
CASSANDRA_KEYSPACE=logs

# ML Analyzer
ML_ANALYZER_URL=http://localhost:5001

# API
QUARKUS_HTTP_PORT=8080

# Frontend
VITE_API_URL=http://localhost:8080
```

### Application Properties

Edit `src/main/resources/application.properties`:

```properties
quarkus.cassandra.contact-points=127.0.0.1:9042
quarkus.cassandra.local-datacenter=datacenter1
quarkus.cassandra.keyspace=logs
```

## 📡 API Endpoints

### Logs API

- `POST /logs` - Add a single log entry
- `POST /logs/batch` - Add multiple log entries
- `GET /logs` - Get all logs (with optional filters)
- `GET /logs/anomalies` - Get only anomalies

### ML Analyzer API

- `POST /predict` - Predict if a log is an anomaly
- `GET /health` - Health check
- `GET /` - Service info

## 🧪 Testing

### Backend Tests
```bash
./mvnw test
```

### ML Analyzer Tests
```bash
pytest ml-service/tests/test_ml_analyzer.py
```

## 📦 Project Structure

```
log-anomaly-detector/
├── docker/                # Docker configuration
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── Dockerfile.ml-analyzer
├── scripts/               # Startup scripts
│   ├── start.bat         # Windows startup
│   └── start.sh          # Linux/Mac startup
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── utils/        # Utility functions
│   └── package.json
├── src/main/java/         # Quarkus backend
│   └── org/project/logs/
│       ├── dao/          # Data access objects
│       ├── model/        # Data models
│       ├── resource/     # REST endpoints
│       └── service/      # Business logic
├── ml-service/            # Flask ML service
│   ├── ml_analyzer.py
│   ├── models/           # Trained models
│   └── tests/            # ML tests
├── ingestion/             # Log collectors
│   ├── docker/           # Docker log collector
│   ├── kubernetes/       # K8s log collector
│   └── aws-lambda-cloudwatch/  # AWS Lambda forwarder
├── simulator/             # Log generator
├── database/              # Cassandra schema
├── requirements.txt       # Python dependencies
└── pom.xml               # Maven configuration
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Quarkus, Flask, React, and Cassandra
- ML powered by scikit-learn's Isolation Forest
- Charts by Recharts
- UI inspired by glassmorphism design

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ for DevOps teams
