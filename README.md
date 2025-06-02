# SentimentFlow API

Sentiment analysis API with multiple ML models, built with FastAPI.

## Features

- **3 ML Models**: DistilBERT, RoBERTa (Twitter), Multilingual BERT
- **REST API**: `/analyze` endpoint with model selection
- **Web Interface**: Real-time analysis with confidence scores
- **Storage**: MongoDB for results, Redis for caching

## Quick Start

```bash
# Setup
docker-compose up -d
pip install -r requirements.txt
uvicorn app.main:app --reload

# Use
# API: http://localhost:8000/docs
# Web: frontend/index.html
```

## Usage

```bash
# Analyze text
curl -X POST "http://localhost:8000/api/v1/sentiment/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this!", "model_name": "distilbert-base-uncased-finetuned-sst-2-english"}'

# Response
{
  "success": true,
  "result": {
    "sentiment": "positive",
    "confidence": 0.99
  }
}
```

**Tech Stack:**

- **FastAPI** - Modern Python web framework
- **Transformers** - Hugging Face ML models
- **MongoDB** - Document database
- **Docker** - Development environment

## 📊 API Endpoints

## API Endpoints

- `POST /api/v1/sentiment/analyze` - Analyze text sentiment
- `GET /api/v1/sentiment/models` - List available models
- `GET /health` - Health check

## Available Models

- **distilbert-base-uncased-finetuned-sst-2-english** (default)
- **cardiffnlp/twitter-roberta-base-sentiment**
- **nlptown/bert-base-multilingual-uncased-sentiment**

## Testing

```bash
pytest  # Run all tests
```

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Transformers** - Hugging Face ML models
- **MongoDB** - Document database
- **Redis** - Caching layer
