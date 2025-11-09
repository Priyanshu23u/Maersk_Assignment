import google.generativeai as genai
from app.config import GEMINI_API_KEY, MODEL_NAME

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

response = model.generate_content("Say hello from Gemini 2.0 Flash!")
print(response.text)
