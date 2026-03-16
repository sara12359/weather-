import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_project.settings')
try:
    django.setup()
except Exception as e:
    print(f"Failed to setup django: {e}")

client = Client(HTTP_HOST='localhost')
try:
    response = client.get('/dashboard/')
    if response.status_code == 200:
        print("Success! No 500 error.")
    else:
        print(f"Status: {response.status_code}")
except Exception as e:
    import traceback
    traceback.print_exc()
