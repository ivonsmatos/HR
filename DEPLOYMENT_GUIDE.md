# 🚀 DEPLOYMENT GUIDE - Worksuite PWA

## Pre-Deployment Checklist

### ✅ Security

- [ ] SECRET_KEY configurada e segura em .env
- [ ] DEBUG=False em produção
- [ ] ALLOWED_HOSTS configurado com domínios reais
- [ ] HTTPS/TLS habilitado
- [ ] CORS whitelist validado
- [ ] Rate limiting configurado
- [ ] Sentry integrado para error tracking
- [ ] Database backup strategy definido

### ✅ Testes

- [ ] Tests executados com sucesso (pytest)
- [ ] Coverage > 70%
- [ ] Migrations testadas
- [ ] Multi-tenancy isolation validado
- [ ] Integrações (Stripe, PayPal) testadas

### ✅ Performance

- [ ] APM configurado
- [ ] Database queries otimizadas
- [ ] Redis cache strategy definida
- [ ] CDN configurado para assets PWA
- [ ] Load testing concluído

### ✅ PWA

- [ ] Service Worker testado
- [ ] Offline mode funcional
- [ ] Web manifest validado
- [ ] Icons gerados em todos os tamanhos
- [ ] Push notifications testadas

---

## Local Development Setup

### 1. Clone e Configure

```bash
git clone https://github.com/seu-repo/worksuite-hr.git
cd worksuite-hr

# Copy example env
cp .env.example .env

# Edit .env com suas configurações
nano .env
```

### 2. Docker Setup (Recomendado)

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### 3. Manual Setup (Alternativa)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static
python manage.py collectstatic

# Run development server
python manage.py runserver
```

---

## Production Deployment (AWS/GCP/Heroku)

### Heroku Deployment

```bash
# Login
heroku login

# Create app
heroku create worksuite-pwa

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:premium-0

# Add Redis addon
heroku addons:create heroku-redis:premium-0

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### AWS Deployment (ECS/Fargate)

```bash
# Build Docker image
docker build -t worksuite-pwa:latest .

# Tag for ECR
docker tag worksuite-pwa:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/worksuite-pwa:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/worksuite-pwa:latest

# Deploy with Terraform or CloudFormation
terraform apply
```

### Docker Swarm/Kubernetes

```bash
# Kubernetes deployment
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres-secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods -n worksuite
kubectl logs -n worksuite deployment/worksuite-web
```

---

## Post-Deployment Validation

### 1. Health Checks

```bash
# Check application
curl -I https://your-domain.com/health/

# Check API
curl https://your-domain.com/api/v1/status/

# Check PWA
curl -I https://your-domain.com/manifest.json
```

### 2. Database Verification

```bash
# SSH into server
ssh user@your-server.com

# Connect to database
psql -h your-db-host -U postgres -d worksuite_db

# Check tables
\dt

# Exit
\q
```

### 3. Monitoring

```bash
# View logs (Docker)
docker-compose logs -f web

# View logs (Heroku)
heroku logs -t

# Monitor Sentry
# https://sentry.io/organizations/your-org/issues/
```

---

## Rollback Procedure

### If deployment fails:

```bash
# Docker
docker-compose down
docker-compose up -d

# Heroku
heroku rollback

# AWS
aws ecs update-service --cluster prod --service worksuite-web --force-new-deployment
```

---

## Scaling

### Horizontal Scaling

```bash
# Docker Swarm
docker service scale web=3

# Kubernetes
kubectl scale deployment worksuite-web --replicas=3

# Heroku
heroku ps:scale web=3 worker=2
```

### Database Scaling

```bash
# Read replicas (AWS)
aws rds create-db-instance-read-replica \
  --db-instance-identifier worksuite-db-replica \
  --source-db-instance-identifier worksuite-db

# Connection pooling (PgBouncer)
# Configure em DATABASES['default']['CONN_MAX_AGE']
```

---

## Monitoring & Maintenance

### Daily Checks

```bash
# Check logs
docker-compose logs --tail 100 web

# Check disk space
df -h

# Check database
psql -c "SELECT count(*) FROM users;"

# Check Redis
redis-cli info
```

### Weekly Maintenance

```bash
# Database backup
python manage.py dumpdata > backup.json

# Clean old logs
find logs/ -mtime +30 -delete

# Check performance metrics
# Via Sentry, New Relic, ou DataDog dashboard
```

### Monthly Tasks

```bash
# Security updates
pip install --upgrade -r requirements.txt

# Performance optimization
python manage.py shell_plus
>>> from django.core.cache import cache
>>> cache.clear()

# Certificate renewal (if using LetsEncrypt)
certbot renew
```

---

## Troubleshooting

### Application won't start

```bash
# Check logs
docker-compose logs web

# Common issues:
# 1. Missing SECRET_KEY - Check .env
# 2. Database not accessible - Check DB_HOST, DB_PORT
# 3. Redis not available - Check REDIS_URL

# Solution:
docker-compose down
docker-compose up -d
```

### Database migrations fail

```bash
# Check migration status
python manage.py showmigrations

# Apply migrations manually
python manage.py migrate --run-syncdb

# If corrupted:
python manage.py migrate core zero  # Rollback
python manage.py migrate            # Reapply
```

### Performance issues

```bash
# Check slow queries
python manage.py shell
>>> from django.db import connection
>>> from django.test.utils import CaptureQueriesContext
>>> with CaptureQueriesContext(connection) as context:
>>>     # Run code
>>> for query in context:
>>>     print(query['time'], query['sql'])

# Enable query logging in settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## Disaster Recovery

### Database Restoration

```bash
# Restore from backup
pg_restore -h your-db-host -U postgres -d worksuite_db backup.dump

# or
psql -h your-db-host -U postgres -d worksuite_db < backup.sql
```

### Full System Recovery

```bash
# 1. Restore database
pg_restore -h new-host -U postgres -d worksuite_db backup.dump

# 2. Deploy latest code
git clone https://github.com/seu-repo/worksuite-hr.git
cd worksuite-hr
git checkout production-release-tag

# 3. Update env
cp .env.production .env

# 4. Restart services
docker-compose up -d

# 5. Verify
curl https://your-domain.com/health/
```

---

**Pronto para deploy!** 🚀
