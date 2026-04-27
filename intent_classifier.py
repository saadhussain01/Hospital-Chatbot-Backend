"""
Intent Classification Module
Determines user intent from message using rule-based + keyword matching
"""

import re
from typing import Dict

class IntentClassifier:
    def __init__(self):
        # Define keyword patterns for each intent
        self.intent_patterns = {
            "appointment": [
                r'\b(book|schedule|appointment|appoint|reserve|slot)\b',
                r'\b(doctor|physician|specialist|consultation)\b.*\b(when|time|date|available)\b',
                r'\b(cancel|reschedule|change)\b.*\b(appointment)\b',
                r'\bsee\s+(a\s+)?doctor\b',
            ],
            "symptom": [
                r'\b(pain|ache|hurt|sore)\b',
                r'\b(fever|temperature|cold|cough|flu)\b',
                r'\b(headache|migraine|dizzy|nausea)\b',
                r'\b(symptom|sick|ill|unwell|feeling)\b',
                r'\b(chest pain|stomach ache|back pain)\b',
                r'\b(vomit|diarrhea|constipation)\b',
                r'\bi\s+(have|feel|am\s+having)\b',
            ],
            "faq": [
                r'\b(service|facility|department|specialist)\b',
                r'\b(timing|hours|open|close)\b',
                r'\b(location|address|where|direction)\b',
                r'\b(cost|price|fee|charge|insurance)\b',
                r'\b(doctor|staff|nurse)\b',
                r'\b(visit|visiting|visitor)\b',
                r'\b(emergency|ambulance)\b',
                r'\bdo\s+you\s+(have|offer|provide)\b',
                r'\bwhat\s+(is|are)\b',
            ],
            "greeting": [
                r'\b(hi|hello|hey|greetings)\b',
                r'\bgood\s+(morning|afternoon|evening)\b',
                r'\b(thank|thanks)\b',
            ]
        }
        
        # Priority order (check in this order)
        self.intent_priority = ["appointment", "symptom", "faq", "greeting"]
    
    def classify(self, message: str) -> str:
        """
        Classify user message into intent category
        Returns: intent name (appointment/symptom/faq/greeting/unknown)
        """
        message = message.lower().strip()
        
        # Check each intent in priority order
        for intent in self.intent_priority:
            patterns = self.intent_patterns.get(intent, [])
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return intent
        
        # Default to faq if no match
        return "faq"
    
    def get_confidence(self, message: str, intent: str) -> float:
        """
        Calculate confidence score for classified intent
        Returns: confidence score between 0 and 1
        """
        message = message.lower()
        patterns = self.intent_patterns.get(intent, [])
        
        matches = 0
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                matches += 1
        
        if len(patterns) == 0:
            return 0.0
        
        return min(matches / len(patterns), 1.0)
