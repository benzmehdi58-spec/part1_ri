"""
Master Launcher for Reuters IR Admin Application (Part 1)
Starts both the FastAPI Backend and the Vite React Frontend.
Usage:
    py run_app.py
"""

import subprocess
import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

print("=" * 65)
print(" STARTING REUTERS IR ADMIN SUITE (PART 1)")
print("=" * 65)

# 1. Start FastAPI Backend
print("\n[1/2] Starting FastAPI Backend on http://localhost:8000 ...")
backend_cmd = [sys.executable, "-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
backend_proc = subprocess.Popen(backend_cmd, cwd=BASE_DIR)

time.sleep(1.5)

# 2. Start Vite Frontend
print("\n[2/2] Starting React Frontend on http://localhost:5173 ...")
frontend_cmd = ["npm.cmd" if os.name == "nt" else "npm", "run", "dev"]
frontend_proc = subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR)

print("\n" + "=" * 65)
print(" -> Backend API  : http://localhost:8000")
print(" -> Swagger Docs : http://localhost:8000/docs")
print(" -> React UI     : http://localhost:5173")
print("=" * 65)
print("Press Ctrl+C to stop both servers.\n")

try:
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    print("\nShutting down servers...")
    backend_proc.terminate()
    frontend_proc.terminate()
    print("Done.")
