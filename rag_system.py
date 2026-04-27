"""
RAG (Retrieval-Augmented Generation) System
Answers FAQ using hospital knowledge base + embeddings + LLM
"""

import os
import json
from typing import List, Dict, Optional
import numpy as np

# Note: In production, use actual OpenAI API or local models
# This is a simplified implementation showing the architecture

class RAGSystem:
    def __init__(self):
        self.knowledge_base = []
        self.embeddings = []
        self.is_loaded = False
        
        # In production, initialize actual embedding model
        # from sentence_transformers import SentenceTransformer
        # self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def load_knowledge_base(self):
        """Load hospital knowledge base and create embeddings"""
        
        # Hospital knowledge base (in production, load from files/database)
        self.knowledge_base = [
            {
                "id": 1,
                "question": "What services does the hospital offer?",
                "answer": "Our hospital offers comprehensive healthcare services including: Emergency Care (24/7), Cardiology, Orthopedics, Neurology, Pediatrics, Obstetrics & Gynecology, General Surgery, Radiology & Imaging, Laboratory Services, Physiotherapy, and Pharmacy Services.",
                "category": "services"
            },
            {
                "id": 2,
                "question": "What are the hospital timings?",
                "answer": "Our hospital operates 24/7 for emergency services. OPD (Outpatient Department) hours are Monday to Saturday, 9:00 AM to 5:00 PM. The emergency department is always open.",
                "category": "timings"
            },
            {
                "id": 3,
                "question": "Do you have a cardiologist?",
                "answer": "Yes, we have experienced cardiologists available. Dr. Ahmed Khan specializes in cardiology and is available for consultations Monday through Friday. You can book an appointment through our chatbot or by calling our reception.",
                "category": "doctors"
            },
            {
                "id": 4,
                "question": "What is the location of the hospital?",
                "answer": "We are located at Medical Complex, University Road, Mardan, Khyber Pakhtunkhwa. The hospital is easily accessible from the main highway and has ample parking space.",
                "category": "location"
            },
            {
                "id": 5,
                "question": "Do you accept insurance?",
                "answer": "Yes, we accept major health insurance plans including government health cards, private insurance from most major providers. Please bring your insurance card when visiting. Our billing department can help verify your coverage.",
                "category": "insurance"
            },
            {
                "id": 6,
                "question": "Is there an emergency department?",
                "answer": "Yes, we have a fully-equipped 24/7 emergency department with trauma care, critical care units, and ambulance services. In case of emergency, call our emergency hotline or visit directly.",
                "category": "emergency"
            },
            {
                "id": 7,
                "question": "What specialists are available?",
                "answer": "We have specialists in: Cardiology (Dr. Ahmed Khan), Orthopedics (Dr. Sara Ali), Neurology (Dr. Hassan Raza), Pediatrics (Dr. Fatima Sheikh), Gynecology (Dr. Ayesha Malik), General Surgery (Dr. Imran Yousaf), and ENT (Dr. Bilal Ahmad).",
                "category": "doctors"
            },
            {
                "id": 8,
                "question": "How do I book an appointment?",
                "answer": "You can book appointments through: 1) This chatbot - just say 'I want to book an appointment', 2) Calling our reception at the hospital number, 3) Visiting the hospital in person. Online booking through chatbot is the fastest method.",
                "category": "appointments"
            },
            {
                "id": 9,
                "question": "What diagnostic facilities are available?",
                "answer": "We have state-of-the-art diagnostic facilities including: X-Ray, CT Scan, MRI, Ultrasound, ECG, Echo, Complete Blood Count (CBC), Biochemistry tests, Microbiology lab, and Pathology services. Most tests can be done same-day.",
                "category": "diagnostics"
            },
            {
                "id": 10,
                "question": "Do you have pharmacy services?",
                "answer": "Yes, we have an in-house pharmacy that stocks a wide range of medicines and is open during hospital hours. Prescriptions from our doctors can be filled immediately. We also provide home delivery for chronic medications.",
                "category": "pharmacy"
            },
            {
                "id": 11,
                "question": "What are the visiting hours?",
                "answer": "Visiting hours are 4:00 PM to 7:00 PM daily for general wards. ICU visiting hours are restricted to 2:00 PM to 3:00 PM. Only two visitors per patient allowed at a time. Please follow hospital hygiene protocols.",
                "category": "visiting"
            },
            {
                "id": 12,
                "question": "Is there parking available?",
                "answer": "Yes, we have a large parking facility for both visitors and patients. Parking is free for the first 2 hours and nominal charges apply thereafter. Disabled parking spots are available near the main entrance.",
                "category": "facilities"
            }
        ]
        
        # In production, generate actual embeddings
        # for item in self.knowledge_base:
        #     text = f"{item['question']} {item['answer']}"
        #     embedding = self.embedding_model.encode(text)
        #     self.embeddings.append(embedding)
        
        # For this demo, use simple keyword matching
        self.is_loaded = True
        
        print(f"✅ Loaded {len(self.knowledge_base)} knowledge base entries")
    
    def query(self, user_question: str) -> str:
        """
        Query the knowledge base and generate answer using RAG
        
        Process:
        1. Convert question to embedding
        2. Find most relevant documents (vector similarity)
        3. Pass to LLM with context
        4. Generate answer
        """
        if not self.is_loaded:
            return "Knowledge base not loaded. Please try again later."
        
        # Step 1: Find relevant documents (simplified keyword matching)
        relevant_docs = self._retrieve_relevant_documents(user_question)
        
        if not relevant_docs:
            return "I don't have specific information about that. Please contact our reception for detailed information, or ask about our services, timings, doctors, or facilities."
        
        # Step 2: Generate answer (in production, use actual LLM)
        answer = self._generate_answer(user_question, relevant_docs)
        
        return answer
    
    def _retrieve_relevant_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve most relevant documents from knowledge base
        In production, use vector similarity search
        """
        query_lower = query.lower()
        
        # Score each document based on keyword matching
        scored_docs = []
        for doc in self.knowledge_base:
            score = self._calculate_relevance_score(query_lower, doc)
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and return top_k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]
    
    def _calculate_relevance_score(self, query: str, doc: Dict) -> float:
        """Calculate relevance score using keyword matching (simplified)"""
        score = 0.0
        doc_text = f"{doc['question']} {doc['answer']}".lower()
        
        # Split query into words
        query_words = set(query.split())
        
        # Count matching words
        for word in query_words:
            if len(word) > 3 and word in doc_text:  # Ignore short words
                score += 1
        
        # Boost if category keyword matches
        if doc['category'] in query:
            score += 2
        
        return score
    
    def _generate_answer(self, question: str, relevant_docs: List[Dict]) -> str:
        """
        Generate answer using LLM with retrieved context
        In production, call actual LLM API (OpenAI, Claude, etc.)
        """
        
        # For production, use this pattern:
        # context = "\n\n".join([f"Q: {doc['question']}\nA: {doc['answer']}" for doc in relevant_docs])
        # 
        # prompt = f"""You are a helpful hospital assistant. Answer the user's question based on the following information.
        # 
        # Context:
        # {context}
        # 
        # User Question: {question}
        # 
        # Provide a helpful, accurate answer based on the context. If the context doesn't contain the answer, say so politely.
        # """
        # 
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # 
        # return response.choices[0].message.content
        
        # Simplified version: return most relevant answer
        if relevant_docs:
            best_match = relevant_docs[0]
            answer = best_match['answer']
            
            # Add related information if available
            if len(relevant_docs) > 1:
                answer += "\n\n📌 Related information:\n"
                for doc in relevant_docs[1:]:
                    answer += f"• {doc['answer'][:100]}...\n"
            
            return answer
        
        return "I don't have specific information about that. Please contact our reception for more details."
    
    def add_to_knowledge_base(self, question: str, answer: str, category: str = "general"):
        """Add new entry to knowledge base (for admin updates)"""
        new_id = max([item['id'] for item in self.knowledge_base]) + 1 if self.knowledge_base else 1
        
        new_entry = {
            "id": new_id,
            "question": question,
            "answer": answer,
            "category": category
        }
        
        self.knowledge_base.append(new_entry)
        
        # In production, regenerate embedding
        # embedding = self.embedding_model.encode(f"{question} {answer}")
        # self.embeddings.append(embedding)
        
        return new_id
    
    def is_ready(self) -> bool:
        """Check if RAG system is ready"""
        return self.is_loaded


# ==================== PRODUCTION IMPLEMENTATION NOTES ====================
"""
For production deployment, replace simplified methods with:

1. EMBEDDINGS:
   - Use sentence-transformers or OpenAI embeddings
   - Example:
     from sentence_transformers import SentenceTransformer
     model = SentenceTransformer('all-MiniLM-L6-v2')
     embedding = model.encode(text)

2. VECTOR DATABASE:
   - Use FAISS, Pinecone, or Weaviate for similarity search
   - Example with FAISS:
     import faiss
     index = faiss.IndexFlatL2(dimension)
     index.add(embeddings)
     distances, indices = index.search(query_embedding, k=5)

3. LLM GENERATION:
   - Use OpenAI API, Anthropic Claude, or local models
   - Example with OpenAI:
     import openai
     response = openai.ChatCompletion.create(
         model="gpt-3.5-turbo",
         messages=[{"role": "system", "content": system_prompt},
                   {"role": "user", "content": user_query}]
     )

4. KNOWLEDGE BASE STORAGE:
   - Load from files (JSON, CSV) or database
   - Update embeddings when knowledge base changes
   - Cache embeddings to avoid recomputation
"""
