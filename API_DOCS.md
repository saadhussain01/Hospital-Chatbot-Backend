# 📚 API Documentation

## Base URL
```
Development: http://localhost:8000
Production: https://api.yourhospital.com
```

## Authentication
Currently, the API is open for development. In production, implement JWT authentication.

---

## 🔹 Core Chat Endpoint

### POST `/api/chat`
Main chatbot endpoint for processing user messages.

**Request Body:**
```json
{
  "message": "string",           // Required: User's message
  "session_id": "string",        // Optional: Session identifier
  "user_id": "string"            // Optional: User identifier
}
```

**Response:**
```json
{
  "response": "string",          // Bot's response message
  "intent": "string",            // Detected intent (appointment/faq/symptom/greeting)
  "requires_action": boolean,    // Whether user action is needed
  "action_type": "string",       // Type of action (if requires_action is true)
  "metadata": {                  // Additional context data
    "severity": "string",        // For symptom queries
    "doctors": [],               // For appointment queries
    "available_slots": []        // For appointment queries
  }
}
```

**Example - Greeting:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "session_id": "user123"
  }'
```

**Example - FAQ:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your hospital timings?",
    "session_id": "user123"
  }'
```

**Example - Symptom Check:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have a headache and fever",
    "session_id": "user123"
  }'
```

**Example - Appointment Booking:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to book an appointment",
    "session_id": "user123"
  }'
```

---

## 🔹 Doctor Endpoints

### GET `/api/doctors`
Retrieve list of all available doctors.

**Response:**
```json
{
  "doctors": [
    {
      "id": 1,
      "name": "Ahmed Khan",
      "specialty": "Cardiology",
      "phone": "+92-300-1234567",
      "email": "ahmed.khan@hospital.com",
      "available_days": "Mon,Tue,Wed,Thu,Fri",
      "created_at": "2026-04-21T10:00:00"
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/api/doctors
```

---

## 🔹 Appointment Endpoints

### POST `/api/appointments`
Create a new appointment directly (bypasses chatbot flow).

**Request Body:**
```json
{
  "patient_name": "string",     // Required
  "doctor_id": integer,         // Required
  "date": "YYYY-MM-DD",        // Required
  "time": "HH:MM",             // Required
  "phone": "string",           // Optional
  "reason": "string"           // Optional
}
```

**Response:**
```json
{
  "success": boolean,
  "message": "string",
  "appointment_id": integer
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Ahmed Ali",
    "doctor_id": 1,
    "date": "2026-04-25",
    "time": "10:00",
    "phone": "+92-300-1234567",
    "reason": "Regular checkup"
  }'
```

### GET `/api/appointments/availability`
Check available time slots for a doctor on a specific date.

**Query Parameters:**
- `doctor_id` (integer, required): Doctor's ID
- `date` (string, required): Date in YYYY-MM-DD format

**Response:**
```json
{
  "available_slots": [
    "09:00", "09:30", "10:00", "10:30", "11:00", "..."
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/appointments/availability?doctor_id=1&date=2026-04-25"
```

### DELETE `/api/appointments/{appointment_id}`
Cancel an existing appointment.

**Path Parameters:**
- `appointment_id` (integer): ID of the appointment to cancel

**Response:**
```json
{
  "success": true,
  "message": "Appointment cancelled successfully"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/appointments/123
```

---

## 🔹 Admin Endpoints

### GET `/api/admin/stats`
Get dashboard statistics for monitoring.

**Response:**
```json
{
  "total_chats": 150,
  "total_appointments": 45,
  "common_queries": [
    {
      "intent": "faq",
      "count": 60
    },
    {
      "intent": "appointment",
      "count": 45
    }
  ],
  "recent_chats": [
    {
      "id": 1,
      "session_id": "user123",
      "message": "Hello",
      "response": "Hi! How can I help?",
      "intent": "greeting",
      "timestamp": "2026-04-21T10:00:00"
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/api/admin/stats
```

### GET `/api/admin/chats`
Get chat history with pagination.

**Query Parameters:**
- `limit` (integer, optional): Number of records to return (default: 50)
- `offset` (integer, optional): Offset for pagination (default: 0)

**Response:**
```json
{
  "chats": [
    {
      "id": 1,
      "session_id": "user123",
      "user_id": null,
      "message": "Hello",
      "response": "Hi! How can I help?",
      "intent": "greeting",
      "timestamp": "2026-04-21T10:00:00"
    }
  ],
  "total": 150
}
```

**Example:**
```bash
curl "http://localhost:8000/api/admin/chats?limit=20&offset=0"
```

### GET `/api/admin/appointments`
Get all appointments with optional date filter.

**Query Parameters:**
- `date` (string, optional): Filter by date (YYYY-MM-DD)

**Response:**
```json
{
  "appointments": [
    {
      "id": 1,
      "patient_name": "Ahmed Ali",
      "doctor_id": 1,
      "doctor_name": "Ahmed Khan",
      "specialty": "Cardiology",
      "date": "2026-04-25",
      "time": "10:00",
      "phone": "+92-300-1234567",
      "reason": "Checkup",
      "status": "confirmed",
      "created_at": "2026-04-21T10:00:00"
    }
  ]
}
```

**Example:**
```bash
# Get all appointments
curl http://localhost:8000/api/admin/appointments

# Get appointments for specific date
curl "http://localhost:8000/api/admin/appointments?date=2026-04-25"
```

---

## 🔹 Health Check

### GET `/health`
Check if the API is running and all services are healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-21T10:00:00",
  "services": {
    "database": true,
    "rag_system": true,
    "intent_classifier": true
  }
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

## 📊 Intent Types

The chatbot classifies messages into these intents:

| Intent | Description | Example Messages |
|--------|-------------|------------------|
| `appointment` | Booking, scheduling, cancellation | "I want to book appointment", "Cancel my appointment" |
| `faq` | General questions about hospital | "What services do you offer?", "What are your timings?" |
| `symptom` | Health-related queries | "I have a headache", "I feel dizzy" |
| `greeting` | Greetings and thanks | "Hello", "Thank you", "Good morning" |

---

## 🔒 Error Responses

All endpoints return standard HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## 💡 Usage Examples

### Complete Appointment Booking Flow

```python
import requests

base_url = "http://localhost:8000"
session_id = "user-12345"

# Step 1: Initiate booking
response = requests.post(f"{base_url}/api/chat", json={
    "message": "I want to book an appointment",
    "session_id": session_id
})
print(response.json()['response'])

# Step 2: Provide name
response = requests.post(f"{base_url}/api/chat", json={
    "message": "My name is Ahmed Ali",
    "session_id": session_id
})
print(response.json()['response'])

# Step 3: Select doctor
response = requests.post(f"{base_url}/api/chat", json={
    "message": "I want to see a cardiologist",
    "session_id": session_id
})
print(response.json()['response'])

# Step 4: Choose date
response = requests.post(f"{base_url}/api/chat", json={
    "message": "2026-04-25",
    "session_id": session_id
})
print(response.json()['response'])

# Step 5: Choose time
response = requests.post(f"{base_url}/api/chat", json={
    "message": "10:00",
    "session_id": session_id
})
print(response.json()['response'])

# Step 6: Provide phone
response = requests.post(f"{base_url}/api/chat", json={
    "message": "+92-300-1234567",
    "session_id": session_id
})
print(response.json()['response'])  # Booking confirmation
```

### FAQ Query

```python
response = requests.post(f"{base_url}/api/chat", json={
    "message": "Do you have a cardiologist?",
    "session_id": "user-12345"
})
print(response.json()['response'])
```

### Symptom Check

```python
response = requests.post(f"{base_url}/api/chat", json={
    "message": "I have chest pain",
    "session_id": "user-12345"
})
data = response.json()
print(f"Severity: {data['metadata']['severity']}")
print(f"Response: {data['response']}")
```

---

## 🔗 Interactive API Documentation

Visit `http://localhost:8000/docs` for:
- Interactive API testing
- Request/response schemas
- Try-it-out functionality
- Complete endpoint documentation

Alternative documentation: `http://localhost:8000/redoc`

---

## 📝 Notes

1. **Session Management**: Use consistent `session_id` for multi-turn conversations
2. **Rate Limiting**: Production API should implement rate limiting
3. **CORS**: Configure `ALLOWED_ORIGINS` in `.env` for frontend domains
4. **Timezone**: All timestamps are in UTC
5. **Date Format**: Use ISO 8601 format (YYYY-MM-DD) for dates
6. **Time Format**: Use 24-hour format (HH:MM) for times

---

## 🆘 Support

For issues or questions:
1. Check the [README.md](README.md)
2. Review the [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
3. Test with [test_system.py](test_system.py)
4. Check logs for detailed error information
