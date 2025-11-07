import streamlit as st
from app.chatbot import ChatBot
from app.data_loader import load_olist_data
from app.config import GEMINI_API_KEY, MODEL_NAME, DATA_PATH

st.set_page_config(page_title="E-Commerce Insight Assistant", page_icon="💬")

st.title("🧠 GenAI E-Commerce Insight Assistant")

# Load data once
@st.cache_data
def get_data():
    return load_olist_data(DATA_PATH)

data = get_data()

# Initialize chatbot
bot = ChatBot(GEMINI_API_KEY, MODEL_NAME, data)

# Chat interface
user_input = st.text_input("Ask about your data (e.g., 'Top 5 categories by revenue in 2018'):")

if st.button("Ask"):
    if user_input:
        with st.spinner("Thinking..."):
            response = bot.ask(user_input)
            st.write(response)
