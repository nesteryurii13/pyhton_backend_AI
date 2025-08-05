# 🚀 Sophisticated FastAPI GPT Backend

A production-ready, scalable FastAPI backend for querying OpenAI's GPT models with professional architecture, comprehensive error handling, and modern development practices.

## 🏗️ **Architecture Overview**

This application follows a sophisticated, layered architecture designed for scalability and maintainability:

```
app/
├── api/                 # API layer with versioning
│   ├── deps.py         # Shared dependencies
│   └── v1/             # API version 1
│       ├── api.py      # Router aggregation
│       └── endpoints/  # Individual endpoint modules
├── core/               # Core functionality
│   ├── config.py       # Configuration management
│   └── logging.py      # Centralized logging
├── middleware/         # Custom middleware
│   ├── cors.py         # CORS configuration
│   └── error_handler.py # Global error handling
├── models/             # Data models and schemas
│   └── schemas.py      # Pydantic models
├── services/           # Business logic layer
│   └── gpt_service.py  # GPT service implementation
└── tests/              # Test suite
```

## ✨ **Key Features**

### 🔧 **Production-Ready Architecture**
- **Layered Design**: Clear separation of concerns with API, service, and data layers
- **Dependency Injection**: Proper DI pattern for testability and maintainability
- **API Versioning**: Future-proof API design with version management
- **Error Handling**: Comprehensive error handling with proper HTTP status codes

### 📊 **Advanced Logging & Monitoring**
- **Structured Logging**: JSON-formatted logs with contextual information
- **Request Tracking**: Unique request IDs for distributed tracing
- **Performance Metrics**: Processing time headers and logging
- **Health Checks**: Comprehensive health monitoring

### 🛡️ **Security & Reliability**
- **Input Validation**: Robust validation with Pydantic models
- **Error Sanitization**: Safe error responses without sensitive data exposure
- **CORS Configuration**: Flexible CORS setup for different environments
- **Rate Limiting Ready**: Structure prepared for rate limiting implementation

### 🐳 **DevOps & Deployment**
- **Docker Support**: Complete containerization with multi-stage builds
- **Docker Compose**: Development environment setup
- **Environment Management**: Flexible configuration for different environments
- **Health Checks**: Built-in health monitoring for container orchestration

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.10+
- OpenAI API key
- Docker (optional, for containerized deployment)

### **1. Install Dependencies**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Environment Configuration**
Create a `.env` file in the project root:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# API Configuration
PROJECT_NAME=GPT Query API
PROJECT_DESCRIPTION=A sophisticated FastAPI backend for querying GPT models
VERSION=1.0.0

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS Configuration (comma-separated)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### **3. Run the Application**

#### **Option A: Direct Python**
```bash
python main.py
```

#### **Option B: Using Uvicorn**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### **Option C: Using Docker**
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t gpt-api .
docker run -p 8000:8000 --env-file .env gpt-api
```

## 📚 **API Documentation**

### **Available Endpoints**

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | System information |
| `/docs` | GET | Interactive API documentation (Swagger UI) |
| `/redoc` | GET | Alternative API documentation (ReDoc) |
| `/api/v1/health` | GET | Health check |
| `/api/v1/query` | POST | GPT query endpoint |

### **API Usage Examples**

#### **Health Check**
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

#### **GPT Query**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Explain quantum computing in simple terms",
       "model": "gpt-3.5-turbo",
       "temperature": 0.7,
       "max_tokens": 500
     }'
```

#### **System Information**
```bash
curl -X GET "http://localhost:8000/"
```

## 🧪 **Testing**

### **Run Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_health.py -v
```

### **Test Structure**
- `app/tests/conftest.py`: Pytest configuration and fixtures
- `app/tests/test_health.py`: Health endpoint tests
- `app/tests/test_gpt.py`: GPT endpoint tests (create as needed)

## 🔧 **Development Features**

### **Code Quality Tools**
```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### **Environment Variables**

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | GPT model to use | gpt-3.5-turbo |
| `OPENAI_MAX_TOKENS` | Max tokens per response | 1000 |
| `OPENAI_TEMPERATURE` | Response creativity (0-2) | 0.7 |
| `PROJECT_NAME` | API project name | GPT Query API |
| `SERVER_HOST` | Server host | 0.0.0.0 |
| `SERVER_PORT` | Server port | 8000 |
| `DEBUG` | Debug mode | false |
| `LOG_LEVEL` | Logging level | INFO |
| `LOG_FORMAT` | Log format (json/text) | json |

## 🏗️ **Advanced Architecture Details**

### **Dependency Injection Pattern**
The application uses FastAPI's dependency injection system for clean, testable code:
- Services are injected into endpoints
- Configuration is injected where needed
- Easy mocking for tests

### **Error Handling Strategy**
- **Global Exception Handlers**: Centralized error handling
- **Custom Exceptions**: Service-specific error types
- **Request ID Tracking**: Unique IDs for error tracing
- **Safe Error Responses**: No sensitive data in error messages

### **Logging Strategy**
- **Structured Logging**: JSON format for log aggregation
- **Contextual Information**: Request IDs, processing time, metadata
- **Performance Tracking**: Built-in performance monitoring
- **Environment-Aware**: Different log levels for dev/prod

## 🚀 **Production Deployment**

### **Docker Deployment**
```bash
# Production build
docker build -t gpt-api:latest .

# Run in production mode
docker run -d \
  --name gpt-api \
  -p 8000:8000 \
  --env-file .env.prod \
  --restart unless-stopped \
  gpt-api:latest
```

### **Environment-Specific Configuration**
Create different `.env` files for different environments:
- `.env.development`
- `.env.staging`
- `.env.production`

### **Health Monitoring**
The application includes comprehensive health checks:
- Application health at `/api/v1/health`
- GPT service connectivity verification
- Docker health check configuration

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 **Related Technologies**

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and settings management
- **OpenAI**: GPT model integration
- **Docker**: Containerization
- **Pytest**: Testing framework
- **Uvicorn**: ASGI server implementation