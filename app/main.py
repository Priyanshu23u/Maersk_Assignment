# app/main.py
import streamlit as st
import hashlib
from chatbot import ChatBot
from data_loader import load_olist_data
from config import GEMINI_API_KEY, MODEL_NAME, DATA_PATH
from visualizer import visualize_result

# ------------------------ PAGE SETUP ------------------------
st.set_page_config(page_title="E-Commerce Insight Chat", page_icon="🧠", layout="wide")

st.markdown(
    """
    <style>
        .user-msg {
            background-color: #DCF8C6;
            color: #000;
            padding: 10px 15px;
            border-radius: 15px 15px 0px 15px;
            max-width: 70%;
            margin: 5px 0 5px auto;
            display: block;
        }
        .bot-msg {
            background-color: #E3E3E3;
            color: #000;
            padding: 10px 15px;
            border-radius: 15px 15px 15px 0px;
            max-width: 70%;
            margin: 5px auto 5px 0;
            display: block;
        }
        .chat-box {
            max-height: 550px;
            overflow-y: auto;
            padding: 10px;
            border-radius: 10px;
            background-color: #F8F9FA;
            border: 1px solid #ddd;
        }
        .title {
            font-size: 28px;
            color: #075E54;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='title'>🧠 GenAI E-Commerce Insight Assistant</div>", unsafe_allow_html=True)
st.caption("Chat naturally to explore insights from the Olist e-commerce dataset.")

# ------------------------ LOAD DATA ------------------------
@st.cache_data(show_spinner=True)
def get_data():
    return load_olist_data(DATA_PATH)

data = get_data()

# ------------------------ SESSION STATE ------------------------
if "bot" not in st.session_state:
    st.session_state.bot = ChatBot(GEMINI_API_KEY, MODEL_NAME, data)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # [{"role": "user"/"bot", "text": str, "data": pd.DataFrame | None}]

bot: ChatBot = st.session_state.bot

# Add initial greeting
if not st.session_state.chat_history:
    st.session_state.chat_history.append({
        "role": "bot",
        "text": "👋 Hello! I’m your AI assistant. Ask me anything about the Olist dataset — "
                "for example, *'Which city placed the most orders last year?'* or *'Show average delivery days by state.'*",
        "data": None
    })

# ------------------------ LAYOUT ------------------------
col1, col2 = st.columns([3, 1])

with col2:
    st.markdown("### 💡 Demo Queries")
    demo_queries = [
        "What is English word of moveis_decoracao?",
        "Which state generated the highest total revenue?",
        "What is the maximum product width in centimeters?",
        "Average delivery_days per customer_state",
        "Top 5 product categories by total_order_value in 2018"
    ]

    selected_query = None
    for q in demo_queries:
        key_hash = hashlib.md5(q.encode()).hexdigest()[:8]
        if st.button(q, key=f"demo_{key_hash}"):
            selected_query = q

    st.markdown("---")
    if st.button("🔄 Clear Chat History"):
        st.session_state.chat_history = []
        bot.memory.clear()
        st.success("Chat history cleared!")
        st.rerun()

with col1:
    # Display Chat
    st.markdown("### 💬 Chat")
    chat_box = st.container()

    with chat_box:
        st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"<div class='user-msg'>{msg['text']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bot-msg'>{msg['text']}</div>", unsafe_allow_html=True)
                if "data" in msg and msg["data"] is not None:
                    visualize_result(msg["text"], msg["data"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    user_query = st.text_input("Type your message:", placeholder="e.g., Average review_score by category", key="user_input")

    final_query = selected_query or user_query.strip()

    if st.button("Send") or selected_query:
        if final_query:
            # Add user message
            st.session_state.chat_history.append({"role": "user", "text": final_query, "data": None})

            # Run bot
            with st.spinner("Thinking..."):
                output = bot.ask(final_query)
                answer_text = output["answer"]
                result_df = output["result"]

            # Add bot message
            st.session_state.chat_history.append({"role": "bot", "text": answer_text, "data": result_df})

            st.rerun()
        else:
            st.warning("Please type or select a question first.")
