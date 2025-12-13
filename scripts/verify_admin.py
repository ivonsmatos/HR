import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_simple')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'contato@ivonmatos.com.br'
password = 'Protonsysdba@1986'
try:
    user = User.objects.get(username=username)
    print('exists')
    print('check_password:', user.check_password(password))
except User.DoesNotExist:
    print('missing')
