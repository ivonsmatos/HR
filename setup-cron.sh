#!/bin/bash
# Configuração automática de cron no servidor
# Execute este script com: ssh root@IP "bash -s" < setup-cron.sh

# Copiar script de deploy para o servidor
cat > /opt/syncrh/deploy.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
# Script para atualizar aplicação do GitHub e reiniciar Gunicorn
set -e

PROJECT_DIR="/opt/syncrh"
LOG_FILE="/var/log/syncrh-deploy.log"
VENV_ACTIVATE="${PROJECT_DIR}/venv/bin/activate"

# Função de logging
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_message "🔄 Iniciando atualização do GitHub..."
cd "$PROJECT_DIR"
source "$VENV_ACTIVATE"

# Git pull
git fetch origin main
COMMITS_BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")

if [ "$COMMITS_BEHIND" -eq 0 ]; then
    log_message "✅ Já está atualizado"
    exit 0
fi

log_message "📥 Puxando $COMMITS_BEHIND novo(s) commit(s)..."
git pull origin main

# Instalar dependências se requirements.txt foi alterado
if git diff HEAD@{1} HEAD --name-only 2>/dev/null | grep -q "requirements.txt"; then
    log_message "📦 Atualizando dependências..."
    pip install -r requirements.txt --quiet
fi

# Coletar static files
log_message "🎨 Coletando static files..."
python manage.py collectstatic --noinput --quiet 2>&1 | grep -v "^Deleting\|^Processing\|^Post-processing"

# Aplicar migrations
log_message "🗄️  Aplicando migrations..."
python manage.py migrate --noinput --quiet

# Reiniciar Gunicorn
log_message "🔄 Reiniciando Gunicorn..."
pkill -f "gunicorn.*config.wsgi" 2>/dev/null || true
sleep 2
nohup /opt/syncrh/start.sh > /tmp/gunicorn.log 2>&1 &

log_message "✅ Atualização concluída com sucesso!"
DEPLOY_SCRIPT

chmod +x /opt/syncrh/deploy.sh

# Criar arquivo de log
touch /var/log/syncrh-deploy.log
chmod 666 /var/log/syncrh-deploy.log

# Adicionar ao crontab para executar a cada 5 minutos
CRON_CMD="*/5 * * * * /opt/syncrh/deploy.sh"
(crontab -l 2>/dev/null || true) | grep -v "/opt/syncrh/deploy.sh" | (cat; echo "$CRON_CMD") | crontab -

echo "✅ Cron job instalado: Verificará updates a cada 5 minutos"
echo "📋 Log disponível em: /var/log/syncrh-deploy.log"
echo "🔍 Para ver os logs em tempo real:"
echo "   tail -f /var/log/syncrh-deploy.log"
