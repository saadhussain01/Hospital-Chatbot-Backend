"""
AI-Powered Hybrid Hospital Chatbot Backend
FastAPI server with intent classification, RAG, and appointment management
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import uvicorn
import json
import os

# Import modules
from intent_classifier import IntentClassifier
from appointment_engine import AppointmentEngine
from rag_system import RAGSystem
from symptom_checker import SymptomChecker
from database import Database

# Global instances
db = None
intent_classifier = None
appointment_engine = None
rag_system = None
symptom_checker = None

# ==================== LIFESPAN CONTEXT MANAGER ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    Replaces deprecated on_event decorators
    """
    # Startup
    global db, intent_classifier, appointment_engine, rag_system, symptom_checker
    
    try:
        print("\n" + "="*60)
        print("🏥 Hospital Chatbot System - Starting Up")
        print("="*60)
        
        # Initialize database
        print("\n📊 Initializing database...")
        db = Database()
        db.initialize()
        print("   ✅ Database ready")
        
        # Verify database connection
        if not db.check_connection():
            raise Exception("Database connection failed")
        
        # Initialize other components
        intent_classifier = IntentClassifier()
        appointment_engine = AppointmentEngine(db)
        rag_system = RAGSystem()
        symptom_checker = SymptomChecker()
        
        # Load RAG system with hospital knowledge
        print("\n🧠 Loading RAG knowledge base...")
        rag_system.load_knowledge_base()
        print("   ✅ RAG system ready")
        
        # Verify RAG system
        if not rag_system.is_ready():
            print("   ⚠️  Warning: RAG system not fully loaded")
        
        port = os.getenv("PORT", "8000")
        print("\n" + "="*60)
        print("🚀 System Ready!")
        print("="*60)
        print(f"\n📡 API Server: http://localhost:{port}")
        print(f"📖 API Docs: http://localhost:{port}/docs")
        print(f"🔍 Health Check: http://localhost:{port}/health")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Startup Error: {str(e)}")
        print("⚠️  System may not function correctly")
        raise
    
    yield  # Server is running
    
    # Shutdown
    try:
        print("\n🛑 Shutting down Hospital Chatbot System...")
        
        # Close database connection
        if db:
            db.close()
            print("   ✅ Database connection closed")
        
        print("👋 Shutdown complete\n")
        
    except Exception as e:
        print(f"⚠️  Shutdown warning: {str(e)}")

# ==================== CREATE APP ====================

app = FastAPI(
    title="Hospital Chatbot API", 
    version="1.0.0",
    description="AI-powered hybrid hospital chatbot with appointment booking and health guidance",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== REQUEST/RESPONSE MODELS ====================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    requires_action: bool = False
    action_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AppointmentRequest(BaseModel):
    patient_name: str
    doctor_id: int
    date: str
    time: str
    phone: Optional[str] = None
    reason: Optional[str] = None

class AppointmentResponse(BaseModel):
    success: bool
    message: str
    appointment_id: Optional[int] = None

class AdminStatsResponse(BaseModel):
    total_chats: int
    total_appointments: int
    common_queries: List[Dict[str, Any]]
    recent_chats: List[Dict[str, Any]]

# ==================== CHAT ENDPOINT ====================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes user message and routes to appropriate module
    """
    try:
        # Log chat to database
        chat_id = db.log_chat(
            session_id=request.session_id or "anonymous",
            user_id=request.user_id,
            message=request.message,
            timestamp=datetime.now()
        )
        
        # Step 1: Classify intent
        intent = intent_classifier.classify(request.message)
        
        # Step 2: Route to appropriate module
        if intent == "appointment":
            response = await handle_appointment_intent(request.message, request.session_id)
        elif intent == "faq":
            response = await handle_faq_intent(request.message)
        elif intent == "symptom":
            response = await handle_symptom_intent(request.message)
        else:
            response = ChatResponse(
                response="I'm here to help! You can:\n• Book appointments\n• Ask about hospital services\n• Get basic health guidance\n\nHow can I assist you?",
                intent="greeting"
            )
        
        # Log response
        db.log_response(chat_id, response.response, intent)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

# ==================== INTENT HANDLERS ====================

async def handle_appointment_intent(message: str, session_id: str) -> ChatResponse:
    """Handle appointment-related queries using rule-based logic"""
    result = appointment_engine.process(message, session_id)
    
    return ChatResponse(
        response=result["response"],
        intent="appointment",
        requires_action=result.get("requires_action", False),
        action_type=result.get("action_type"),
        metadata=result.get("metadata")
    )

async def handle_faq_intent(message: str) -> ChatResponse:
    """Handle general questions using RAG system"""
    answer = rag_system.query(message)
    
    return ChatResponse(
        response=answer,
        intent="faq"
    )

async def handle_symptom_intent(message: str) -> ChatResponse:
    """Handle symptom queries with safety guardrails"""
    result = symptom_checker.process(message)
    
    # Always include disclaimer
    disclaimer = "\n\n⚠️ This is not a medical diagnosis. Please consult a healthcare professional."
    
    return ChatResponse(
        response=result["response"] + disclaimer,
        intent="symptom",
        metadata={"severity": result.get("severity")}
    )

# ==================== APPOINTMENT ENDPOINTS ====================

@app.post("/api/appointments", response_model=AppointmentResponse)
async def create_appointment(appointment: AppointmentRequest):
    """Create a new appointment (rule-based, no AI)"""
    try:
        result = appointment_engine.book_appointment(
            patient_name=appointment.patient_name,
            doctor_id=appointment.doctor_id,
            date=appointment.date,
            time=appointment.time,
            phone=appointment.phone,
            reason=appointment.reason
        )
        
        return AppointmentResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/appointments/availability")
async def get_availability(doctor_id: int, date: str):
    """Get available time slots for a doctor on a specific date"""
    try:
        slots = appointment_engine.get_available_slots(doctor_id, date)
        return {"available_slots": slots}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: int):
    """Cancel an existing appointment"""
    try:
        result = appointment_engine.cancel_appointment(appointment_id)
        return {"success": True, "message": "Appointment cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/doctors")
async def get_doctors():
    """Get list of all doctors"""
    doctors = db.get_doctors()
    return {"doctors": doctors}

# ==================== ADMIN ENDPOINTS ====================

@app.get("/api/admin/stats", response_model=AdminStatsResponse)
async def get_admin_stats():
    """Get dashboard statistics for admin panel"""
    stats = db.get_admin_stats()
    
    return AdminStatsResponse(
        total_chats=stats["total_chats"],
        total_appointments=stats["total_appointments"],
        common_queries=stats["common_queries"],
        recent_chats=stats["recent_chats"]
    )

@app.get("/api/admin/chats")
async def get_chat_history(limit: int = 50, offset: int = 0):
    """Get chat history with pagination"""
    chats = db.get_chat_history(limit=limit, offset=offset)
    return {"chats": chats, "total": len(chats)}

@app.get("/api/admin/appointments")
async def get_all_appointments(date: Optional[str] = None):
    """Get all appointments, optionally filtered by date"""
    appointments = db.get_appointments(date=date)
    return {"appointments": appointments}

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": db.check_connection() if db else False,
            "rag_system": rag_system.is_ready() if rag_system else False,
            "intent_classifier": intent_classifier is not None
        }
    }

# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed. Using default configuration.")
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("DEBUG", "True").lower() == "true"
    
    print("\n🔧 Configuration:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Reload: {reload}")
    print()
    
    # Run server
    # Note: For reload to work properly, use: uvicorn main:app --reload
    uvicorn.run(
        "main:app",  # Use import string instead of app object for reload support
        host=host, 
        port=port, 
        reload=reload,
        log_level="info"
    )