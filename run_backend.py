"""
Runner script for the Reuters IR FastAPI backend server.
Usage:
    py run_backend.py
"""

import uvicorn
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    print("=" * 65)
    print(" REUTERS-21578 IR ADMIN API SERVER (PART 1)")
    print(" Documentation Swagger UI : http://localhost:8000/docs")
    print(" Base API URL             : http://localhost:8000")
    print("=" * 65)
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
