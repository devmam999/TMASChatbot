#!/usr/bin/env python3
"""
Simple script to test AI service connection
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService

async def test_connection():
    """Test the AI service connection"""
    print("Testing AI service connection...")
    
    try:
        ai_service = AIService()
        print(f"✅ AI service initialized with model: {ai_service.model}")
        
        # Test connection
        if await ai_service.test_connection():
            print("✅ Connection test successful")
        else:
            print("❌ Connection test failed")
            
        # Test a simple response
        print("Testing simple response generation...")
        explanation, manim_code = await ai_service.generate_simple_response("Hello, this is a test.")
        print(f"✅ Simple response generated: {explanation[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the test
    success = asyncio.run(test_connection())
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1) 