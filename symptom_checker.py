"""
Symptom Checker Module
Provides SAFE symptom guidance with strict medical disclaimers
NEVER provides diagnosis - only suggests departments and emphasizes consulting doctors
"""

from typing import Dict, List
import re

class SymptomChecker:
    def __init__(self):
        # Define symptom patterns and recommended departments
        self.symptom_mapping = {
            "emergency": {
                "keywords": ["chest pain", "severe chest", "heart attack", "can't breathe", 
                           "difficulty breathing", "unconscious", "severe bleeding", 
                           "stroke", "seizure", "severe injury"],
                "department": "Emergency Department",
                "severity": "critical",
                "message": "🚨 EMERGENCY: Please seek immediate medical attention! Visit our Emergency Department NOW or call emergency services."
            },
            "cardiology": {
                "keywords": ["heart", "chest pain", "palpitation", "irregular heartbeat", 
                           "high blood pressure", "hypertension"],
                "department": "Cardiology",
                "severity": "high",
                "message": "You may need to consult our Cardiology department. Dr. Ahmed Khan can help you."
            },
            "respiratory": {
                "keywords": ["cough", "cold", "flu", "breathing", "asthma", "pneumonia",
                           "shortness of breath", "wheezing"],
                "department": "General Medicine / Pulmonology",
                "severity": "medium",
                "message": "These symptoms may require evaluation by a general physician or pulmonologist."
            },
            "orthopedics": {
                "keywords": ["bone", "fracture", "joint pain", "back pain", "knee pain",
                           "arthritis", "sprain", "injury"],
                "department": "Orthopedics",
                "severity": "medium",
                "message": "You may need to see our Orthopedic specialist, Dr. Sara Ali."
            },
            "neurology": {
                "keywords": ["headache", "migraine", "dizzy", "vertigo", "numbness",
                           "tingling", "seizure", "memory loss"],
                "department": "Neurology",
                "severity": "medium",
                "message": "These symptoms should be evaluated by our Neurology department. Dr. Hassan Raza can assist you."
            },
            "gastro": {
                "keywords": ["stomach", "abdominal pain", "nausea", "vomit", "diarrhea",
                           "constipation", "indigestion", "acid reflux"],
                "department": "Gastroenterology / General Medicine",
                "severity": "medium",
                "message": "You may need consultation for gastrointestinal issues with our general physician."
            },
            "ent": {
                "keywords": ["ear", "nose", "throat", "sore throat", "tonsil", "hearing",
                           "sinus", "nasal"],
                "department": "ENT (Ear, Nose, Throat)",
                "severity": "low",
                "message": "These symptoms can be evaluated by our ENT specialist, Dr. Bilal Ahmad."
            },
            "pediatrics": {
                "keywords": ["child", "baby", "infant", "kid", "pediatric"],
                "department": "Pediatrics",
                "severity": "medium",
                "message": "For children's health concerns, please consult our Pediatrics department. Dr. Fatima Sheikh specializes in child care."
            },
            "gynecology": {
                "keywords": ["pregnancy", "pregnant", "menstrual", "period", "ovarian",
                           "uterus", "gynec", "women health"],
                "department": "Obstetrics & Gynecology",
                "severity": "medium",
                "message": "Please consult our Gynecology department. Dr. Ayesha Malik is available for women's health concerns."
            },
            "general": {
                "keywords": ["fever", "fatigue", "tired", "weak", "general checkup",
                           "routine checkup", "health screening"],
                "department": "General Medicine",
                "severity": "low",
                "message": "You may need a general health consultation. Our general physicians can help with overall health assessment."
            }
        }
        
        # Critical symptoms that need immediate attention
        self.critical_symptoms = [
            "chest pain", "severe pain", "can't breathe", "unconscious",
            "severe bleeding", "stroke", "heart attack", "suicide"
        ]
    
    def process(self, message: str) -> Dict:
        """
        Process symptom query and provide safe guidance
        
        Returns:
        - response: Safe guidance message
        - severity: critical/high/medium/low
        - department: Recommended department
        """
        message_lower = message.lower()
        
        # Check for critical symptoms first
        if self._is_critical(message_lower):
            return {
                "response": self._get_emergency_response(),
                "severity": "critical",
                "department": "Emergency",
                "requires_immediate_action": True
            }
        
        # Find matching symptom category
        matched_category = self._match_symptom_category(message_lower)
        
        if matched_category:
            category_info = self.symptom_mapping[matched_category]
            
            response = self._generate_response(
                message=message,
                department=category_info["department"],
                guidance=category_info["message"],
                severity=category_info["severity"]
            )
            
            return {
                "response": response,
                "severity": category_info["severity"],
                "department": category_info["department"],
                "requires_immediate_action": category_info["severity"] == "critical"
            }
        else:
            # No specific match - give general advice
            return {
                "response": self._get_general_response(),
                "severity": "low",
                "department": "General Medicine",
                "requires_immediate_action": False
            }
    
    def _is_critical(self, message: str) -> bool:
        """Check if message contains critical symptoms"""
        for symptom in self.critical_symptoms:
            if symptom in message:
                return True
        return False
    
    def _match_symptom_category(self, message: str) -> str:
        """Find the best matching symptom category"""
        best_match = None
        max_matches = 0
        
        for category, info in self.symptom_mapping.items():
            match_count = sum(1 for keyword in info["keywords"] if keyword in message)
            
            if match_count > max_matches:
                max_matches = match_count
                best_match = category
        
        return best_match if max_matches > 0 else None
    
    def _generate_response(self, message: str, department: str, 
                          guidance: str, severity: str) -> str:
        """Generate safe, helpful response"""
        
        # Start with empathy
        response = "I understand you're experiencing health concerns. "
        
        # Add severity-based urgency
        if severity == "high":
            response += "⚠️ This may need prompt medical attention.\n\n"
        elif severity == "critical":
            response += "🚨 This requires IMMEDIATE medical attention!\n\n"
        else:
            response += "\n\n"
        
        # Add guidance
        response += guidance
        
        # Add booking assistance
        response += f"\n\n📅 Would you like me to help you book an appointment with {department}?"
        
        return response
    
    def _get_emergency_response(self) -> str:
        """Generate emergency response for critical symptoms"""
        return """🚨 EMERGENCY ALERT 🚨

This appears to be a CRITICAL medical situation that requires IMMEDIATE attention.

⚡ TAKE ACTION NOW:
1. Visit our Emergency Department immediately
2. Call emergency services: [Emergency Number]
3. Do NOT delay seeking medical help

Our Emergency Department is open 24/7 and located at the main entrance.

🏥 For life-threatening emergencies, please call emergency services or go to the nearest hospital immediately."""
    
    def _get_general_response(self) -> str:
        """Generate general response when no specific match found"""
        return """I understand you have health concerns. While I can provide general guidance, I recommend consulting with a healthcare professional for proper evaluation.

Our hospital offers:
• General Medicine - for overall health concerns
• Specialist consultations - for specific conditions
• 24/7 Emergency care - for urgent situations

Would you like me to help you book an appointment with a doctor?"""
    
    def extract_symptoms(self, message: str) -> List[str]:
        """Extract symptom keywords from message (for logging/analysis)"""
        message_lower = message.lower()
        found_symptoms = []
        
        for category, info in self.symptom_mapping.items():
            for keyword in info["keywords"]:
                if keyword in message_lower and keyword not in found_symptoms:
                    found_symptoms.append(keyword)
        
        return found_symptoms
    
    def get_disclaimer(self) -> str:
        """Return medical disclaimer"""
        return """
⚠️ IMPORTANT MEDICAL DISCLAIMER:

This chatbot provides general health information only and is NOT a substitute for professional medical advice, diagnosis, or treatment.

• Always consult a qualified healthcare provider for medical concerns
• This system does not provide medical diagnoses
• In case of emergency, seek immediate medical attention
• Information provided is for educational purposes only

If you have any health concerns, please schedule an appointment with our medical professionals."""


# ==================== SAFETY NOTES ====================
"""
CRITICAL SAFETY RULES FOR SYMPTOM CHECKING:

1. NEVER provide diagnosis
   - Only suggest departments
   - Always recommend consulting doctor
   
2. ALWAYS include disclaimers
   - Not a substitute for medical advice
   - Educational purposes only
   
3. ESCALATE critical cases
   - Chest pain → Emergency
   - Difficulty breathing → Emergency
   - Severe bleeding → Emergency
   
4. LOG all symptom queries
   - For quality monitoring
   - For improving accuracy
   - For liability protection
   
5. HUMAN OVERSIGHT required
   - Medical professional should review
   - Update symptom mappings regularly
   - Monitor for misuse

This is a GUIDANCE tool, not a DIAGNOSTIC tool.
"""
