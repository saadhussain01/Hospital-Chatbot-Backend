"""
Test Script for Hospital Chatbot Backend
Run this to verify all components are working
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_health_check():
    """Test health endpoint"""
    print_header("Testing Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_get_doctors():
    """Test getting doctors list"""
    print_header("Testing Get Doctors")
    response = requests.get(f"{BASE_URL}/api/doctors")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data['doctors'])} doctors:")
    for doctor in data['doctors']:
        print(f"  - Dr. {doctor['name']} ({doctor['specialty']})")
    return response.status_code == 200

def test_chat_greeting():
    """Test chat with greeting"""
    print_header("Testing Chat - Greeting")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Hello!",
        "session_id": "test-session-1"
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Intent: {data['intent']}")
    print(f"Response: {data['response']}")
    return response.status_code == 200

def test_chat_faq():
    """Test chat with FAQ question"""
    print_header("Testing Chat - FAQ")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "What services does the hospital offer?",
        "session_id": "test-session-2"
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Intent: {data['intent']}")
    print(f"Response: {data['response'][:200]}...")
    return response.status_code == 200

def test_chat_symptom():
    """Test chat with symptom"""
    print_header("Testing Chat - Symptom Check")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "I have a headache and feel dizzy",
        "session_id": "test-session-3"
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Intent: {data['intent']}")
    print(f"Severity: {data.get('metadata', {}).get('severity', 'N/A')}")
    print(f"Response: {data['response'][:200]}...")
    return response.status_code == 200

def test_chat_appointment_flow():
    """Test full appointment booking flow"""
    print_header("Testing Appointment Booking Flow")
    
    session_id = "test-session-appointment"
    
    # Step 1: Initial request
    print("\n1. User: 'I want to book an appointment'")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "I want to book an appointment",
        "session_id": session_id
    })
    data = response.json()
    print(f"   Bot: {data['response'][:100]}...")
    
    # Step 2: Provide name
    print("\n2. User: 'My name is Ahmed Ali'")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Ahmed Ali",
        "session_id": session_id
    })
    data = response.json()
    print(f"   Bot: {data['response'][:100]}...")
    
    # Step 3: Select doctor
    print("\n3. User: 'I want to see the cardiologist'")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "cardiologist",
        "session_id": session_id
    })
    data = response.json()
    print(f"   Bot: {data['response'][:100]}...")
    
    # Step 4: Provide date
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"\n4. User: '{tomorrow}'")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": tomorrow,
        "session_id": session_id
    })
    data = response.json()
    print(f"   Bot: {data['response'][:100]}...")
    
    # Step 5: Select time
    print("\n5. User: '10:00'")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "10:00",
        "session_id": session_id
    })
    data = response.json()
    print(f"   Bot: {data['response'][:100]}...")
    
    # Step 6: Provide phone
    print("\n6. User: '+92-300-1234567'")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "+92-300-1234567",
        "session_id": session_id
    })
    data = response.json()
    print(f"   Bot: {data['response'][:200]}...")
    
    return response.status_code == 200

def test_get_availability():
    """Test doctor availability check"""
    print_header("Testing Doctor Availability")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    response = requests.get(
        f"{BASE_URL}/api/appointments/availability",
        params={"doctor_id": 1, "date": tomorrow}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Available slots for {tomorrow}:")
    print(f"  {', '.join(data['available_slots'][:5])}...")
    return response.status_code == 200

def test_admin_stats():
    """Test admin statistics"""
    print_header("Testing Admin Statistics")
    response = requests.get(f"{BASE_URL}/api/admin/stats")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total Chats: {data['total_chats']}")
    print(f"Total Appointments: {data['total_appointments']}")
    print(f"Common Queries:")
    for query in data['common_queries']:
        print(f"  - {query['intent']}: {query['count']} times")
    return response.status_code == 200

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "HOSPITAL CHATBOT BACKEND TEST SUITE" + " "*12 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Health Check", test_health_check),
        ("Get Doctors", test_get_doctors),
        ("Chat - Greeting", test_chat_greeting),
        ("Chat - FAQ", test_chat_faq),
        ("Chat - Symptom", test_chat_symptom),
        ("Appointment Flow", test_chat_appointment_flow),
        ("Doctor Availability", test_get_availability),
        ("Admin Statistics", test_admin_stats),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}")
            results.append((name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    return passed == total

if __name__ == "__main__":
    print("\n⚠️  Make sure the backend server is running at http://localhost:8000")
    print("   Run: python main.py\n")
    
    input("Press Enter to start tests...")
    
    success = run_all_tests()
    
    if success:
        print("✨ All tests passed! System is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
