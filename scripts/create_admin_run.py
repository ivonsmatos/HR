import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_simple')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'contato@ivonmatos.com.br'
password = 'Protonsysdba@1986'
if User.objects.filter(username=username).exists():
    User.objects.filter(username=username).delete()
User.objects.create_superuser(username=username, email=username, password=password)
print('created')
