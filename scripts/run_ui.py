#!/usr/bin/env python3
"""Run Streamlit UI"""

import sys
sys.path.insert(0, '/home/ubuntu/Desktop/Assignment')

import subprocess

if __name__ == "__main__":
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "/home/ubuntu/Desktop/Assignment/src/ui/app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
    ])
