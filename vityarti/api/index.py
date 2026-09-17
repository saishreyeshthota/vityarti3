import sys
import os
from urllib.parse import parse_qs, urlencode

# Ensure project root is in sys.path so app and models can be imported
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app
from database import init_db

# Initialize database on cold start
try:
    with app.app_context():
        init_db()
except Exception as e:
    print(f"Vercel DB initialization notice: {e}")


class VercelWSGIMiddleware:
    """
    Ensures correct PATH_INFO is passed to Flask when running behind
    Vercel Serverless Function rewrites.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query_string = environ.get("QUERY_STRING", "")
        if "__vercel_path" in query_string:
            params = parse_qs(query_string, keep_blank_values=True)
            if "__vercel_path" in params and params["__vercel_path"]:
                target_path = params["__vercel_path"][0]
                if not target_path.startswith("/"):
                    target_path = "/" + target_path
                environ["PATH_INFO"] = target_path
                del params["__vercel_path"]
                environ["QUERY_STRING"] = urlencode(params, doseq=True)
        else:
            raw_uri = (
                environ.get("HTTP_X_FORWARDED_URI")
                or environ.get("RAW_URI")
                or environ.get("REQUEST_URI")
            )
            if raw_uri:
                path_only = raw_uri.split("?")[0]
                if path_only and not path_only.endswith("index.py") and "*" not in path_only:
                    environ["PATH_INFO"] = path_only

        # If PATH_INFO is still pointing to index.py, /api, or is empty, map to root '/'
        current_path = environ.get("PATH_INFO", "")
        if current_path.endswith("index.py") or current_path == "/api" or not current_path:
            environ["PATH_INFO"] = "/"

        return self.wsgi_app(environ, start_response)


# Wrap Flask WSGI application with path-correction middleware
app.wsgi_app = VercelWSGIMiddleware(app.wsgi_app)
