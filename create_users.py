import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()
from django.contrib.auth.models import User
for i in range(1000, 1101):
    User.objects.create_user(username=str(i), password=str(i))
print("Done!")