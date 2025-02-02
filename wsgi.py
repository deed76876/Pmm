import os

import speckenv
from django.core.wsgi import get_wsgi_application


speckenv.read_speckenv(filename=os.environ.get("DOTENV", ".env"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workbench.settings")
application = get_wsgi_application()
