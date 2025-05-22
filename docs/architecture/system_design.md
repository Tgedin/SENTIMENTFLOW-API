# SentimentFlow API - System Design Document

## Architecture Summary

The SentimentFlow API follows a microservices architecture with four specialized containers that work together. Each container handles one specific aspect of the system, allowing for independent scaling and maintenance.

```
+---------------+    +------------------+
|               |    |                  |
| API Gateway   +--->+ NLP Processing   |
| (FastAPI)     |    | Engine           |
|               |    |                  |
+-------+-------+    +------------------+
        |
        v
+-------+-------+    +------------------+
|               |    |                  |
| Data Storage  +--->+ Caching Layer    |
| (MongoDB)     |    | (Redis)          |
|               |    |                  |
+---------------+    +------------------+
```

### Components:

1. **API Gateway**

   - Functions as the system's front door, handling all client interactions through FastAPI
   - Manages authentication, request validation, and rate limiting
   - Provides automatic API documentation via Swagger UI
   - Routes requests to appropriate services

2. **NLP Processing Engine**

   - Contains the machine learning pipeline for sentiment analysis
   - Handles text preprocessing (tokenization, stop-word removal, normalization)
   - Performs model inference using pre-trained BERT models
   - Formats results for client consumption

3. **Data Storage Layer**

   - Uses MongoDB for persistent storage
   - Stores analysis results, user data, and system metrics
   - Leverages document-based structure for flexible schema requirements

4. **Caching Layer**
   - Employs Redis to store frequently accessed results and session data
   - Improves response times for repeated queries
   - Reduces computational costs by minimizing redundant processing

## Data Flow Architecture

```
   +--------+    +-----------------+    +----------------+
   | Client +--->+ API Gateway     +--->+ NLP Processing |
   +--------+    | - Authentication|    | - Text Analysis|
                 | - Validation    |    +--------+-------+
                 +-----------------+             |
                         ^                       v
                         |               +-------+-------+
                  +------+------+        | Data Storage  |
                  | Response    |<-------+ & Caching     |
                  +-------------+        +---------------+
```

1. **Request Processing:**

   - Requests enter through the API Gateway
   - Authentication and validation occur immediately
   - Clean, validated text is prepared for analysis

2. **Sentiment Analysis:**

   - Validated text flows to the NLP Processing Engine
   - Text undergoes preprocessing steps (tokenization, normalization)
   - Preprocessed text is fed to the sentiment analysis model
   - Results are generated with sentiment classification and confidence scores

3. **Data Storage and Caching:**

   - Results are stored in MongoDB for historical tracking
   - Simultaneously cached in Redis for performance optimization
   - Unique request IDs link results across the system

4. **Response Delivery:**
   - Response travels back through the API Gateway
   - Future identical requests may be served directly from cache

## Key Design Decisions

### Scalability

- **Horizontal Scaling:** Stateless design enables adding more container instances as needed
- **Load Balancing:** Requests distributed across multiple instances of the NLP Processing Engine
- **Independent Scaling:** Each component can scale according to its specific resource needs

### Separation of Concerns

- Authentication logic, ML processing, and data storage operate independently
- Makes the system easier to debug, test, and evolve
- Enables specialized optimization for each component

### Performance Optimization

- **Lazy Model Loading:** Reduces startup time for the NLP container
- **Efficient Caching:** Redis strategies for repeated analyses
- **Database Indexing:** Optimized for common query patterns
- **Async Processing:** FastAPI's asynchronous capabilities maximize throughput

### Startup-Friendly Implementation

- Initially deploy all containers on a single machine
- Scale individual components based on actual usage patterns
- Cost-effective resource utilization during early stages

## Sequence Diagram for Request Processing

```
Client        API Gateway        NLP Engine        MongoDB        Redis
  |                |                 |                |              |
  |---Request----->|                 |                |              |
  |                |----Validate---->|                |              |
  |                |                 |                |              |
  |                |                 |--Process Text->|              |
  |                |                 |                |              |
  |                |                 |--Store Result->|              |
  |                |                 |                |              |
  |                |                 |--Cache Result---------------->|
  |                |<---Result-------|                |              |
  |<---Response----|                 |                |              |
  |                |                 |                |              |
```

This sequence diagram illustrates the flow of a typical sentiment analysis request through the system, showing the interactions between different components and the data transformations that occur.
