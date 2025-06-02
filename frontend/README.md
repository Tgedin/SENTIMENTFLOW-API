# SentimentFlow Frontend

A minimalist web interface for the SentimentFlow sentiment analysis API.

## Features

- 🎨 **Clean, modern design** with responsive layout
- 🤖 **Real-time sentiment analysis** using multiple BERT models
- 📊 **Visual results** with confidence scores and emoji indicators
- ⚡ **Fast API integration** with proper error handling
- 📱 **Mobile-friendly** responsive design

## Quick Start

1. Make sure your FastAPI server is running:

   ```bash
   cd /home/theo-gedin/sentimentflow-api
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Open the frontend:

   ```bash
   # Open in browser
   open frontend/index.html
   # OR serve with a simple HTTP server
   cd frontend && python -m http.server 3000
   ```

3. Enter text and analyze sentiment!

## Architecture

```
index.html → script.js → fetch() → FastAPI API → ML Models → Results
    🎨         📝         🔗         🚀          🤖        📊
```

## Files

- `index.html` - Main page structure
- `style.css` - Modern styling and responsive design
- `script.js` - API integration and DOM manipulation

## API Integration

The frontend connects to these API endpoints:

- `POST /api/v1/sentiment/analyze` - Main sentiment analysis
- `GET /docs` - API documentation (linked in footer)

## Sample Texts to Try

- **Positive**: "I absolutely love this product! It's amazing and works perfectly."
- **Negative**: "This is the worst experience I've ever had. Completely disappointed."
- **Neutral**: "The weather is okay today, nothing special but not bad either."

## Learning Focus

This minimalist approach demonstrates:

- **Vanilla JavaScript** - Understanding core browser APIs
- **Fetch API** - Modern HTTP requests without libraries
- **DOM Manipulation** - Real-time UI updates
- **Error Handling** - Graceful failure management
- **Responsive Design** - Works on desktop and mobile

Built as part of Phase 3 of the SentimentFlow learning project.
