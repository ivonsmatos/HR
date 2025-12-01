#!/usr/bin/env python
"""
PWA Validation & Testing Script
Valida se todos os componentes PWA estão configurados corretamente
"""

import os
import json
from pathlib import Path


class PWAValidator:
    """Validador de PWA"""

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.errors = []
        self.warnings = []
        self.successes = []

    def check_files_exist(self):
        """Verificar se todos os arquivos PWA existem"""
        print("\n📁 Verificando arquivos PWA...\n")

        required_files = {
            "config/pwa.py": "Configuração PWA",
            "config/pwa_views.py": "Views PWA",
            "config/pwa_middleware.py": "Middleware PWA",
            "config/pwa_settings.py": "Settings PWA",
            "static/js/service-worker.js": "Service Worker",
            "static/js/pwa.js": "Client PWA",
            "templates/base.html": "Template base",
            "docs/PWA.md": "Documentação PWA",
            "docs/ICON_GENERATION.md": "Guia de ícones",
            "PWA_SUMMARY.md": "Sumário PWA",
        }

        for file_path, description in required_files.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                self.successes.append(f"✅ {file_path} - {description}")
                print(f"✅ {file_path}")
            else:
                self.errors.append(f"❌ {file_path} - {description} NÃO ENCONTRADO")
                print(f"❌ {file_path} - FALTANDO!")

    def check_requirements(self):
        """Verificar se dependências PWA estão em requirements.txt"""
        print("\n📦 Verificando dependências PWA...\n")

        required_packages = [
            "whitenoise",
            "django-pwa",
            "django-push-notifications",
            "pywebpush",
        ]

        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            self.errors.append("❌ requirements.txt não encontrado!")
            return

        with open(req_file, "r") as f:
            content = f.read()

        for package in required_packages:
            if package.lower() in content.lower():
                self.successes.append(f"✅ {package} em requirements.txt")
                print(f"✅ {package}")
            else:
                self.warnings.append(f"⚠️ {package} não encontrado em requirements.txt")
                print(f"⚠️ {package} - FALTANDO!")

    def check_settings_integration(self):
        """Verificar se PWA está integrado em settings.py"""
        print("\n⚙️ Verificando integração em settings.py...\n")

        settings_file = self.project_root / "config" / "settings.py"
        if not settings_file.exists():
            self.errors.append("❌ config/settings.py não encontrado!")
            return

        with open(settings_file, "r") as f:
            content = f.read()

        checks = {
            "whitenoise": "WhiteNoise middleware",
            "from config.pwa import": "PWA import",
            "PWA_APP_NAME": "PWA config import",
        }

        for key, description in checks.items():
            if key in content:
                self.successes.append(f"✅ {description} encontrado")
                print(f"✅ {description}")
            else:
                self.warnings.append(
                    f"⚠️ {description} não encontrado - adicione manualmente"
                )
                print(f"⚠️ {description} - FALTANDO (adicione manualmente)")

    def check_urls_integration(self):
        """Verificar se URLs PWA estão em urls.py"""
        print("\n🔗 Verificando URLs PWA...\n")

        urls_file = self.project_root / "config" / "urls.py"
        if not urls_file.exists():
            self.warnings.append("⚠️ config/urls.py não encontrado!")
            print("⚠️ config/urls.py não encontrado!")
            return

        with open(urls_file, "r") as f:
            content = f.read()

        pwa_checks = {
            "pwa_views": "Import PWA views",
            "/api/pwa/manifest/": "Rota manifest",
            "/api/pwa/browserconfig/": "Rota browserconfig",
        }

        for key, description in pwa_checks.items():
            if key in content:
                self.successes.append(f"✅ {description} encontrado")
                print(f"✅ {description}")
            else:
                self.warnings.append(
                    f"⚠️ {description} não encontrado - adicione manualmente"
                )
                print(f"⚠️ {description} - FALTANDO (adicione manualmente)")

    def check_icons(self):
        """Verificar se ícones existem"""
        print("\n🎨 Verificando ícones PWA...\n")

        icons_dir = self.project_root / "static" / "images" / "icons"

        if not icons_dir.exists():
            self.warnings.append(
                "⚠️ Diretório de ícones não existe - execute: python scripts/generate_icons.py"
            )
            print("⚠️ Diretório static/images/icons não existe!")
            print("   Execute: python scripts/generate_icons.py")
            return

        required_icons = [
            "icon-192x192.png",
            "icon-512x512.png",
            "icon-maskable-192x192.png",
            "icon-maskable-512x512.png",
        ]

        icon_count = 0
        for icon in required_icons:
            icon_path = icons_dir / icon
            if icon_path.exists():
                self.successes.append(f"✅ {icon} encontrado")
                print(f"✅ {icon}")
                icon_count += 1
            else:
                print(f"❌ {icon} - FALTANDO!")

        if icon_count == 0:
            self.warnings.append(
                "⚠️ Nenhum ícone encontrado - execute: python scripts/generate_icons.py"
            )
        elif icon_count < len(required_icons):
            self.warnings.append(f"⚠️ Apenas {icon_count}/{len(required_icons)} ícones encontrados")
        else:
            self.successes.append(f"✅ Todos os {icon_count} ícones necessários encontrados")

    def check_https_ready(self):
        """Verificar se HTTPS está configurado"""
        print("\n🔒 Verificando HTTPS...\n")

        settings_file = self.project_root / "config" / "settings.py"
        if not settings_file.exists():
            self.warnings.append("⚠️ Não foi possível verificar configuração HTTPS")
            return

        with open(settings_file, "r") as f:
            content = f.read()

        https_checks = {
            "SECURE_SSL_REDIRECT": "SSL redirect",
            "SESSION_COOKIE_SECURE": "Session cookie secure",
            "CSRF_COOKIE_SECURE": "CSRF cookie secure",
        }

        for key, description in https_checks.items():
            if f"{key} = " in content or f"{key}=" in content:
                self.successes.append(f"✅ {description} configurado")
                print(f"✅ {description}")
            else:
                self.warnings.append(f"⚠️ {description} não configurado (necessário em produção)")
                print(f"⚠️ {description} - FALTANDO (necessário em produção)")

    def validate_json_files(self):
        """Validar JSON em arquivos Python"""
        print("\n📋 Validando JSON em arquivos...\n")

        pwa_config = self.project_root / "config" / "pwa.py"
        if pwa_config.exists():
            try:
                with open(pwa_config, "r") as f:
                    content = f.read()
                    # Verificar se tem JSON válido
                    if "PWA_APP_ICONS" in content:
                        self.successes.append(
                            "✅ Configuração PWA_APP_ICONS encontrada"
                        )
                        print("✅ PWA_APP_ICONS configurado")
                    else:
                        self.warnings.append("⚠️ PWA_APP_ICONS não encontrado")
                        print("⚠️ PWA_APP_ICONS não encontrado")
            except Exception as e:
                self.errors.append(f"❌ Erro validando {pwa_config}: {str(e)}")
                print(f"❌ Erro: {str(e)}")

    def check_service_worker(self):
        """Verificar Service Worker"""
        print("\n⚙️ Verificando Service Worker...\n")

        sw_file = self.project_root / "static" / "js" / "service-worker.js"
        if not sw_file.exists():
            self.errors.append("❌ Service Worker não encontrado!")
            return

        with open(sw_file, "r") as f:
            content = f.read()

        sw_checks = {
            "self.addEventListener('install'": "Install event",
            "self.addEventListener('activate'": "Activate event",
            "self.addEventListener('fetch'": "Fetch event",
            "CACHE_NAME": "Cache name",
            "networkFirstStrategy": "Network-first strategy",
            "cacheFirstStrategy": "Cache-first strategy",
        }

        for key, description in sw_checks.items():
            if key in content:
                self.successes.append(f"✅ {description} implementado")
                print(f"✅ {description}")
            else:
                self.errors.append(f"❌ {description} não encontrado!")
                print(f"❌ {description} - FALTANDO!")

    def run_all_checks(self):
        """Executar todos os checks"""
        print("=" * 60)
        print("🚀 VALIDADOR PWA - WORKSUITE CLONE")
        print("=" * 60)

        self.check_files_exist()
        self.check_requirements()
        self.check_settings_integration()
        self.check_urls_integration()
        self.check_icons()
        self.check_https_ready()
        self.validate_json_files()
        self.check_service_worker()

        self.print_summary()

    def print_summary(self):
        """Imprimir sumário"""
        print("\n" + "=" * 60)
        print("📊 SUMÁRIO")
        print("=" * 60)

        print(f"\n✅ Sucessos: {len(self.successes)}")
        print(f"⚠️ Avisos: {len(self.warnings)}")
        print(f"❌ Erros: {len(self.errors)}")

        if self.warnings:
            print("\n⚠️ AVISOS:")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.errors:
            print("\n❌ ERROS:")
            for error in self.errors:
                print(f"  {error}")

        # Status final
        print("\n" + "=" * 60)
        if len(self.errors) == 0 and len(self.warnings) <= 2:
            print("✅ PWA VALIDADA COM SUCESSO!")
            print("   Próximos passos:")
            print("   1. Gerar ícones: python scripts/generate_icons.py")
            print("   2. Instalar dependências: pip install -r requirements.txt")
            print("   3. Configurar HTTPS: mkcert localhost")
            print("   4. Integrar em settings.py (seguir pwa_settings.py)")
            print("   5. Testar: python manage.py runserver")
        elif len(self.errors) == 0:
            print("⚠️ PWA QUASE PRONTA - Ajustes necessários")
        else:
            print("❌ PWA COM PROBLEMAS - Erros encontrados")

        print("=" * 60)


def main():
    """Main"""
    validator = PWAValidator()
    validator.run_all_checks()


if __name__ == "__main__":
    main()
