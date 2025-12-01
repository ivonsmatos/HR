#!/bin/bash

# 🚀 QUICK START COMMANDS - Worksuite PWA QA Implementation

echo "═══════════════════════════════════════════════════════════════"
echo "  QA IMPLEMENTATION - QUICK START"
echo "═══════════════════════════════════════════════════════════════"

# 1. Setup Environment
echo ""
echo "📋 PASSO 1: Configurar Ambiente"
echo "───────────────────────────────────────────────────────────────"
echo "cp .env.example .env"
echo "nano .env  # Editar variáveis"
echo ""

# 2. Verificar Alterações
echo "📋 PASSO 2: Verificar Alterações Git"
echo "───────────────────────────────────────────────────────────────"
echo "git status"
echo "git diff config/settings.py"
echo "git diff requirements.txt"
echo ""

# 3. Instalar Dependências
echo "📋 PASSO 3: Instalar Dependências"
echo "───────────────────────────────────────────────────────────────"
echo "pip install -r requirements.txt"
echo ""

# 4. Docker Setup (Recomendado)
echo "📋 PASSO 4: Docker Setup"
echo "───────────────────────────────────────────────────────────────"
echo "docker-compose up -d"
echo "docker-compose ps"
echo "docker-compose logs -f web"
echo ""

# 5. Database Migrations
echo "📋 PASSO 5: Database Setup"
echo "───────────────────────────────────────────────────────────────"
echo "docker-compose exec web python manage.py migrate"
echo "docker-compose exec web python manage.py createsuperuser"
echo "docker-compose exec web python manage.py collectstatic --noinput"
echo ""

# 6. Rodar Testes
echo "📋 PASSO 6: Rodar Testes"
echo "───────────────────────────────────────────────────────────────"
echo "docker-compose exec web pytest tests/ -v"
echo "docker-compose exec web pytest tests/ -v --cov=apps --cov-report=html"
echo ""

# 7. Verificar Segurança
echo "📋 PASSO 7: Verificar Segurança"
echo "───────────────────────────────────────────────────────────────"
echo "docker-compose exec web python scripts/run_qa_tests.py"
echo ""

# 8. Verificar Aplicação
echo "📋 PASSO 8: Verificar Aplicação"
echo "───────────────────────────────────────────────────────────────"
echo "curl -I http://localhost:8000/health/"
echo "curl http://localhost:8000/"
echo ""

# 9. Commit Changes
echo "📋 PASSO 9: Commitar Mudanças"
echo "───────────────────────────────────────────────────────────────"
echo "git add ."
echo "git commit -m \"🔧 QA: Security, Tests, DevOps - Production Ready\""
echo "git push origin main"
echo ""

# 10. Deploy (Escolha uma)
echo "📋 PASSO 10: Deploy"
echo "───────────────────────────────────────────────────────────────"
echo ""
echo "OPÇÃO A - Heroku:"
echo "  heroku login"
echo "  heroku create worksuite-pwa"
echo "  git push heroku main"
echo ""
echo "OPÇÃO B - AWS:"
echo "  Ver DEPLOYMENT_GUIDE.md"
echo ""
echo "OPÇÃO C - Kubernetes:"
echo "  kubectl apply -f k8s/"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Pronto para começar!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Documentação:"
echo "  📖 QA_IMPLEMENTATION_COMPLETE.md"
echo "  📖 DEPLOYMENT_GUIDE.md"
echo "  📖 TROUBLESHOOTING_GUIDE.md"
echo "  📖 FILES_IMPLEMENTATION_SUMMARY.md"
