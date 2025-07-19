#!/usr/bin/env python3
"""
Life Tracker - Setup Script

This script helps set up the Life Tracker application with initial configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        print("\nCreating .env file...")
        env_content = """# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/life_tracker

# Application Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True

# Optional: Logging
LOG_LEVEL=INFO
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✓ .env file created")
        print("⚠️  Please edit .env file with your actual database credentials")
    else:
        print("✓ .env file already exists")

def install_dependencies():
    """Install Python dependencies"""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def setup_database():
    """Set up database and run migrations"""
    print("\nSetting up database...")
    
    # Check if PostgreSQL is running
    if not run_command("pg_isready", "Checking PostgreSQL connection"):
        print("⚠️  PostgreSQL might not be running. Please start PostgreSQL and try again.")
        return False
    
    # Create database if it doesn't exist
    if not run_command("createdb life_tracker", "Creating database"):
        print("⚠️  Database might already exist or PostgreSQL is not accessible")
    
    # Run migrations
    if not run_command("alembic upgrade head", "Running database migrations"):
        print("⚠️  Database migrations failed. Please check your database connection.")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Life Tracker Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("\n❌ Setup failed at database setup")
        print("Please check your PostgreSQL installation and .env configuration")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your database credentials")
    print("2. Run the application: python run.py")
    print("3. Open http://localhost:8000 in your browser")
    print("4. Check API documentation at http://localhost:8000/docs")

if __name__ == "__main__":
    main() 