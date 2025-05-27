# SentimentFlow API

> **🎯 Learning-Focused FastAPI & ML Integration Project**

A hands-on learning project that demonstrates modern Python API development with FastAPI and machine learning model integration. Built for **local development** and educational purposes.

```
                    📊 Sentiment Analysis Pipeline

   User Input  ──▶  FastAPI  ──▶  ML Models  ──▶  MongoDB  ──▶  Results
      📝            🚀           🤖 BERT         🗄️           📈
                                🤖 RoBERTa
                                🤖 DistilBERT
```

## 🎯 Project Purpose

This project emphasizes **hands-on learning** over complex production features, focusing on:

- **FastAPI Framework**: Modern Python API development with automatic documentation
- **ML Model Integration**: Multiple transformer models (BERT, RoBERTa, DistilBERT)
- **Local Database**: MongoDB integration with Docker Compose
- **Testing Strategies**: Unit, integration, and API testing patterns
- **Clean Architecture**: Repository patterns and service layer design
- **Documentation**: Professional-level docs for learning best practices

## ✨ Key Features

- 🔍 **Real-time sentiment analysis** with confidence scores
- 🤖 **Multiple ML models** comparison (BERT variants)
- 📊 **Historical data storage** with MongoDB
- 🚀 **Interactive API docs** at `/docs` endpoint
- 🧪 **Comprehensive testing** suite
- 🎨 **Simple web interface** for demonstration
- ⚡ **Fast local development** setup

## 📁 Documentation


- [🏗️ Project Structure](docs/architecture/project_structure.md) - Complete directory organization
- [🎨 System Design](docs/architecture/system_design.md) - Architecture and data flow


## 🛠️ Technology Stack

```
   API Layer          ML Layer           Data Layer
   ┌─────────┐       ┌─────────┐       ┌─────────┐
   │ FastAPI │ ────▶ │  BERT   │ ────▶ │ MongoDB │
   │ Uvicorn │       │ RoBERTa │       │ Docker  │
   │ Pydantic│       │DistilBERT│      │ Compose │
   └─────────┘       └─────────┘       └─────────┘
```

- **🐍 Backend**: FastAPI (Python 3.12+)
- **🤖 ML Models**: Hugging Face Transformers (BERT, RoBERTa, DistilBERT)
- **🗄️ Database**: MongoDB with Docker Compose
- **🔧 Core Tools**: Uvicorn, Pydantic, pytest
- **📦 Development**: Docker, Docker Compose
- **🧪 Testing**: pytest, httpx, unittest

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Tgedin/sentimentflow-api.git
   cd sentimentflow-api
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start MongoDB (optional for basic testing):**

   ```bash
   docker-compose up -d
   ```

5. **Run the API:**

   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

6. **Test the API:**
   ```bash
   # Open browser to http://localhost:8001/docs
   # Or test with curl:
   curl -X POST "http://localhost:8001/api/v1/sentiment/analyze" \
        -H "Content-Type: application/json" \
        -d '{"text": "I love learning FastAPI!"}'
   ```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test categories
pytest tests/unit/        # Unit tests
pytest tests/integration/ # Integration tests
```

## 📈 Current Progress

- ✅ **Phase 1**: Core API & ML integration (Complete)
- 🔄 **Phase 2**: Database & storage (In Progress)
- ⏳ **Phase 3**: Web interface
- ⏳ **Phase 4**: Model comparison & testing
- ⏳ **Phase 5**: Documentation & polish

## 🎓 Learning Outcomes

Through this project, you'll gain hands-on experience with:

- 🚀 **FastAPI**: Modern async Python web framework
- 🤖 **ML Integration**: Working with transformer models
- 🗄️ **Database Design**: MongoDB document modeling
- 🧪 **Testing**: API testing strategies and best practices
- 📚 **Documentation**: Writing clear, professional docs
- 🛠️ **Development**: Local development workflow and tooling

## 🤝 Contributing

This is a personal learning project, but feedback and suggestions are welcome! Feel free to:

- 🐛 Report bugs or issues
- 💡 Suggest improvements or learning opportunities
- 📚 Share educational resources related to the tech stack
- 🤔 Ask questions about the implementation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

_Built with ❤️ for learning FastAPI and ML integration_
