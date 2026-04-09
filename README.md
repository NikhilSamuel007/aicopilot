# AI Copilot: Intelligent Document RAG Agent

AI Copilot is a high-performance Retrieval-Augmented Generation (RAG) agent built with **FastAPI**, **LangChain**, and **LangGraph**. It utilizes **Groq (Llama 3.1)** for reasoning and **FAISS** for efficient local vector storage, combined with **Supabase** for document metadata tracking.

## 🚀 Features

- **Tool-Calling Agent**: Uses LangChain / LangGraph patterns to intelligently decide when to search the knowledge base.
- **Multi-Format Support**: Seamlessly ingest and query information from **PDF** and **DOCX** files.
- **Fast Inference**: Powered by **Groq** for lightning-fast LLM responses.
- **Modern Embeddings**: Uses `langchain-huggingface` with high-quality inference-based embeddings.
- **Real-Time Interaction**: Supports both standard REST API endpoints and **WebSockets** for conversational interfaces.
- **Source Citations**: Every answer includes inline citations (e.g., `[Source: document.pdf]`) to ensure factual accuracy.

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **LLM**: Groq (Llama 3.1 8B)
- **Framework**: LangChain, LangGraph
- **Vectorstore**: FAISS (CPU)
- **Database**: Supabase (PostgreSQL)
- **Embeddings**: HuggingFace Inference API

## 📋 Prerequisites

- Python 3.10+
- A Supabase account and project
- A Groq API key
- A HuggingFace API token

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/aicopilot.git
cd aicopilot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the `.env.example` file to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

### 4. Database Setup
Run the provided SQL script in your Supabase **SQL Editor** to create the required tables:
1. Open [supabase_setup.sql](./supabase_setup.sql).
2. Copy and paste the contents into your Supabase dashboard and click **Run**.

## 🏃 Running the Application

Start the FastAPI server:
```bash
python app.py
```
The server will be available at `http://127.0.0.1:8000`.

## 📍 API Endpoints

- `GET /health`: Verify the API status.
- `POST /upload-doc`: Upload a PDF or DOCX file for indexing.
- `POST /query`: Send a question to the RAG agent.
- `WS /ws`: Connect via WebSocket for real-time chat.
- `GET /docs`: Interactive Swagger UI documentation.

## 🛡️ License
This project is licensed under the MIT License.
