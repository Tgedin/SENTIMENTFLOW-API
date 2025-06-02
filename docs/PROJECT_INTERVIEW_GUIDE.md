# SentimentFlow API - Interview Guide

> **"I built this to go beyond tutorials and understand how modern ML-powered APIs really work"**

## 🎯 What I Built & Why

**"I wanted to understand the full stack - from ML models to production-ready APIs. So I built a sentiment analysis system that actually works."**

### The System

- FastAPI backend with 3 different ML models (BERT variants)
- MongoDB for storing analysis history
- Clean web interface for real-time sentiment analysis
- 48 passing tests with proper error handling

### Why This Project?

- **Real Learning**: Not just following tutorials - solving actual problems
- **Full Stack**: Frontend, backend, database, ML - everything connected
- **Production Mindset**: Built like something that could actually be deployed

## 🏗️ Architecture

**"I designed this to be simple but scalable - each piece does one thing well."**

```
User Input → Web Interface → FastAPI → ML Models → Database → Results
    📝           🎨           🚀       🤖         🗄️        📊

Flow: Text comes in, gets analyzed by BERT/RoBERTa/DistilBERT, results stored & returned
```

### Key Decisions

**FastAPI over Flask**: _"I wanted async support and automatic documentation"_

```python
@app.post("/analyze")
async def analyze_sentiment(text: str):
    # Async all the way through
```

**Multiple ML Models**: _"Compare BERT variants - speed vs accuracy tradeoffs"_

- DistilBERT: Fast, good enough for most cases
- RoBERTa: Better accuracy, slower
- BERT: Baseline comparison

**MongoDB over SQL**: _"Flexible schema for storing different model outputs"_

## 🚀 Development Journey

**"I built this in phases - each one taught me something new"**

```
Week 1-2: API Foundation    → Got FastAPI running, learned async patterns
Week 3-4: ML Integration    → Connected BERT models, solved memory issues
Week 5-6: Database Layer    → Added MongoDB, built repository pattern
Week 7-8: Testing Suite     → 48 tests, caught real bugs
Week 9-10: Web Interface    → Simple UI, connected everything
```

### Biggest Challenges I Solved

**Memory Problem**: _"Models were eating 4GB RAM on startup"_

```
Before: Load all models at startup (4GB RAM)
After:  Lazy loading - only load when needed (257MB baseline)
```

**Model Chaos**: _"Each model returned different formats"_

```python
# Before: DistilBERT → 'NEGATIVE', RoBERTa → 'LABEL_0'
# After: Everything → {'sentiment': 'negative', 'confidence': 0.9}
```

**Storage Explosion**: _"Tests created 240 duplicate model files"_

- Fixed: Reuse "latest" version instead of timestamped copies
- Result: 97% storage reduction (62GB → 1.8GB)

## 🎓 What I Learned

**Technical Skills**: FastAPI async patterns, ML model integration, MongoDB, testing strategies

**Problem-Solving**: _"Real projects have messy requirements. You can't just follow tutorials."_

- Memory optimization when models are expensive
- Standardizing inconsistent ML outputs
- Debugging async/await patterns
- Test-driven development for catching edge cases

## 📊 Results

```
✅ 48/49 tests passing (98% success)
✅ 3 ML models integrated with standardized output
✅ 150ms average response time
✅ 257MB memory footprint (down from 4GB+)
✅ Clean, documented codebase ready for interviews
```

## 🎤 Interview Soundbites

**"The biggest challenge was memory management with multiple ML models. I learned that premature optimization can backfire - lazy loading was much better than preloading everything."**

**"I chose FastAPI for async support and automatic docs. MongoDB for flexible schema. The goal was learning modern patterns, not just getting something working."**

**"Building this taught me the difference between tutorial code and production code. Real systems need error handling, testing, and performance considerations you don't see in examples."**

---

_This project shows I can learn independently, solve real problems, and build production-quality code._
