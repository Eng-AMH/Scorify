# ══════════════════════════════════════════════════════════
#  Scorify — PythonAnywhere WSGI Config
#  Copy this file's content into the WSGI file in the Web tab
# ══════════════════════════════════════════════════════════
import os, sys
from pathlib import Path
from dotenv import load_dotenv

project_path = '/home/Scorify/scorify'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

load_dotenv(Path(project_path) / '.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scorify.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
