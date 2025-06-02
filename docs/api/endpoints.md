# API Endpoints

## Sentiment Analysis

### Analyze Text

```
POST /api/v1/sentiment/analyze
```

**Request:**

```json
{
  "text": "I love this product!",
  "model_name": "distilbert-base-uncased-finetuned-sst-2-english"
}
```

**Response:**

```json
{
  "success": true,
  "result": {
    "sentiment": "positive",
    "confidence": 0.9918,
    "model_name": "distilbert-base-uncased-finetuned-sst-2-english"
  }
}
```

### List Models

```
GET /api/v1/sentiment/models
```

**Response:**

```json
{
  "success": true,
  "result": {
    "models": [
      "distilbert-base-uncased-finetuned-sst-2-english",
      "cardiffnlp/twitter-roberta-base-sentiment",
      "nlptown/bert-base-multilingual-uncased-sentiment"
    ],
    "default": "distilbert-base-uncased-finetuned-sst-2-english"
  }
}
```

## Health Check

### System Status

```
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-06-02T18:30:00Z"
}
```
