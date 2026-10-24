"""
Entry point for AI Tutor Flask web application.
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
FLASK_DIR = os.path.join(PROJECT_ROOT, "testFrontend", "FlaskApp")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if FLASK_DIR not in sys.path:
    sys.path.insert(0, FLASK_DIR)

from testFrontend.FlaskApp.app import app

if __name__ == "__main__":
    print("=" * 60)
    print("Starting KIRA: AI Tutor Web Application")
    print("Access the web UI at: http://localhost:5500")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5500, debug=True)
