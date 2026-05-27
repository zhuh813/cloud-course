import sys
import os

# Ensure the root directory is in the Python search path so we can import src cleanly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.app import create_app

app = create_app()

if __name__ == '__main__':
    print("[Server] Antigravity Flask App is launching on port 1919...")
    print("[URL] Open http://localhost:1919 in your web browser.")
    app.run(host='0.0.0.0', port=1919, debug=True)
