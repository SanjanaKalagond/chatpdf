import os
from django.contrib.auth import get_user_model

def ensure_admin():
    User = get_user_model()

    username = os.environ.get("DJANGO_ADMIN_USER")
    password = os.environ.get("DJANGO_ADMIN_PASSWORD")
    email = os.environ.get("DJANGO_ADMIN_EMAIL", "")

    if not username or not password:
        return

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            password=password,
            email=email,
        )