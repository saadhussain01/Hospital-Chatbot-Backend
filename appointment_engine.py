"""
Appointment Engine - Rule-Based Logic
Handles appointment booking, cancellation, and rescheduling
NO AI - Uses structured logic and database queries
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

class AppointmentEngine:
    def __init__(self, database):
        self.db = database
        self.conversation_state = {}  # Track multi-turn conversations
        
        # Define working hours
        self.working_hours = {
            'start': '09:00',
            'end': '17:00',
            'slot_duration': 30  # minutes
        }
    
    def process(self, message: str, session_id: str) -> Dict:
        """
        Process appointment-related message
        Uses state machine for multi-turn conversation
        """
        state = self.conversation_state.get(session_id, {})
        
        # Check for cancellation request
        if self._is_cancellation(message):
            return self._handle_cancellation(message, session_id, state)
        
        # Check for booking request
        if self._is_booking_request(message):
            return self._start_booking_flow(session_id)
        
        # Continue existing conversation flow
        if state.get('flow') == 'booking':
            return self._continue_booking_flow(message, session_id, state)
        
        # Show available options
        return {
            'response': "I can help you with:\n• Book a new appointment\n• Cancel an existing appointment\n• Check doctor availability\n\nWhat would you like to do?",
            'requires_action': False
        }
    
    def _is_booking_request(self, message: str) -> bool:
        """Check if message is requesting to book appointment"""
        patterns = [
            r'\b(book|schedule|make|get)\b.*\b(appointment|slot)\b',
            r'\bsee\s+(a\s+)?doctor\b',
            r'\bwant\s+to\s+(book|schedule)\b'
        ]
        return any(re.search(p, message, re.IGNORECASE) for p in patterns)
    
    def _is_cancellation(self, message: str) -> bool:
        """Check if message is requesting cancellation"""
        patterns = [
            r'\b(cancel|delete|remove)\b.*\b(appointment)\b',
            r'\bcancel\s+my\s+appointment\b'
        ]
        return any(re.search(p, message, re.IGNORECASE) for p in patterns)
    
    def _start_booking_flow(self, session_id: str) -> Dict:
        """Start the appointment booking conversation flow"""
        self.conversation_state[session_id] = {
            'flow': 'booking',
            'step': 'ask_name',
            'data': {}
        }
        
        return {
            'response': "I'd be happy to help you book an appointment! 📅\n\nMay I have your name, please?",
            'requires_action': True,
            'action_type': 'collect_name'
        }
    
    def _continue_booking_flow(self, message: str, session_id: str, state: Dict) -> Dict:
        """Continue multi-step booking conversation"""
        step = state.get('step')
        data = state.get('data', {})
        
        if step == 'ask_name':
            # Extract name
            name = message.strip()
            data['patient_name'] = name
            
            # Get list of doctors
            doctors = self.db.get_doctors()
            doctor_list = "\n".join([f"{d['id']}. Dr. {d['name']} - {d['specialty']}" for d in doctors])
            
            state['step'] = 'ask_doctor'
            state['data'] = data
            self.conversation_state[session_id] = state
            
            return {
                'response': f"Thank you, {name}! 👋\n\nWhich doctor would you like to see?\n\n{doctor_list}\n\nPlease select a number or tell me the specialty you need.",
                'requires_action': True,
                'action_type': 'collect_doctor',
                'metadata': {'doctors': doctors}
            }
        
        elif step == 'ask_doctor':
            # Extract doctor selection
            doctor_id = self._extract_doctor_id(message, self.db.get_doctors())
            
            if not doctor_id:
                return {
                    'response': "I couldn't identify the doctor. Please provide the number or specialty.",
                    'requires_action': True,
                    'action_type': 'collect_doctor'
                }
            
            data['doctor_id'] = doctor_id
            doctor = self.db.get_doctor_by_id(doctor_id)
            
            state['step'] = 'ask_date'
            state['data'] = data
            self.conversation_state[session_id] = state
            
            return {
                'response': f"Great! You've selected Dr. {doctor['name']} ({doctor['specialty']}).\n\nWhat date would you prefer? (Format: YYYY-MM-DD or 'tomorrow', 'next Monday', etc.)",
                'requires_action': True,
                'action_type': 'collect_date'
            }
        
        elif step == 'ask_date':
            # Parse date
            date = self._parse_date(message)
            
            if not date:
                return {
                    'response': "I couldn't understand the date. Please provide in format YYYY-MM-DD (e.g., 2026-04-25)",
                    'requires_action': True,
                    'action_type': 'collect_date'
                }
            
            data['date'] = date
            
            # Get available slots
            slots = self.get_available_slots(data['doctor_id'], date)
            
            if not slots:
                return {
                    'response': f"Sorry, no slots available on {date}. Please choose another date.",
                    'requires_action': True,
                    'action_type': 'collect_date'
                }
            
            slots_text = ", ".join(slots)
            
            state['step'] = 'ask_time'
            state['data'] = data
            self.conversation_state[session_id] = state
            
            return {
                'response': f"Available time slots on {date}:\n\n{slots_text}\n\nWhich time works best for you?",
                'requires_action': True,
                'action_type': 'collect_time',
                'metadata': {'available_slots': slots}
            }
        
        elif step == 'ask_time':
            # Extract time
            time = self._parse_time(message)
            
            if not time:
                return {
                    'response': "Please provide a valid time (e.g., 10:00, 2:30 PM)",
                    'requires_action': True,
                    'action_type': 'collect_time'
                }
            
            data['time'] = time
            
            state['step'] = 'ask_phone'
            state['data'] = data
            self.conversation_state[session_id] = state
            
            return {
                'response': "Perfect! May I have your phone number for confirmation?",
                'requires_action': True,
                'action_type': 'collect_phone'
            }
        
        elif step == 'ask_phone':
            # Extract phone
            phone = self._extract_phone(message)
            data['phone'] = phone or message.strip()
            
            # Confirm and book
            result = self.book_appointment(
                patient_name=data['patient_name'],
                doctor_id=data['doctor_id'],
                date=data['date'],
                time=data['time'],
                phone=data['phone']
            )
            
            # Clear conversation state
            if session_id in self.conversation_state:
                del self.conversation_state[session_id]
            
            if result['success']:
                doctor = self.db.get_doctor_by_id(data['doctor_id'])
                return {
                    'response': f"✅ Appointment booked successfully!\n\n📋 Confirmation Details:\n• Patient: {data['patient_name']}\n• Doctor: Dr. {doctor['name']}\n• Date: {data['date']}\n• Time: {data['time']}\n• Appointment ID: {result['appointment_id']}\n\nYou'll receive a confirmation call at {data['phone']}.",
                    'requires_action': False,
                    'metadata': {'appointment_id': result['appointment_id']}
                }
            else:
                return {
                    'response': f"❌ Sorry, booking failed: {result['message']}\n\nPlease try again.",
                    'requires_action': False
                }
        
        return {
            'response': "Something went wrong. Let's start over. Would you like to book an appointment?",
            'requires_action': False
        }
    
    def _extract_doctor_id(self, message: str, doctors: List[Dict]) -> Optional[str]:
        """Extract doctor ID from message"""
        # Check for number (1-7 maps to doctor index)
        match = re.search(r'\b(\d+)\b', message)
        if match:
            doctor_num = int(match.group(1))
            if 1 <= doctor_num <= len(doctors):
                return doctors[doctor_num - 1]['id']  # Return MongoDB _id string
        
        # Check for specialty match
        message_lower = message.lower()
        for doctor in doctors:
            if doctor['specialty'].lower() in message_lower:
                return doctor['id']
        
        return None
    
    def _parse_date(self, message: str) -> Optional[str]:
        """Parse date from natural language or format"""
        message = message.lower().strip()
        
        # Check for relative dates
        if 'tomorrow' in message:
            date = datetime.now() + timedelta(days=1)
            return date.strftime('%Y-%m-%d')
        
        if 'today' in message:
            return datetime.now().strftime('%Y-%m-%d')
        
        # Check for explicit date format YYYY-MM-DD
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', message)
        if match:
            return match.group(0)
        
        return None
    
    def _parse_time(self, message: str) -> Optional[str]:
        """Parse time from message"""
        # Format: HH:MM or H:MM AM/PM
        match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', message, re.IGNORECASE)
        if match:
            hour = int(match.group(1))
            minute = match.group(2)
            period = match.group(3)
            
            if period:
                if period.lower() == 'pm' and hour != 12:
                    hour += 12
                elif period.lower() == 'am' and hour == 12:
                    hour = 0
            
            return f"{hour:02d}:{minute}"
        
        return None
    
    def _extract_phone(self, message: str) -> Optional[str]:
        """Extract phone number from message"""
        match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', message)
        if match:
            return match.group(0)
        return None
    
    def _handle_cancellation(self, message: str, session_id: str, state: Dict) -> Dict:
        """Handle appointment cancellation"""
        # Extract appointment ID if present
        match = re.search(r'\b(\d+)\b', message)
        
        if match:
            appointment_id = int(match.group(1))
            try:
                self.cancel_appointment(appointment_id)
                return {
                    'response': f"✅ Appointment #{appointment_id} has been cancelled successfully.",
                    'requires_action': False
                }
            except Exception as e:
                return {
                    'response': f"❌ Could not cancel appointment: {str(e)}",
                    'requires_action': False
                }
        else:
            return {
                'response': "To cancel an appointment, please provide the appointment ID.\n\nExample: 'Cancel appointment 123'",
                'requires_action': True,
                'action_type': 'collect_appointment_id'
            }
    
    def book_appointment(self, patient_name: str, doctor_id: str, 
                        date: str, time: str, phone: str = None, 
                        reason: str = None) -> Dict:
        """
        Book an appointment (RULE-BASED - NO AI)
        doctor_id is now a MongoDB ObjectId string
        """
        # Validate inputs
        if not all([patient_name, doctor_id, date, time]):
            return {
                'success': False,
                'message': 'Missing required fields'
            }
        
        # Check if slot is available
        if not self._is_slot_available(doctor_id, date, time):
            return {
                'success': False,
                'message': 'Time slot not available'
            }
        
        # Create appointment in database
        appointment_id = self.db.create_appointment({
            'patient_name': patient_name,
            'doctor_id': doctor_id,
            'date': date,
            'time': time,
            'phone': phone,
            'reason': reason,
            'status': 'confirmed',
            'created_at': datetime.now().isoformat()
        })
        
        return {
            'success': True,
            'message': 'Appointment booked successfully',
            'appointment_id': appointment_id
        }
    
    def get_available_slots(self, doctor_id: str, date: str) -> List[str]:
        """Get available time slots for a doctor on a specific date"""
        # Get existing appointments
        booked_slots = self.db.get_appointments_by_doctor_date(doctor_id, date)
        booked_times = [apt['time'] for apt in booked_slots]
        
        # Generate all possible slots
        all_slots = self._generate_time_slots()
        
        # Filter out booked slots
        available = [slot for slot in all_slots if slot not in booked_times]
        
        return available
    
    def _generate_time_slots(self) -> List[str]:
        """Generate all possible time slots for a day"""
        slots = []
        start_hour, start_min = map(int, self.working_hours['start'].split(':'))
        end_hour, end_min = map(int, self.working_hours['end'].split(':'))
        
        current = datetime.strptime(self.working_hours['start'], '%H:%M')
        end = datetime.strptime(self.working_hours['end'], '%H:%M')
        delta = timedelta(minutes=self.working_hours['slot_duration'])
        
        while current < end:
            slots.append(current.strftime('%H:%M'))
            current += delta
        
        return slots
    
    def _is_slot_available(self, doctor_id: str, date: str, time: str) -> bool:
        """Check if a time slot is available"""
        available_slots = self.get_available_slots(doctor_id, date)
        return time in available_slots
    
    def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment (MongoDB ObjectId string)"""
        return self.db.cancel_appointment(appointment_id)