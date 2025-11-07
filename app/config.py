import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.0-flash"

# Data path
DATA_PATH = "./data"
