#!/usr/bin/env python3
"""
Simple script to start the server without AI service dependency
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Start the server"""
    print("🚀 Starting TMAS Chatbot Server...")
    print("ℹ️ AI service will be tested on first request")
    
    # Import settings
    from utils.config import settings
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    main() 