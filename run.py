#!/usr/bin/env python3
"""
Life Tracker - Startup Script

This script starts the Life Tracker application with proper configuration.
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"Starting Life Tracker on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')}")
    
    # Start the application
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 