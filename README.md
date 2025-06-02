# SentimentFlow API

> **A hands-on learning project for FastAPI and machine learning integration**

A complete sentiment analysis system demonstrating modern Python API development with multiple ML models, database integration, and a clean web interface.

## ✨ What it does

- **Analyzes sentiment** of any text using state-of-the-art BERT models
- **Compares models** - DistilBERT, RoBERTa (Twitter), and Multilingual BERT
- **Stores results** in MongoDB with session tracking
- **Web interface** for real-time analysis and testing
- **RESTful API** with automatic documentation

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd sentimentflow-api

# Start services
docker-compose up -d  # MongoDB & Redis
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload

# Open in browser
# API: http://localhost:8000/docs
# Web: frontend/index.html
```

## 🎯 Key Features

- **3 ML Models**: Compare different sentiment analysis approaches
- **Real-time Analysis**: Fast inference with confidence scores
- **Historical Data**: Store and query past analyses
- **Clean Architecture**: Repository pattern, service layers
- **Comprehensive Testing**: 98% test coverage
- **Modern Frontend**: Responsive web interface

## 🏗️ Architecture

```
API Layer          ML Layer           Data Layer
┌─────────┐       ┌─────────┐       ┌─────────┐
│ FastAPI │ ────▶ │  BERT   │ ────▶ │ MongoDB │
│ Pydantic│       │ RoBERTa │       │ Session │
│ Uvicorn │       │DistilBERT│      │ Storage │
└─────────┘       └─────────┘       └─────────┘
```

**Tech Stack:**

- **FastAPI** - Modern Python web framework
- **Transformers** - Hugging Face ML models
- **MongoDB** - Document database
- **Docker** - Development environment

## 📊 API Endpoints

- `POST /api/v1/sentiment/analyze` - Analyze single text
- `POST /api/v1/sentiment/analyze/batch` - Analyze multiple texts
- `GET /api/v1/sentiment/models` - List available models
- `GET /api/v1/history/sessions` - Get analysis history
- `GET /health` - System health check

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test types
pytest tests/unit/        # Unit tests
pytest tests/integration/ # Integration tests
pytest tests/e2e/         # End-to-end tests
```

## 📈 Project Status

- ✅ **Phase 1**: Core API & ML integration
- ✅ **Phase 2**: Database & comprehensive testing
- ✅ **Phase 3**: Web interface & optimization
- ⏳ **Phase 4**: Advanced features (optional)
- ⏳ **Phase 5**: Production deployment (optional)

## 🎓 Learning Focus

This project demonstrates:

- **Modern Python APIs** with FastAPI and async/await
- **ML Model Integration** using Hugging Face transformers
- **Database Design** with MongoDB and repository patterns
- **Testing Strategies** from unit to integration testing
- **Clean Code Architecture** with proper separation of concerns

## 📁 Documentation

- [Project Status & Todo](docs/todo.md) - Current progress and next steps
- [Final Status Report](docs/FINAL_PROJECT_STATUS.md) - Complete project summary
- [API Documentation](docs/api/) - Detailed endpoint documentation
- [Architecture Guide](docs/architecture/) - System design and structure
- [Frontend Guide](frontend/README.md) - Web interface documentation
