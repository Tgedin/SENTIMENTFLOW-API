# SentimentFlow API

A microservices-based sentiment analysis API with cloud integration built with FastAPI, Docker, and AWS/Azure services.

## Project Purpose

This project was created as a personal learning endeavor to gain hands-on experience with:

- FastAPI framework
- Docker containerization
- Cloud services (AWS Lambda/Azure Functions)
- Serverless architecture
- Cloud databases (MongoDB/DynamoDB)
- NLP techniques (sentiment analysis, text preprocessing)
- API security patterns
- Cloud monitoring and observability

While the repository is public, its primary purpose is educational rather than for production use. I've put significant emphasis on writing comprehensive documentation as if it were a professional project to reinforce best practices.

## Overview

SentimentFlow API provides sentiment analysis capabilities through a RESTful API interface. The system is designed with cloud-native architecture that demonstrates scalability, maintainability, and performance considerations using serverless computing.

## Key Features

- Real-time sentiment analysis of text inputs
- Multiple model approaches (BERT, distilled models)
- Detailed sentiment breakdown with confidence scores
- Serverless deployment options for cost-effective scaling
- Cloud database integration for persistent storage
- Infrastructure-as-Code templates for consistent deployments
- Comprehensive API documentation
- Authentication and rate limiting
- Historical analysis tracking

## Documentation

- [Project Structure](docs/architecture/project_structure.md) - Complete project directory structure and organization
- [System Design](./docs/architecture/system_design.md) - Technical architecture and system design documentation
- API Documentation (available at `/docs` when running the API)

## Technology Stack

- **Backend**: FastAPI (Python 3.9+)
- **Core Dependencies**: Uvicorn, Pydantic, pytest
- **Database**: MongoDB/DynamoDB
- **Caching**: Redis
- **Cloud Services**: AWS Lambda/Azure Functions
- **Monitoring**: CloudWatch/Azure Monitor
- **Infrastructure**: Terraform/CloudFormation/ARM Templates
- **Containerization**: Docker & Docker Compose
- **NLP**: Hugging Face Transformers, NLTK, spaCy, transformers-based sentiment models (BERT, RoBERTa)

## Local Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Tgedin/sentimentflow-api.git
   cd sentimentflow-api
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. Copy the example environment file and modify as needed:

   ```bash
   cp .env.example .env
   ```

5. Start the services using Docker Compose:

   ```bash
   docker-compose up -d
   ```

6. Run the application:

   ```bash
   uvicorn app.main:app --reload
   ```

## Learning Outcomes

This project is instrumental in understanding:

- How to structure a FastAPI application
- MongoDB integration in a Python ecosystem
- NLP processing pipelines for text analysis
- Docker containerization for microservices
- API security best practices
- Documentation standards in professional software development

## License

This project is licensed under the MIT License - see the LICENSE file for details.
