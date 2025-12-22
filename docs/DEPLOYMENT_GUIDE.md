# Deployment Guide

## Production Deployment Guide for AI Portfolio Analysis Platform

This guide covers deploying the platform to production environments.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Deployment Options](#deployment-options)
4. [Security Configuration](#security-configuration)
5. [Monitoring & Logging](#monitoring--logging)
6. [Scaling & Performance](#scaling--performance)
7. [Backup & Recovery](#backup--recovery)

---

## Pre-Deployment Checklist

### Code Review

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Documentation complete
- [ ] Environment variables configured
- [ ] Security vulnerabilities addressed
- [ ] Performance optimizations applied

### Infrastructure

- [ ] Server/cloud resources provisioned
- [ ] Database configured
- [ ] SSL certificates obtained
- [ ] Domain configured
- [ ] CDN setup (if needed)
- [ ] Backup strategy defined

### Dependencies

- [ ] All dependencies listed in `requirements.txt`
- [ ] Compatible Python version (3.9+)
- [ ] System dependencies documented
- [ ] Model files available
- [ ] API keys secured

---

## Environment Setup

### Production Environment Variables

Create `.env.production`:

```bash
# Environment
ENVIRONMENT=production
DEBUG=False

# API Keys
OPENAI_API_KEY=your_production_openai_key
ALPHA_VANTAGE_API_KEY=your_production_alpha_vantage_key
SENDGRID_API_KEY=your_production_sendgrid_key

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://redis:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your_very_secure_secret_key_here_use_secrets.token_hex
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security
ENABLE_CORS=True
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_MINUTE=100

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO

# Email
EMAIL_FROM=noreply@yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com

# Models
MODEL_PATH=/app/data/models
CACHE_DIR=/app/data/cache
```

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB SSD
- OS: Ubuntu 20.04+ / Windows Server 2019+

**Recommended:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 50GB SSD
- OS: Ubuntu 22.04 LTS
- GPU: Optional (for faster predictions)

---

## Deployment Options

### Option 1: Docker Deployment (Recommended)

**1. Create Dockerfile:**

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/models data/processed data/raw logs

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (API server)
CMD ["uvicorn", "api.model_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. Create docker-compose.yml:**

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env.production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: always
    depends_on:
      - redis
      - postgres
  
  dashboard:
    build: .
    command: streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
    ports:
      - "8501:8501"
    env_file:
      - .env.production
    volumes:
      - ./data:/app/data
    restart: always
    depends_on:
      - api
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: always
  
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=portfolio_analysis
      - POSTGRES_USER=dbuser
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
      - dashboard
    restart: always

volumes:
  redis_data:
  postgres_data:
```

**3. Deploy:**

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 2: Cloud Deployment (AWS)

**Using AWS Elastic Beanstalk:**

1. **Install EB CLI:**
   ```bash
   pip install awsebcli
   ```

2. **Initialize:**
   ```bash
   eb init -p python-3.9 portfolio-analysis-platform
   ```

3. **Create environment:**
   ```bash
   eb create production-env
   ```

4. **Configure environment variables:**
   ```bash
   eb setenv OPENAI_API_KEY=your_key DATABASE_URL=your_db_url
   ```

5. **Deploy:**
   ```bash
   eb deploy
   ```

**Using AWS EC2:**

```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install python3.9 python3-pip nginx

# Clone repository
git clone your-repo-url
cd your-repo

# Install Python dependencies
pip3 install -r requirements.txt

# Configure systemd service
sudo nano /etc/systemd/system/portfolio-api.service
```

**Service file:**
```ini
[Unit]
Description=Portfolio Analysis API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/portfolio-analysis
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/usr/bin/python3 -m uvicorn api.model_api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl start portfolio-api
sudo systemctl enable portfolio-api
```

### Option 3: Azure Deployment

**Using Azure App Service:**

```bash
# Login
az login

# Create resource group
az group create --name portfolio-rg --location eastus

# Create App Service plan
az appservice plan create --name portfolio-plan --resource-group portfolio-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group portfolio-rg --plan portfolio-plan --name portfolio-analysis-app --runtime "PYTHON|3.9"

# Deploy
az webapp up --name portfolio-analysis-app --resource-group portfolio-rg
```

### Option 4: Heroku Deployment

**1. Create Procfile:**
```
web: uvicorn api.model_api:app --host 0.0.0.0 --port $PORT
worker: python automation/scheduler.py
```

**2. Deploy:**
```bash
# Login
heroku login

# Create app
heroku create portfolio-analysis-platform

# Set config
heroku config:set OPENAI_API_KEY=your_key

# Deploy
git push heroku main

# Scale
heroku ps:scale web=1 worker=1
```

---

## Security Configuration

### API Authentication

**Implement API key authentication:**

```python
# api/auth.py
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_SECRET_KEY"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return api_key

# Use in endpoints
@app.post("/api/v1/predict/risk")
async def predict_risk(data: Input, api_key: str = Depends(get_api_key)):
    # Your code here
```

### HTTPS Configuration

**Nginx configuration (nginx.conf):**

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # API
    location /api {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Dashboard
    location / {
        proxy_pass http://dashboard:8501;
        proxy_set_header Host $host;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Rate Limiting

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://localhost")
    await FastAPILimiter.init(redis_client)

@app.post("/api/v1/predict")
@limits(calls=100, period=3600)  # 100 calls per hour
async def predict(data: Input):
    # Your code
```

---

## Monitoring & Logging

### Logging Setup

**Configure structured logging:**

```python
import logging
from loguru import logger

# Configure loguru
logger.add(
    "logs/production.log",
    rotation="500 MB",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# Integrate with Sentry
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0
)
```

### Application Monitoring

**Use Prometheus + Grafana:**

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Metrics
request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def monitor_requests(request, call_next):
    request_count.inc()
    with request_duration.time():
        response = await call_next(request)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Health Checks

```python
@app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "checks": {
            "database": check_database(),
            "redis": check_redis(),
            "models": check_models(),
            "disk_space": check_disk_space()
        }
    }
```

---

## Scaling & Performance

### Horizontal Scaling

**Load balancing with multiple instances:**

```yaml
# docker-compose.yml
services:
  api:
    build: .
    deploy:
      replicas: 3
    # ... other config

  nginx:
    image: nginx:alpine
    # Load balancer configuration
```

### Caching Strategy

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379)

def cache_result(timeout=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, timeout, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### Database Optimization

- Use connection pooling
- Implement database indexes
- Regular vacuuming (PostgreSQL)
- Query optimization

---

## Backup & Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Database backup
pg_dump portfolio_analysis > $BACKUP_DIR/database.sql

# Data files
tar -czf $BACKUP_DIR/data.tar.gz data/

# Upload to S3
aws s3 cp $BACKUP_DIR s3://your-backup-bucket/ --recursive
```

**Schedule with cron:**
```bash
# Daily at 2 AM
0 2 * * * /path/to/backup.sh
```

### Disaster Recovery

1. **Maintain offsite backups**
2. **Test recovery procedures monthly**
3. **Document recovery steps**
4. **Keep backup of environment variables**
5. **Version control for code**

---

## Post-Deployment

### Verification Checklist

- [ ] API responding correctly
- [ ] Dashboard accessible
- [ ] Models loading properly
- [ ] Database connections working
- [ ] SSL certificate valid
- [ ] Monitoring active
- [ ] Logs being collected
- [ ] Backups configured
- [ ] Rate limiting functional
- [ ] Error tracking working

### Performance Testing

```bash
# Load testing with locust
pip install locust

# Create locustfile.py
locust -f locustfile.py --host=https://yourdomain.com
```

### Maintenance

- **Weekly**: Review logs and metrics
- **Monthly**: Update dependencies
- **Quarterly**: Security audit
- **Annually**: Infrastructure review

---

## Support & Troubleshooting

### Common Production Issues

**1. High memory usage**
- Reduce batch sizes
- Implement pagination
- Clear caches regularly

**2. Slow response times**
- Enable caching
- Optimize database queries
- Add more instances

**3. Model loading failures**
- Check file permissions
- Verify model file integrity
- Increase memory allocation

### Rollback Procedure

```bash
# Docker
docker-compose down
git checkout previous-version
docker-compose up -d

# Kubernetes
kubectl rollout undo deployment/portfolio-api
```

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Security Best Practices](https://owasp.org/www-project-top-ten/)
