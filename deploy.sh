#!/bin/bash
# Script para atualizar aplicação do GitHub e reiniciar Gunicorn
# Executado automaticamente via cron ou webhook

set -e

PROJECT_DIR="/opt/syncrh"
LOG_FILE="/var/log/syncrh-deploy.log"
VENV_ACTIVATE="${PROJECT_DIR}/venv/bin/activate"

# Função de logging
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "🔄 Iniciando atualização do GitHub..."

# Verificar se o diretório existe
if [ ! -d "$PROJECT_DIR" ]; then
    log_message "❌ Erro: Diretório $PROJECT_DIR não encontrado"
    exit 1
fi

cd "$PROJECT_DIR"

# Ativar venv e pull
source "$VENV_ACTIVATE"

log_message "📥 Puxando atualizações do GitHub..."
git fetch origin main
COMMITS_BEHIND=$(git rev-list --count HEAD..origin/main)

if [ "$COMMITS_BEHIND" -eq 0 ]; then
    log_message "✅ Já está atualizado (nenhum novo commit)"
    exit 0
fi

log_message "📝 Encontrados $COMMITS_BEHIND novo(s) commit(s), atualizando..."
git pull origin main

# Instalar dependências se requirements.txt foi alterado
if git diff HEAD@{1} HEAD --name-only | grep -q "requirements.txt"; then
    log_message "📦 Atualizando dependências..."
    pip install -r requirements.txt --quiet
fi

# Coletar static files
log_message "🎨 Coletando static files..."
python manage.py collectstatic --noinput --quiet

# Aplicar migrations se existirem
log_message "🗄️  Aplicando migrations..."
python manage.py migrate --noinput

# Reiniciar Gunicorn
log_message "🔄 Reiniciando Gunicorn..."
pkill -f "gunicorn.*config.wsgi" || true
sleep 2
nohup /opt/syncrh/start.sh > /tmp/gunicorn.log 2>&1 &

log_message "✅ Atualização concluída com sucesso!"
log_message "🟢 Gunicorn reiniciado"
