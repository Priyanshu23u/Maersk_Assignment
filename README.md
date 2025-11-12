# 🧠 GenAI-Powered E-Commerce Insight Assistant  
> *Conversational Data Analyst for the Olist Brazilian E-Commerce Dataset*

---

## 📖 Project Overview

The **GenAI E-Commerce Insight Assistant** is a **chat-based data analysis system** that lets users explore the [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) through **natural-language queries**.

Powered by **Google Gemini 2.0 Flash**, **DuckDB**, and **Streamlit**, it converts your text questions into **SQL queries**, executes them, and replies with **insightful explanations, charts, and downloadable reports** — just like chatting with a data analyst!

---

## 🚀 Key Features

| Feature | Description |
|----------|-------------|
| 💬 **Conversational Interface** | WhatsApp-style chat UI built in Streamlit |
| 🧠 **LLM-Driven Query Generation** | Gemini converts plain English (or Hindi/Portuguese) to SQL |
| 📊 **Smart Visualization** | Auto-selects best chart type (bar, line, pie, scatter) |
| 📄 **Report Export** | Download results as CSV or PDF |
| 🌍 **Multilingual Understanding** | Handles English, Hindi, and Portuguese |
| 💡 **Definition Lookup** | Explains metrics like AOV, freight_value, etc. |
| 🧩 **Context Memory** | Follows up naturally (“now show only electronics”) |
| ⚙️ **Retry & Caching Logic** | Gracefully handles API rate limits |
| 🖼️ **Persistent Chat History** | Previous messages remain until cleared |

---

## 🏗️ Project Architecture

         ┌────────────────────────┐
         │     User Interface      │
         │ (Streamlit Frontend)    │
         └────────────┬────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │     Chat Processor      │
         │ (Gemini 2.0 Flash)      │
         └────────────┬────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   SQL / Pandas Engine   │
         │  (DuckDB + Executor)    │
         └────────────┬────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   Olist Dataset Merged  │
         │ (9 CSV Files → DF)      │
         └────────────┬────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   Result Interpreter    │
         │ (Charts + Summaries)    │
         └────────────────────────┘


---

## 🗂️ Folder Structure
```bash
genai_ecom_insights/
│
├── app/
│ ├── main.py
│ ├── chatbot.py 
│ ├── query_executor.py 
│ ├── data_loader.py 
│ ├── visualizer.py 
│ ├── utils.py 
│ ├── config.py 
│
├── data/
│ ├── olist_orders_dataset.csv
│ ├── olist_customers_dataset.csv
│ ├── olist_order_items_dataset.csv
│ ├── olist_products_dataset.csv
│ ├── olist_order_reviews_dataset.csv
│ ├── olist_order_payments_dataset.csv
│ ├── olist_geolocation_dataset.csv
│ ├── olist_sellers_dataset.csv
│ ├── product_category_name_translation.csv
│
├── .env ← Contains GEMINI_API_KEY
├── requirements.txt
├── README.md
└── screenshots.md
```
## 🧠 Tech Stack

| Layer | Technology | Purpose |
|--------|-------------|----------|
| 💻 **Frontend** | [Streamlit](https://streamlit.io/) | Builds the chat-style web UI (WhatsApp-like interface) |
| 🧠 **LLM Backend** | [Google Gemini 2.0 Flash](https://ai.google.dev/) | Natural language understanding, SQL generation, summaries |
| 🗃️ **Database Engine** | [DuckDB](https://duckdb.org/) | In-memory analytical SQL engine for fast queries |
| 📊 **Visualization** | [Plotly Express](https://plotly.com/python/plotly-express/) | Dynamic and interactive charts (bar, line, pie, scatter) |
| 🧾 **Report Generation** | [FPDF](https://pypi.org/project/fpdf/) | Creates downloadable PDF summaries |
| 🌍 **Language Translation** | Gemini model (built-in translation) | Supports Hindi, Portuguese, and English queries |
| 💬 **Conversation Memory** | Python `deque` (LangChain-style) | Retains context for follow-up queries |
| 🧩 **Data Handling** | [Pandas](https://pandas.pydata.org/) | Data cleaning, merging, and transformation |
| ⚙️ **Error Handling & Retry** | `google.api_core.exceptions` | Graceful handling of rate limits (429 errors) |
| 🔐 **Configuration** | `.env` + `dotenv` | Secure API key management |
| ☁️ **Deployment** | [Streamlit Cloud](https://streamlit.io/cloud) / [Hugging Face Spaces](https://huggingface.co/spaces) | Optional hosting platform |


