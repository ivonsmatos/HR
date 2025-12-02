# 🔐 GitHub Secrets Configuration para Deploy SyncRH

## O que fazer:

1. **Acesse seu repositório no GitHub**
   - Vá para: `Settings` → `Secrets and variables` → `Actions`

2. **Crie os seguintes Secrets:**

### 1️⃣ `HOST`
- **O quê:** IP ou hostname do seu servidor produção
- **Exemplo:** `192.168.1.100` ou `syncrh.example.com`
- **Onde obter:** Seu provedor de hospedagem/VPS

### 2️⃣ `USERNAME`
- **O quê:** Usuário SSH para conectar ao servidor
- **Exemplo:** `deploy` ou `root`
- **Nota:** Deve ter permissão para rodar `docker compose`

### 3️⃣ `SSH_PRIVATE_KEY`
- **O quê:** Chave privada SSH para autenticação
- **Como gerar (se não tiver):**
  ```bash
  # No seu servidor:
  ssh-keygen -t rsa -b 4096 -f /home/deploy/.ssh/id_rsa
  
  # Copiar a chave privada (conteúdo completo):
  cat /home/deploy/.ssh/id_rsa
  ```
- **Cole todo o conteúdo** (começa com `-----BEGIN RSA PRIVATE KEY-----`)

## ✅ Verificar se está funcionando:

1. Faça um push para a branch `main`
2. Vá para `Actions` no GitHub
3. Veja o workflow `Deploy SyncRH` rodando
4. Se passar ✅, seu servidor foi atualizado!

## 🐛 Se der erro:

| Erro | Solução |
|------|---------|
| `Permission denied (publickey)` | Chave SSH incorreta ou usuário sem permissão |
| `cd /opt/syncrh: No such file or directory` | Crie a pasta no servidor: `mkdir -p /opt/syncrh` |
| `docker compose: command not found` | Instale Docker Compose no servidor |
| `git pull: not a git repository` | Faça um clone primeiro: `git clone ... /opt/syncrh` |

## 📋 Pré-requisitos no Servidor:

```bash
# 1. SSH como deploy user
ssh deploy@your-server

# 2. Instalar Docker e Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker deploy

# 3. Clonar repositório
mkdir -p /opt/syncrh
cd /opt/syncrh
git clone https://github.com/ivonsmatos/HR.git .

# 4. Criar arquivo .env com secrets
cat > .env << EOF
SECRET_KEY=seu-secret-key-super-seguro
DEBUG=False
DB_PASSWORD=sua-senha-db-segura
REDIS_URL=redis://redis:6379/0
EOF

# 5. Fazer primeiro deploy manual
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
```

## 🚀 Após primeiro deploy:

Próximas vezes que você fazer push para `main`, o GitHub Actions vai:
1. ✅ Conectar ao servidor via SSH
2. ✅ Pull das mudanças do git
3. ✅ Reconstruir Docker images
4. ✅ Rodar migrações
5. ✅ Coletar estáticos
6. ✅ Reiniciar containers

Tudo automaticamente! 🤖

---

**Arquivo de workflow:** `.github/workflows/deploy.yml`
