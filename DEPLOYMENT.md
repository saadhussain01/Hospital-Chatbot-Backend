# 🚀 Production Deployment Guide

## Pre-Deployment Checklist

### 1. Environment Setup
- [ ] Set up production server (Ubuntu 20.04+ recommended)
- [ ] Install Python 3.9+
- [ ] Install PostgreSQL 13+
- [ ] Set up SSL certificates
- [ ] Configure firewall (ufw)
- [ ] Set up domain name and DNS

### 2. Security Hardening
- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_ORIGINS properly
- [ ] Enable HTTPS only
- [ ] Set up rate limiting
- [ ] Implement API authentication
- [ ] Configure CORS properly

### 3. Database Migration
- [ ] Set up PostgreSQL database
- [ ] Create database user with limited privileges
- [ ] Migrate data from SQLite (if applicable)
- [ ] Set up database backups
- [ ] Configure connection pooling

### 4. Monitoring & Logging
- [ ] Set up application logging
- [ ] Configure error tracking (Sentry)
- [ ] Set up uptime monitoring
- [ ] Configure performance monitoring
- [ ] Set up alerting

## Step-by-Step Deployment

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib supervisor

# Create application user
sudo useradd -m -s /bin/bash chatbot
sudo su - chatbot
```

### Step 2: Application Setup

```bash
# Clone repository
cd /home/chatbot
git clone <your-repo-url> hospital-chatbot
cd hospital-chatbot/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Step 3: PostgreSQL Setup

```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
createdb hospital_chatbot_db
createuser chatbot_user

# Set password and grant privileges
psql
```

```sql
ALTER USER chatbot_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE hospital_chatbot_db TO chatbot_user;
\q
```

Update `.env`:
```env
DATABASE_URL=postgresql://chatbot_user:your_secure_password@localhost:5432/hospital_chatbot_db
```

### Step 4: Migrate to PostgreSQL

Update `database.py` to use SQLAlchemy:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

Run migration:
```bash
python migrate_to_postgres.py
```

### Step 5: Nginx Configuration

Create `/etc/nginx/sites-available/hospital-chatbot`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Proxy settings
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/hospital-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Step 7: Supervisor Configuration

Create `/etc/supervisor/conf.d/hospital-chatbot.conf`:

```ini
[program:hospital-chatbot]
directory=/home/chatbot/hospital-chatbot/backend
command=/home/chatbot/hospital-chatbot/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
user=chatbot
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/hospital-chatbot/error.log
stdout_logfile=/var/log/hospital-chatbot/access.log
environment=PATH="/home/chatbot/hospital-chatbot/backend/venv/bin"
```

Create log directory:
```bash
sudo mkdir -p /var/log/hospital-chatbot
sudo chown chatbot:chatbot /var/log/hospital-chatbot
```

Start application:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start hospital-chatbot
```

### Step 8: Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## Upgrade to Production AI Components

### Install AI Dependencies

```bash
pip install openai anthropic sentence-transformers faiss-cpu transformers torch
```

### Update RAG System

Replace mock implementation in `rag_system.py`:

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import openai

class RAGSystem:
    def __init__(self):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Vector database
        self.dimension = 384  # all-MiniLM-L6-v2 dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        
    def load_knowledge_base(self):
        # Generate embeddings for all documents
        texts = [f"{doc['question']} {doc['answer']}" 
                for doc in self.knowledge_base]
        
        embeddings = self.embedding_model.encode(texts)
        self.index.add(np.array(embeddings))
        
    def _retrieve_relevant_documents(self, query: str, top_k: int = 3):
        # Convert query to embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in vector database
        distances, indices = self.index.search(
            np.array(query_embedding), 
            top_k
        )
        
        return [self.knowledge_base[i] for i in indices[0]]
    
    def _generate_answer(self, question: str, relevant_docs: List[Dict]):
        context = "\n\n".join([
            f"Q: {doc['question']}\nA: {doc['answer']}" 
            for doc in relevant_docs
        ])
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful hospital assistant."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ]
        )
        
        return response.choices[0].message.content
```

## Monitoring Setup

### Install Monitoring Tools

```bash
# Install Prometheus
sudo apt install prometheus

# Install Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana
```

### Add Prometheus Metrics to FastAPI

```bash
pip install prometheus-fastapi-instrumentator
```

In `main.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app)
```

## Database Backup

### Set up automated backups

Create `/home/chatbot/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/chatbot/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="hospital_chatbot_db"

mkdir -p $BACKUP_DIR

# Create backup
pg_dump $DB_NAME > "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /home/chatbot/backup.sh
```

## Health Monitoring

### Set up Uptime Monitoring

Use services like:
- UptimeRobot
- Pingdom
- StatusCake

Monitor endpoint: `https://your-domain.com/health`

### Error Tracking

Install Sentry:
```bash
pip install sentry-sdk[fastapi]
```

In `main.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

## Performance Optimization

### Enable Caching

```bash
pip install redis
```

### Database Indexing

```sql
CREATE INDEX idx_appointments_date ON appointments(date);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX idx_chat_logs_session ON chat_logs(session_id);
CREATE INDEX idx_chat_logs_timestamp ON chat_logs(timestamp);
```

### Connection Pooling

Use SQLAlchemy with connection pooling:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

## Maintenance

### Regular Tasks

- [ ] Monitor disk space
- [ ] Review error logs weekly
- [ ] Update dependencies monthly
- [ ] Review security patches
- [ ] Backup verification
- [ ] Performance tuning

### Log Rotation

Create `/etc/logrotate.d/hospital-chatbot`:

```
/var/log/hospital-chatbot/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 chatbot chatbot
    sharedscripts
    postrotate
        supervisorctl restart hospital-chatbot
    endscript
}
```

## Troubleshooting

### Check Application Status
```bash
sudo supervisorctl status hospital-chatbot
```

### View Logs
```bash
sudo tail -f /var/log/hospital-chatbot/error.log
sudo tail -f /var/log/hospital-chatbot/access.log
```

### Restart Application
```bash
sudo supervisorctl restart hospital-chatbot
```

### Check Nginx Status
```bash
sudo systemctl status nginx
sudo nginx -t
```

### Database Connection Issues
```bash
psql -U chatbot_user -d hospital_chatbot_db -h localhost
```

## Rollback Procedure

1. Stop application: `sudo supervisorctl stop hospital-chatbot`
2. Restore database backup
3. Revert code: `git checkout <previous-commit>`
4. Restart: `sudo supervisorctl start hospital-chatbot`

---

## Production Checklist Summary

- [x] Server configured
- [x] PostgreSQL set up
- [x] Nginx configured
- [x] SSL enabled
- [x] Application running via Supervisor
- [x] Firewall configured
- [x] Backups automated
- [x] Monitoring enabled
- [x] Error tracking set up
- [x] Logs rotating
- [x] Performance optimized

**Your hospital chatbot is now production-ready! 🎉**
