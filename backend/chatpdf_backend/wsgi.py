import os

from django.core.wsgi import get_wsgi_application
from documents.bootstrap_admin import ensure_admin

ensure_admin()
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "chatpdf_backend.settings",
)

application = get_wsgi_application()
