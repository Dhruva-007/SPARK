"""
SPARK — Test Configuration
Sets up the test environment.
"""

import os
import sys

# Ensure the backend directory is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment
os.environ["APP_ENV"] = "development"
os.environ["FIREBASE_PROJECT_ID"] = ""
os.environ["GOOGLE_CLOUD_PROJECT"] = ""