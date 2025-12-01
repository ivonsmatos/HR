"""
STAGING ENVIRONMENT SETUP
Docker compose configuration for staging environment
"""

import yaml
from typing import Dict, Any


STAGING_DOCKER_COMPOSE = """
version: '3.9'

services:
  # PostgreSQL Database
  db-staging:
    image: postgres:16.1-alpine
    container_name: syncrh-db-staging
    environment:
      POSTGRES_USER: syncrh_staging
      POSTGRES_PASSWORD: ${DB_PASSWORD_STAGING}
      POSTGRES_DB: syncrh_staging
      POSTGRES_INITDB_ARGS: "-c shared_preload_libraries=pg_stat_statements"
    volumes:
      - postgres_data_staging:/var/lib/postgresql/data
      - ./scripts/init_staging_db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5433:5432"
    networks:
      - syncrh-staging
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U syncrh_staging"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis-staging:
    image: redis:7.2-alpine
    container_name: syncrh-redis-staging
    command: redis-server --appendonly yes
    volumes:
      - redis_data_staging:/data
    ports:
      - "6380:6379"
    networks:
      - syncrh-staging
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Django Application
  app-staging:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: syncrh-app-staging
    environment:
      DEBUG: "False"
      ENVIRONMENT: staging
      DB_ENGINE: django.db.backends.postgresql
      DB_NAME: syncrh_staging
      DB_USER: syncrh_staging
      DB_PASSWORD: ${DB_PASSWORD_STAGING}
      DB_HOST: db-staging
      DB_PORT: 5432
      REDIS_URL: redis://redis-staging:6379/0
      CELERY_BROKER_URL: redis://redis-staging:6379/0
      SECRET_KEY: ${SECRET_KEY_STAGING}
      ALLOWED_HOSTS: "staging.syncrh.local,localhost:8001"
      SENTRY_DSN: ${SENTRY_DSN_STAGING}
    depends_on:
      db-staging:
        condition: service_healthy
      redis-staging:
        condition: service_healthy
    volumes:
      - ./apps:/app/apps
      - ./config:/app/config
      - ./templates:/app/templates
      - ./static:/app/static
      - ./media:/app/media
    ports:
      - "8001:8000"
    networks:
      - syncrh-staging
    command: |
      sh -c "
      python manage.py migrate &&
      python manage.py collectstatic --noinput &&
      gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
      "

  # Celery Worker
  celery-staging:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: syncrh-celery-staging
    environment:
      DEBUG: "False"
      ENVIRONMENT: staging
      DB_ENGINE: django.db.backends.postgresql
      DB_NAME: syncrh_staging
      DB_USER: syncrh_staging
      DB_PASSWORD: ${DB_PASSWORD_STAGING}
      DB_HOST: db-staging
      REDIS_URL: redis://redis-staging:6379/0
      CELERY_BROKER_URL: redis://redis-staging:6379/0
    depends_on:
      - db-staging
      - redis-staging
    volumes:
      - ./apps:/app/apps
      - ./config:/app/config
      - ./celery_logs:/app/celery_logs
    networks:
      - syncrh-staging
    command: |
      celery -A config worker --loglevel=info --logfile=/app/celery_logs/worker.log

  # Nginx Reverse Proxy
  nginx-staging:
    image: nginx:alpine
    container_name: syncrh-nginx-staging
    volumes:
      - ./nginx.staging.conf:/etc/nginx/nginx.conf
      - ./static:/app/static
      - ./media:/app/media
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - app-staging
    networks:
      - syncrh-staging

volumes:
  postgres_data_staging:
    driver: local
  redis_data_staging:
    driver: local

networks:
  syncrh-staging:
    driver: bridge
"""


STAGING_ENV_FILE = """
# STAGING ENVIRONMENT VARIABLES
# .env.staging

# Django Settings
DEBUG=False
ENVIRONMENT=staging
SECRET_KEY=${RANDOM_SECRET_KEY}
ALLOWED_HOSTS=staging.syncrh.local,localhost:8001

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=syncrh_staging
DB_USER=syncrh_staging
DB_PASSWORD=${RANDOM_DB_PASSWORD}
DB_HOST=db-staging
DB_PORT=5432

# Redis
REDIS_URL=redis://redis-staging:6379/0
CACHE_URL=redis://redis-staging:6379/1

# Celery
CELERY_BROKER_URL=redis://redis-staging:6379/0
CELERY_RESULT_BACKEND=redis://redis-staging:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.staging.syncrh.local
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Sentry
SENTRY_DSN=${STAGING_SENTRY_DSN}

# AWS (if using S3)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# Logging
LOGGING_LEVEL=INFO
"""


NGINX_STAGING_CONFIG = """
upstream django {
    server app-staging:8000;
}

server {
    listen 80;
    server_name staging.syncrh.local localhost;

    client_max_body_size 50M;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    location /static/ {
        alias /app/static/;
        expires 30d;
    }

    location /media/ {
        alias /app/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health/ {
        proxy_pass http://django/health/;
        access_log off;
    }
}
"""


STAGING_INIT_DB_SCRIPT = """
-- init_staging_db.sql
-- Initialize staging database

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create tenant schema
CREATE SCHEMA IF NOT EXISTS public;

-- Create test tenant
INSERT INTO core_company (name, slug, email, currency, timezone, is_on_trial, is_verified)
VALUES ('Staging Company', 'staging-company', 'admin@staging.syncrh.local', 'BRL', 'America/Sao_Paulo', false, true)
ON CONFLICT (slug) DO NOTHING;

-- Create test users (note: passwords should be set via Django)
INSERT INTO core_user (username, email, first_name, last_name, is_staff, is_superuser, is_active, company_id)
SELECT 'admin', 'admin@staging.syncrh.local', 'Admin', 'User', true, true, true, id
FROM core_company WHERE slug = 'staging-company'
ON CONFLICT (username) DO NOTHING;

INSERT INTO core_user (username, email, first_name, last_name, is_active, company_id)
SELECT 'testuser', 'test@staging.syncrh.local', 'Test', 'User', true, id
FROM core_company WHERE slug = 'staging-company'
ON CONFLICT (username) DO NOTHING;

-- Create test company domain
INSERT INTO core_companydomain (domain, company_id)
SELECT 'staging.syncrh.local', id
FROM core_company WHERE slug = 'staging-company'
ON CONFLICT (domain) DO NOTHING;
"""


INSTALLATION_INSTRUCTIONS = """
STAGING ENVIRONMENT SETUP INSTRUCTIONS
=======================================

1. Prepare Environment Files:
   
   cp docker-compose.yml docker-compose.staging.yml
   cp .env .env.staging
   
   Update .env.staging with:
   - Unique SECRET_KEY for staging
   - Strong DB_PASSWORD_STAGING
   - STAGING_SENTRY_DSN if applicable

2. Create Required Files:
   
   scripts/init_staging_db.sql (provided above)
   nginx.staging.conf (provided above)

3. Build and Start Services:
   
   docker-compose -f docker-compose.staging.yml up -d

4. Initialize Database:
   
   docker-compose -f docker-compose.staging.yml exec app-staging python manage.py migrate
   docker-compose -f docker-compose.staging.yml exec app-staging python manage.py createsuperuser

5. Seed Test Data:
   
   # Create test records via admin interface or management commands
   docker-compose -f docker-compose.staging.yml exec app-staging python manage.py loaddata fixtures/staging_data.json

6. Access Staging Environment:
   
   Web Application: http://localhost:8001/
   Admin Panel: http://localhost:8001/admin/
   Swagger Docs: http://localhost:8001/api/schema/swagger-ui/
   Health Check: http://localhost:8001/health/

MONITORING STAGING
==================

Check Services Status:
  docker-compose -f docker-compose.staging.yml ps

View Logs:
  docker-compose -f docker-compose.staging.yml logs app-staging
  docker-compose -f docker-compose.staging.yml logs celery-staging

Database Connection:
  docker-compose -f docker-compose.staging.yml exec db-staging psql -U syncrh_staging -d syncrh_staging

Performance Testing:
  locust -f locustfile.py --host=http://localhost:8001 --users 50 --spawn-rate 5

COMPARING STAGING vs PRODUCTION
================================

Staging Environment:
✅ Same tech stack as production
✅ Same data structures
✅ Test with realistic data volumes
✅ Test deployment procedures
✅ Validate configuration changes
✅ Run load testing
✅ Test disaster recovery

But with:
⚠️  Smaller data volumes (for speed)
⚠️  Reduced resource allocation
⚠️  Shorter retention policies
⚠️  Test-level security (not production-hardened)

TESTING CHECKLIST
=================

Before production deployment:

Database:
☐ Run migrations successfully
☐ Verify data integrity
☐ Test backup/restore procedures
☐ Check query performance

Application:
☐ All endpoints functional
☐ Authentication working
☐ Authorization rules enforced
☐ API documentation accessible
☐ Health checks passing

Performance:
☐ Load test 50 concurrent users
☐ P95 latency < 200ms
☐ Error rate < 1%
☐ CPU usage reasonable

Security:
☐ No debug mode enabled
☐ HTTPS configured (if applicable)
☐ API rate limiting working
☐ Admin only accessible via VPN

Operations:
☐ Logging working correctly
☐ Error tracking (Sentry) active
☐ Monitoring alerts configured
☐ Backup jobs running

CLEANUP
=======

Stop all staging services:
  docker-compose -f docker-compose.staging.yml down

Remove staging volumes:
  docker-compose -f docker-compose.staging.yml down -v

Remove staging data:
  docker volume rm syncrh_postgres_data_staging
  docker volume rm syncrh_redis_data_staging
"""
