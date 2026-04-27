"""
Database Module
Handles all database operations using SQLite
In production, replace with PostgreSQL or MySQL
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

class Database:
    def __init__(self, db_path: str = "hospital_chatbot.db"):
        self.db_path = db_path
        self.connection = None
    
    def initialize(self):
        """Initialize database and create tables"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        cursor = self.connection.cursor()
        
        # Create doctors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialty TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                available_days TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create appointments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                doctor_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                phone TEXT,
                reason TEXT,
                status TEXT DEFAULT 'confirmed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES doctors (id)
            )
        ''')
        
        # Create chat logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id TEXT,
                message TEXT NOT NULL,
                response TEXT,
                intent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create users table (optional)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT UNIQUE,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.connection.commit()
        
        # Insert sample doctors if table is empty
        cursor.execute('SELECT COUNT(*) FROM doctors')
        if cursor.fetchone()[0] == 0:
            self._insert_sample_data()
        
        print("✅ Database initialized successfully")
    
    def _insert_sample_data(self):
        """Insert sample doctors data"""
        sample_doctors = [
            ("Ahmed Khan", "Cardiology", "+92-300-1234567", "ahmed.khan@hospital.com", "Mon,Tue,Wed,Thu,Fri"),
            ("Sara Ali", "Orthopedics", "+92-300-2234567", "sara.ali@hospital.com", "Mon,Tue,Wed,Thu,Fri,Sat"),
            ("Hassan Raza", "Neurology", "+92-300-3234567", "hassan.raza@hospital.com", "Mon,Wed,Fri"),
            ("Fatima Sheikh", "Pediatrics", "+92-300-4234567", "fatima.sheikh@hospital.com", "Mon,Tue,Wed,Thu,Fri"),
            ("Ayesha Malik", "Gynecology", "+92-300-5234567", "ayesha.malik@hospital.com", "Tue,Thu,Sat"),
            ("Imran Yousaf", "General Surgery", "+92-300-6234567", "imran.yousaf@hospital.com", "Mon,Tue,Wed,Thu,Fri"),
            ("Bilal Ahmad", "ENT", "+92-300-7234567", "bilal.ahmad@hospital.com", "Mon,Wed,Fri,Sat"),
        ]
        
        cursor = self.connection.cursor()
        cursor.executemany(
            'INSERT INTO doctors (name, specialty, phone, email, available_days) VALUES (?, ?, ?, ?, ?)',
            sample_doctors
        )
        self.connection.commit()
        print(f"✅ Inserted {len(sample_doctors)} sample doctors")
    
    # ==================== DOCTOR OPERATIONS ====================
    
    def get_doctors(self) -> List[Dict]:
        """Get all doctors"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM doctors')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_doctor_by_id(self, doctor_id: int) -> Optional[Dict]:
        """Get doctor by ID"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM doctors WHERE id = ?', (doctor_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_doctors_by_specialty(self, specialty: str) -> List[Dict]:
        """Get doctors by specialty"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM doctors WHERE specialty LIKE ?', (f'%{specialty}%',))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # ==================== APPOINTMENT OPERATIONS ====================
    
    def create_appointment(self, appointment_data: Dict) -> int:
        """Create new appointment and return appointment ID"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO appointments 
            (patient_name, doctor_id, date, time, phone, reason, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            appointment_data['patient_name'],
            appointment_data['doctor_id'],
            appointment_data['date'],
            appointment_data['time'],
            appointment_data.get('phone'),
            appointment_data.get('reason'),
            appointment_data.get('status', 'confirmed')
        ))
        self.connection.commit()
        return cursor.lastrowid
    
    def get_appointments(self, date: Optional[str] = None) -> List[Dict]:
        """Get all appointments, optionally filtered by date"""
        cursor = self.connection.cursor()
        
        if date:
            query = '''
                SELECT a.*, d.name as doctor_name, d.specialty 
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.id
                WHERE a.date = ?
                ORDER BY a.date, a.time
            '''
            cursor.execute(query, (date,))
        else:
            query = '''
                SELECT a.*, d.name as doctor_name, d.specialty 
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.id
                ORDER BY a.date DESC, a.time DESC
                LIMIT 100
            '''
            cursor.execute(query)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_appointments_by_doctor_date(self, doctor_id: int, date: str) -> List[Dict]:
        """Get appointments for specific doctor on specific date"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM appointments 
            WHERE doctor_id = ? AND date = ? AND status != 'cancelled'
        ''', (doctor_id, date))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_appointment_by_id(self, appointment_id: int) -> Optional[Dict]:
        """Get appointment by ID"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT a.*, d.name as doctor_name, d.specialty 
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.id = ?
        ''', (appointment_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def cancel_appointment(self, appointment_id: int) -> bool:
        """Cancel appointment"""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE appointments 
            SET status = 'cancelled' 
            WHERE id = ?
        ''', (appointment_id,))
        self.connection.commit()
        return cursor.rowcount > 0
    
    def update_appointment(self, appointment_id: int, updates: Dict) -> bool:
        """Update appointment details"""
        allowed_fields = ['date', 'time', 'phone', 'reason', 'status']
        update_parts = []
        values = []
        
        for field in allowed_fields:
            if field in updates:
                update_parts.append(f"{field} = ?")
                values.append(updates[field])
        
        if not update_parts:
            return False
        
        values.append(appointment_id)
        query = f"UPDATE appointments SET {', '.join(update_parts)} WHERE id = ?"
        
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        return cursor.rowcount > 0
    
    # ==================== CHAT LOG OPERATIONS ====================
    
    def log_chat(self, session_id: str, message: str, user_id: Optional[str] = None, 
                 timestamp: Optional[datetime] = None) -> int:
        """Log user message and return chat ID"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO chat_logs (session_id, user_id, message, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (session_id, user_id, message, timestamp or datetime.now()))
        self.connection.commit()
        return cursor.lastrowid
    
    def log_response(self, chat_id: int, response: str, intent: str):
        """Update chat log with response and intent"""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE chat_logs 
            SET response = ?, intent = ?
            WHERE id = ?
        ''', (response, intent, chat_id))
        self.connection.commit()
    
    def get_chat_history(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get chat history with pagination"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM chat_logs 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_chats_by_session(self, session_id: str) -> List[Dict]:
        """Get all chats for a specific session"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM chat_logs 
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # ==================== ADMIN STATS ====================
    
    def get_admin_stats(self) -> Dict:
        """Get statistics for admin dashboard"""
        cursor = self.connection.cursor()
        
        # Total chats
        cursor.execute('SELECT COUNT(*) as count FROM chat_logs')
        total_chats = cursor.fetchone()['count']
        
        # Total appointments
        cursor.execute('SELECT COUNT(*) as count FROM appointments WHERE status != "cancelled"')
        total_appointments = cursor.fetchone()['count']
        
        # Common queries (top intents)
        cursor.execute('''
            SELECT intent, COUNT(*) as count 
            FROM chat_logs 
            WHERE intent IS NOT NULL
            GROUP BY intent 
            ORDER BY count DESC 
            LIMIT 5
        ''')
        common_queries = [dict(row) for row in cursor.fetchall()]
        
        # Recent chats
        cursor.execute('''
            SELECT * FROM chat_logs 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        recent_chats = [dict(row) for row in cursor.fetchall()]
        
        return {
            'total_chats': total_chats,
            'total_appointments': total_appointments,
            'common_queries': common_queries,
            'recent_chats': recent_chats
        }
    
    def get_appointment_stats(self) -> Dict:
        """Get appointment statistics"""
        cursor = self.connection.cursor()
        
        # Appointments by status
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM appointments 
            GROUP BY status
        ''')
        by_status = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Appointments by doctor
        cursor.execute('''
            SELECT d.name, d.specialty, COUNT(a.id) as count 
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.status != 'cancelled'
            GROUP BY d.id
            ORDER BY count DESC
        ''')
        by_doctor = [dict(row) for row in cursor.fetchall()]
        
        return {
            'by_status': by_status,
            'by_doctor': by_doctor
        }
    
    # ==================== UTILITY FUNCTIONS ====================
    
    def check_connection(self) -> bool:
        """Check if database connection is active"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT 1')
            return True
        except:
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()


# ==================== PRODUCTION NOTES ====================
"""
For production deployment:

1. Use PostgreSQL or MySQL instead of SQLite
   - Better concurrent access
   - More robust for production
   - Better performance at scale

2. Add proper indexing:
   - CREATE INDEX idx_appointments_date ON appointments(date);
   - CREATE INDEX idx_appointments_doctor ON appointments(doctor_id);
   - CREATE INDEX idx_chat_logs_session ON chat_logs(session_id);

3. Implement connection pooling:
   - Use SQLAlchemy or similar ORM
   - Connection pool for better performance

4. Add data validation:
   - Validate phone numbers
   - Validate email formats
   - Validate date/time formats

5. Security:
   - Parameterized queries (already implemented)
   - Input sanitization
   - SQL injection prevention
   - Encrypt sensitive data

6. Backup and recovery:
   - Regular database backups
   - Transaction logs
   - Point-in-time recovery

7. Monitoring:
   - Query performance monitoring
   - Connection pool monitoring
   - Error logging
"""
