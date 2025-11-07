import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Paths
DATA_PATH = "./data"

# Model config
MODEL_NAME = "gemini-1.5-pro"
