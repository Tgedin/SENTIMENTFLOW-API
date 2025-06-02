# API Examples

## Basic Usage

### Analyze Sentiment

```bash
curl -X POST "http://localhost:8000/api/v1/sentiment/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}'
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

### With Different Model

```bash
curl -X POST "http://localhost:8000/api/v1/sentiment/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is terrible!",
    "model_name": "cardiffnlp/twitter-roberta-base-sentiment"
  }'
```

### Get Available Models

```bash
curl "http://localhost:8000/api/v1/sentiment/models"
```

## Test Cases

- **Positive**: "Amazing product! I absolutely love it!"
- **Negative**: "This is the worst experience ever."
- **Neutral**: "The weather is okay today."
