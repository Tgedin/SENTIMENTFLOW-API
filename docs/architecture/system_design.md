# SentimentFlow API - System Design Document

## Architecture Overview

SentimentFlow API is designed as a **learning-focused local development project** that demonstrates modern Python API development with machine learning integration. The architecture prioritizes simplicity, clarity, and educational value over complex production patterns.

```
                    🎯 Local Development Architecture

   ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
   │   Client    │───▶│   FastAPI    │───▶│ ML Models   │
   │ (Browser/   │    │   Server     │    │ (Hugging    │
   │  API calls) │    │ (Port 8001)  │    │  Face)      │
   └─────────────┘    └──────┬───────┘    └─────────────┘
                             │
                             ▼
                      ┌─────────────┐
                      │  MongoDB    │
                      │ (Docker)    │
                      │ Port 27017  │
                      └─────────────┘
```

### Core Components

1. **🚀 FastAPI Application Server**

   - Handles HTTP requests and responses
   - Provides automatic API documentation at `/docs`
   - Manages request validation with Pydantic models
   - Runs on `localhost:8001` for development

2. **🤖 ML Processing Pipeline**

   - Multiple transformer models (BERT, RoBERTa, DistilBERT)
   - Text preprocessing and tokenization
   - Sentiment classification with confidence scores
   - Lazy model loading for faster startup

3. **🗄️ MongoDB Database (Optional)**

   - Document storage for analysis results
   - User session tracking (UUID-based)
   - Historical data for analytics
   - Runs in Docker container for easy setup

4. **🎨 Web Interface (Planned)**
   - Simple HTML/CSS/JavaScript frontend
   - Real-time sentiment analysis demo
   - Results visualization and history
   - Served directly from FastAPI

## Data Flow Architecture

```
                    📊 Request → Response Flow

   1️⃣ User Input    2️⃣ Validation    3️⃣ ML Processing    4️⃣ Storage    5️⃣ Response

   ┌─────────┐     ┌─────────┐      ┌──────────────┐    ┌─────────┐    ┌─────────┐
   │ "I love │────▶│ FastAPI │─────▶│ Transform    │───▶│ MongoDB │───▶│ JSON    │
   │ this    │     │ Pydantic│      │ Models       │    │ (opt.)  │    │ Response│
   │ API!"   │     │ Schema  │      │ • BERT       │    └─────────┘    │ + Score │
   └─────────┘     └─────────┘      │ • RoBERTa    │                   └─────────┘
                                    │ • DistilBERT │
                                    └──────────────┘
```

### Processing Steps:

1. **📝 Request Validation**

   - Client sends POST request to `/api/v1/sentiment/analyze`
   - Pydantic validates JSON payload and text content
   - Text preprocessing (cleaning, tokenization)

2. **🤖 Sentiment Analysis**

   - Text tokenized for transformer models
   - Multiple model inference (optional comparison)
   - Confidence scores and classification results generated

3. **💾 Data Persistence (Optional)**

   - Results stored in MongoDB with unique session ID
   - Historical tracking for analytics and comparison
   - Fast retrieval for repeated analyses

4. **📊 Response Formation**
   - Structured JSON response with sentiment and confidence
   - Multiple model results (if requested)
   - Processing metadata and timing information

## Key Design Decisions

### 🎯 Learning-First Approach

- **Simplified Architecture**: Focus on core concepts rather than complex patterns
- **Local Development**: Docker Compose for easy setup, no cloud dependencies
- **Progressive Enhancement**: Each development phase builds educational value
- **Hands-on Learning**: Every feature chosen for its teaching potential

### 🏗️ Clean Architecture Patterns

- **Repository Pattern**: Clean separation between data access and business logic
- **Service Layer**: Dedicated services for ML processing and text analysis
- **Dependency Injection**: FastAPI's built-in DI for testable components
- **Configuration Management**: Environment-based config with sensible defaults

### 🚀 Development Experience

- **Fast Startup**: Lazy model loading reduces development iteration time
- **Hot Reload**: FastAPI's `--reload` flag for instant code changes
- **Interactive Documentation**: Automatic OpenAPI docs at `/docs` endpoint
- **Comprehensive Testing**: Unit, integration, and API tests for confidence

### 📚 Educational Value

- **Multiple ML Models**: Compare different transformer architectures
- **Database Integration**: Learn MongoDB document modeling
- **API Design**: RESTful patterns with proper HTTP status codes
- **Testing Strategies**: Different testing approaches and best practices

## Development Phases & Learning Progression

### ✅ Phase 1: Foundation (Complete)

```
FastAPI Setup ──▶ ML Models ──▶ Basic API ──▶ Documentation
     🚀              🤖            📡            📚
```

### 🔄 Phase 2: Database Integration (Current)

```
MongoDB Setup ──▶ Repository Pattern ──▶ Data Storage ──▶ Historical APIs
     🗄️                  🏗️                   💾              📊
```

### ⏳ Phase 3: Web Interface

```
HTML/CSS/JS ──▶ API Integration ──▶ Real-time UI ──▶ Visualization
     🎨              🔌                ⚡              📈
```

### ⏳ Phase 4: Model Comparison

```
Multi-Model API ──▶ Performance Tests ──▶ Benchmarking ──▶ A/B Testing
       🤖                   ⚡                  📊             🧪
```

## Request Flow Sequence

```
Client          FastAPI         ML Service      MongoDB         Response
  │                │                │              │               │
  │──POST /analyze─▶│                │              │               │
  │                │──validate──────▶│              │               │
  │                │                │──tokenize────▶│               │
  │                │                │              │               │
  │                │                │◀─inference───│               │
  │                │                │              │               │
  │                │                │──store result▶│               │
  │                │◀──sentiment────│              │               │
  │◀─JSON response─│                │              │               │
  │                │                │              │               │
```

This sequence illustrates the simplified flow of a sentiment analysis request, emphasizing the learning aspects of each component interaction.
