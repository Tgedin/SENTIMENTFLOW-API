# SentimentFlow API

A microservices-based sentiment analysis API built with FastAPI, MongoDB, and Redis.

## Overview

SentimentFlow API provides sentiment analysis capabilities through a RESTful API interface. The system is designed with a microservices architecture that ensures scalability, maintainability, and high performance.

## Key Features

- Real-time sentiment analysis of text inputs
- Detailed sentiment breakdown with confidence scores
- Caching system for improved performance on repeated requests
- Comprehensive API documentation
- Authentication and rate limiting
- Historical analysis tracking

## Documentation

- [Project Structure](docs/architecture/project_structure.md) - Complete project directory structure and organization
- [System Design](./docs/architecture/system_design.md) - Technical architecture and system design documentation
- API Documentation (available at `/docs` when running the API)

## Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- MongoDB
- Redis

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/sentimentflow-api.git
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

7. Access the API documentation at http://localhost:8000/docs

## Pushing to a New GitHub Repository

1. Create a new repository on GitHub (e.g., `SENTIMENTFLOW-API`) via the GitHub web interface, **without** initializing with a README or .gitignore.

2. In your terminal, run the following commands from your project root:

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/Tgedin/SENTIMENTFLOW-API.git
   git push -u origin main
   ```

3. Your code is now pushed to your new GitHub repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
