#!/usr/bin/env python3
"""
Simple startup script for the Subscription Service
"""

import os
import sys
from app.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting Subscription Service...")
    print("Documentation will be available at:")
    print("- Swagger UI: http://localhost:8000/docs")
    print("- ReDoc: http://localhost:8000/redoc")
    print("- Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the service\n")
    
    try:
        uvicorn.run(
            "app.main:app",
            host=os.getenv("APP_HOST", "0.0.0.0"),
            port=int(os.getenv("APP_PORT", 8000)),
            reload=os.getenv("DEBUG", "True").lower() == "true"
        )
    except KeyboardInterrupt:
        print("\nService stopped by user")
    except Exception as e:
        print(f"Error starting service: {e}")
        sys.exit(1)