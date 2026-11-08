"""VisionGuard Universal WSGI & Development Entrypoint."""
import os
from webapp.app import create_app

# Default application object for WSGI servers (Gunicorn, Waitress, Render, etc.)
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
