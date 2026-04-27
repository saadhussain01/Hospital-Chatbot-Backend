# 🏥 AI-Powered Hybrid Hospital Chatbot - Backend

A modular, production-ready backend system for a hospital chatbot that combines rule-based logic with AI capabilities.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Production Deployment](#production-deployment)
- [Testing](#testing)

## ✨ Features

### Core Capabilities

1. **Intent Classification** - Automatically categorizes user messages
2. **Rule-Based Appointment System** - Safe, deterministic booking logic
3. **RAG-Based FAQ System** - AI-powered answers from hospital knowledge base
4. **Symptom Checker** - Safe health guidance with medical disclaimers
5. **Admin Dashboard API** - Analytics and monitoring endpoints
6. **Multi-language Support** (Future: English + Urdu)

### Safety Features

- ✅ No AI for critical booking operations
- ✅ Medical disclaimers on all symptom responses
- ✅ Emergency escalation for critical symptoms
- ✅ Complete chat logging for compliance
- ✅ HIPAA-ready architecture

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
│  (Frontend) │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
├─────────────────────────────────────┤
│  ┌──────────────────────────────┐  │
│  │   Intent Classifier          │  │
│  │   (Rule-based + Keywords)    │  │
│  └────────────┬─────────────────┘  │
│               │                     │
│      ┌────────┼────────┐           │
│      ▼        ▼        ▼           │
│  ┌────────┐ ┌───┐ ┌─────────┐     │
│  │Appoint │ │RAG│ │ Symptom │     │
│  │Engine  │ │Sys│ │ Checker │     │
│  └────────┘ └───┘ └─────────┘     │
│      │        │        │           │
│      └────────┼────────┘           │
│               ▼                     │
│       ┌──────────────┐             │
│       │   Database   │             │
│       │   (SQLite)   │             │
│       └──────────────┘             │
└─────────────────────────────────────┘
```

## 🚀 Installation

### Prerequisites

- Python 3.9+
- pip
- Virtual environment (recommended)

### Step 1: Clone and Setup

```bash
# Create project directory
mkdir hospital-chatbot-backend
cd hospital-chatbot-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# (For basic setup, defaults work fine)
```

### Step 3: Initialize Database

The database will be automatically initialized on first run, but you can do it manually:

```bash
python -c "from database import Database; db = Database(); db.initialize()"
```

### Step 4: Run Server

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

API Documentation (Swagger): `http://localhost:8000/docs`

## 📖 Usage

### Testing the API

#### 1. Health Check

```bash
curl http://localhost:8000/health
```

#### 2. Send Chat Message

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to book an appointment",
    "session_id": "test-session-123"
  }'
```

#### 3. Get Available Doctors

```bash
curl http://localhost:8000/api/doctors
```

#### 4. Check Doctor Availability

```bash
curl "http://localhost:8000/api/appointments/availability?doctor_id=1&date=2026-04-25"
```

#### 5. Get Admin Statistics

```bash
curl http://localhost:8000/api/admin/stats
```

## 🔌 API Documentation

### Chat Endpoints

#### POST `/api/chat`
Main chatbot endpoint - processes user messages

**Request:**
```json
{
  "message": "I have a headache",
  "session_id": "optional-session-id",
  "user_id": "optional-user-id"
}
```

**Response:**
```json
{
  "response": "You may need to consult our Neurology department...",
  "intent": "symptom",
  "requires_action": false,
  "metadata": {
    "severity": "medium"
  }
}
```

**Intent Types:**
- `appointment` - Booking/scheduling requests
- `faq` - General questions
- `symptom` - Health-related queries
- `greeting` - Hi/hello messages

### Appointment Endpoints

#### POST `/api/appointments`
Create a new appointment

**Request:**
```json
{
  "patient_name": "John Doe",
  "doctor_id": 1,
  "date": "2026-04-25",
  "time": "10:00",
  "phone": "+92-300-1234567",
  "reason": "Checkup"
}
```

#### GET `/api/appointments/availability`
Get available time slots

**Query Parameters:**
- `doctor_id` (int) - Doctor ID
- `date` (string) - Date in YYYY-MM-DD format

#### DELETE `/api/appointments/{appointment_id}`
Cancel an appointment

#### GET `/api/doctors`
Get list of all doctors

### Admin Endpoints

#### GET `/api/admin/stats`
Get dashboard statistics

**Response:**
```json
{
  "total_chats": 150,
  "total_appointments": 45,
  "common_queries": [
    {"intent": "faq", "count": 60},
    {"intent": "appointment", "count": 45}
  ],
  "recent_chats": [...]
}
```

#### GET `/api/admin/chats`
Get chat history with pagination

**Query Parameters:**
- `limit` (int) - Number of records (default: 50)
- `offset` (int) - Offset for pagination (default: 0)

#### GET `/api/admin/appointments`
Get all appointments

**Query Parameters:**
- `date` (string, optional) - Filter by date (YYYY-MM-DD)

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application & routes
├── intent_classifier.py    # Intent classification module
├── appointment_engine.py   # Rule-based appointment logic
├── rag_system.py          # RAG system for FAQ
├── symptom_checker.py     # Symptom guidance module
├── database.py            # Database operations
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
└── hospital_chatbot.db   # SQLite database (auto-created)
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```env
# API Keys (for production RAG)
OPENAI_API_KEY=your_key_here

# Database
DATABASE_URL=sqlite:///hospital_chatbot.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

### Customizing Hospital Data

#### Add/Modify Doctors

Edit `database.py` in the `_insert_sample_data()` method:

```python
sample_doctors = [
    ("Doctor Name", "Specialty", "Phone", "Email", "Mon,Tue,Wed"),
    # Add more doctors...
]
```

#### Add/Modify FAQ Knowledge Base

Edit `rag_system.py` in the `load_knowledge_base()` method:

```python
self.knowledge_base = [
    {
        "question": "Your question",
        "answer": "Your answer",
        "category": "category_name"
    },
    # Add more Q&A pairs...
]
```

#### Customize Symptom Mapping

Edit `symptom_checker.py` in the `__init__()` method:

```python
self.symptom_mapping = {
    "category_name": {
        "keywords": ["symptom1", "symptom2"],
        "department": "Department Name",
        "severity": "low/medium/high/critical",
        "message": "Guidance message"
    }
}
```

## 🚀 Production Deployment

### Upgrade to Production-Grade Components

#### 1. Database: SQLite → PostgreSQL

```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/hospital_db
```

#### 2. RAG System: Add Real AI

```bash
# Install AI libraries
pip install openai sentence-transformers faiss-cpu

# Update rag_system.py to use actual embeddings and LLM
```

Example code in `rag_system.py`:

```python
from sentence_transformers import SentenceTransformer
import openai

self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
openai.api_key = os.getenv('OPENAI_API_KEY')
```

#### 3. Add Authentication

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

Implement JWT tokens for API security.

#### 4. Add Rate Limiting

```bash
pip install slowapi
```

#### 5. Use Production Server

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t hospital-chatbot-backend .
docker run -p 8000:8000 hospital-chatbot-backend
```

## 🧪 Testing

### Manual Testing

Use the Swagger UI at `http://localhost:8000/docs` to test all endpoints interactively.

### Automated Testing

Create `test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint():
    response = client.post("/api/chat", json={
        "message": "Hello",
        "session_id": "test"
    })
    assert response.status_code == 200
    assert "response" in response.json()
```

Run tests:

```bash
pytest test_api.py
```

## 🔒 Security Considerations

1. **Input Validation** - All inputs are validated via Pydantic models
2. **SQL Injection** - Parameterized queries prevent SQL injection
3. **CORS** - Configure allowed origins in production
4. **Rate Limiting** - Implement in production
5. **Authentication** - Add JWT tokens for production
6. **HTTPS** - Use SSL/TLS in production
7. **Data Encryption** - Encrypt sensitive data at rest

## 📊 Monitoring & Logging

### Add Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hospital_chatbot.log'),
        logging.StreamHandler()
    ]
)
```

### Monitor Performance

- Use FastAPI's built-in metrics
- Add Prometheus/Grafana for production
- Monitor database query performance
- Track API response times

## 🤝 Contributing

1. Follow PEP 8 style guide
2. Add docstrings to all functions
3. Write tests for new features
4. Update README for new endpoints

# 🚀 Quick Start Guide

## Fixed Issues
✅ **Deprecated on_event warning** - Now using modern `lifespan` context manager
✅ **Reload warning** - Now using import string `"main:app"` instead of app object

## Running the Server

### Method 1: Direct Python (Recommended for Development)
```bash
python main.py
```

### Method 2: Using Uvicorn CLI (For More Control)
```bash
# Development with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production (with workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Method 3: Using Gunicorn (Production)
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Method 4: Using Docker
```bash
# Build and run with docker-compose
docker-compose up --build

# Or just run
docker-compose up
```

## Environment Variables

Create a `.env` file:
```env
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## Testing the API

### 1. Check Health
```bash
curl http://localhost:8000/health
```

### 2. Send Chat Message
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'
```

### 3. View API Documentation
Open browser: http://localhost:8000/docs

## Common Issues & Solutions

### Issue: Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Issue: Module Not Found
```bash
# Make sure you're in virtual environment
pip install -r requirements.txt
```

### Issue: Database Not Initializing
```bash
# Manually initialize
python -c "from database import Database; db = Database(); db.initialize()"
```

## Accessing Endpoints

| Endpoint | URL |
|----------|-----|
| API Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health | http://localhost:8000/health |
| Chat | http://localhost:8000/api/chat |
| Doctors | http://localhost:8000/api/doctors |
| Admin Stats | http://localhost:8000/api/admin/stats |

## Next Steps

1. ✅ Server is running
2. 📖 Read API_DOCS.md for endpoint details
3. 🧪 Run tests: `python test_system.py`
4. 🎨 Build frontend to connect to this backend
5. 🚀 Deploy (see DEPLOYMENT.md)

Happy coding! 🎉

## 📄 License

This project is for educational/demonstration purposes.

## 🆘 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the logs in `hospital_chatbot.log`
3. Verify database integrity
4. Check environment variables

## 🎯 Roadmap

- [ ] Multi-language support (Urdu)
- [ ] Voice input/output
- [ ] WhatsApp integration
- [ ] Email/SMS notifications
- [ ] Advanced analytics dashboard
- [ ] ML-based intent classification
- [ ] Appointment reminders
- [ ] Patient history tracking

---

**Built with ❤️ for better healthcare accessibility**
#   H o s p i t a l - C h a t b o t - B a c k e n d  
 #   H o s p i t a l - C h a t b o t - B a c k e n d  
 