import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the root directory
load_dotenv()

class Config:
    """Centralized configuration for the agent."""
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Using the newer Gemini 2.x models for better performance
    # Switched REDUCE_MODEL to flash to avoid free-tier quota limits
    MAP_MODEL = os.getenv("MAP_MODEL", "gemini-2.5-flash")
    REDUCE_MODEL = os.getenv("REDUCE_MODEL", "gemini-2.5-flash")

    @classmethod
    def validate(cls):
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is missing. Please check your .env file.")