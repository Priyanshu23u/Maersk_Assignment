import streamlit as st
from app.chatbot import ChatBot
from app.data_loader import load_olist_data
from app.config import GEMINI_API_KEY, MODEL_NAME, DATA_PATH

st.set_page_config(page_title="E-Commerce Insight Assistant", page_icon="🧠", layout="wide")

st.title("🧠 GenAI E-Commerce Insight Assistant")
st.caption("Chat with the Olist e-commerce dataset using Gemini 2.0 Flash")

@st.cache_data
def get_data():
    return load_olist_data(DATA_PATH)

data = get_data()
bot = ChatBot(GEMINI_API_KEY, MODEL_NAME, data)

user_input = st.text_input("💬 Ask a question (e.g., 'Average delivery time by state')")

if st.button("Ask"):
    if user_input.strip():
        with st.spinner("Thinking..."):
            st.write(bot.ask(user_input))
    else:
        st.warning("Please enter a valid question.")
