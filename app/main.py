# app/main.py
import streamlit as st
from chatbot import ChatBot
from data_loader import load_olist_data
from config import GEMINI_API_KEY, MODEL_NAME, DATA_PATH

st.set_page_config(page_title="GenAI E-Commerce Insight Assistant", page_icon="🧠", layout="wide")
st.title("🧠 GenAI E-Commerce Insight Assistant")
st.caption("Chat with the Olist e-commerce dataset using Gemini 2.0 Flash")

# Load & cache data
@st.cache_data(show_spinner=True)
def get_data():
    return load_olist_data(DATA_PATH)

data = get_data()

# Initialize bot (do not reload on every rerun)
if "bot" not in st.session_state:
    st.session_state.bot = ChatBot(GEMINI_API_KEY, MODEL_NAME, data)

bot: ChatBot = st.session_state.bot

# UI
user_input = st.text_input("💬 Ask a question (e.g., 'Average delivery time by state')", key="input")

if st.button("Ask"):
    if not user_input.strip():
        st.warning("Please type a question.")
    else:
        with st.spinner("Thinking..."):
            answer = bot.ask(user_input)
            # display the English summary (if returned)
            if isinstance(answer, str):
                # Render the answer in a nicely formatted card
                st.markdown("---")
                st.markdown(f"<div style='background:#0b2545;color:#eaf4ff;padding:12px;border-radius:8px;'>"
                            f"{answer}</div>", unsafe_allow_html=True)
                st.markdown("---")
