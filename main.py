"""
Gunicorn entry point for FloodTwin.
"""

from server import app

# Gunicorn looks for a module-level variable like `app`.
application = app
