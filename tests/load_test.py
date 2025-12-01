"""
Load Testing Script - Locust

Executar:
  locust -f tests/load_test.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import random


class WorksuiteUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login antes de rodar testes"""
        self.client.post("/api/v1/auth/login/", json={
            "username": "testuser",
            "password": "testpass123456"
        })
    
    @task(3)
    def list_users(self):
        """Listar usuários (3x mais frequente)"""
        self.client.get("/api/v1/users/")
    
    @task(2)
    def get_user_detail(self):
        """Ver detalhes do usuário"""
        user_id = random.randint(1, 100)
        self.client.get(f"/api/v1/users/{user_id}/")
    
    @task(1)
    def create_user(self):
        """Criar novo usuário"""
        self.client.post("/api/v1/users/", json={
            "username": f"user_{random.randint(1000, 9999)}",
            "email": f"user_{random.randint(1000, 9999)}@test.com",
            "password": "testpass123456"
        })


class AdminUser(HttpUser):
    """Admin user com mais ações"""
    wait_time = between(2, 4)
    
    def on_start(self):
        self.client.post("/api/v1/auth/login/", json={
            "username": "admin",
            "password": "adminpass123456"
        })
    
    @task(4)
    def list_reports(self):
        """Acessar relatórios"""
        self.client.get("/api/v1/reports/")
    
    @task(2)
    def export_data(self):
        """Exportar dados"""
        self.client.get("/api/v1/export/?format=csv")
    
    @task(1)
    def system_config(self):
        """Configurações do sistema"""
        self.client.get("/api/v1/system/config/")
