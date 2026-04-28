# 🏥 AI-Powered Hybrid Hospital Chatbot (Backend)

> Production-ready FastAPI backend combining rule-based logic + AI for
> hospital automation.

------------------------------------------------------------------------

## ✨ Features

-   Intent classification
-   Appointment system
-   RAG FAQ system
-   Symptom checker
-   Admin analytics API
-   Safety-first architecture

------------------------------------------------------------------------

## 🏗️ Architecture

Client → FastAPI → Intent Classifier → (Appointments / RAG / Symptoms) →
SQLite DB

------------------------------------------------------------------------

## 🚀 Quick Start

``` bash
git clone https://github.com/your-repo/hospital-chatbot.git
cd hospital-chatbot-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Run Server

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

------------------------------------------------------------------------

## 📡 API Endpoints

### Chat

POST /api/chat

### Doctors

GET /api/doctors

### Appointments

POST /api/appointments

------------------------------------------------------------------------

## 📁 Structure

backend/ - main.py - database.py - intent_classifier.py -
appointment_engine.py - rag_system.py - symptom_checker.py

------------------------------------------------------------------------

## ⚙️ Config

.env HOST=0.0.0.0 PORT=8000 DEBUG=True

------------------------------------------------------------------------

## 🧪 Test

pytest test_api.py

------------------------------------------------------------------------

## 🐳 Docker

docker build -t hospital-chatbot . docker run -p 8000:8000
hospital-chatbot

------------------------------------------------------------------------
