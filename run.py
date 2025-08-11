#!/usr/bin/env python3
"""
LinkedIn Android Poster - Main Runner Script

This script provides a simple way to start the application in different modes.
"""
import sys
import subprocess
import os
import argparse
from pathlib import Path

def run_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend server...")
    os.chdir("backend")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "127.0.0.1", 
        "--port", "8000", 
        "--reload"
    ])

def run_frontend():
    """Start the React frontend development server"""
    print("🚀 Starting React frontend development server...")
    os.chdir("frontend")
    subprocess.run(["npm", "run", "dev"])

def init_database():
    """Initialize the database"""
    print("🗄️ Initializing database...")
    os.chdir("backend")
    subprocess.run([sys.executable, "-m", "backend.cli", "init"])

def install_dependencies():
    """Install all dependencies"""
    print("📦 Installing backend dependencies...")
    os.chdir("backend")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("📦 Installing frontend dependencies...")
    os.chdir("../frontend")
    subprocess.run(["npm", "install"])

def run_tests():
    """Run the test suite"""
    print("🧪 Running test suite...")
    os.chdir("tests")
    subprocess.run([sys.executable, "-m", "pytest", "-v"])

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Android Poster Runner")
    parser.add_argument(
        "command", 
        choices=["backend", "frontend", "init", "install", "test"],
        help="Command to run"
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    if args.command == "backend":
        run_backend()
    elif args.command == "frontend":
        run_frontend()
    elif args.command == "init":
        init_database()
    elif args.command == "install":
        install_dependencies()
    elif args.command == "test":
        run_tests()

if __name__ == "__main__":
    main()