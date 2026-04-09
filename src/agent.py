import os
from dotenv import load_dotenv
from typing import List, Dict

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

from config import config
from src.logging.logger import logger

load_dotenv()

llm = ChatGroq(
    api_key=config.GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0
)

@tool
def knowledge_base_search(query: str):
    """
    Search the knowledge base for information from uploaded documents and workbooks.
    Always use this tool when answering questions that require specific project context or factual information from files.
    """
    from src.retriever import load_vectorstore
    logger.info(f"Tool calling: knowledge_base_search with query '{query}'")
    
    try:
        vectorstore = load_vectorstore()
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(query)
        
        if not docs:
            return "No relevant information found in the knowledge base."
            
        formatted_results = []
        for doc in docs:
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content
            formatted_results.append(f"[Source: {source}]\n{content}")
        
        return "\n\n---\n\n".join(formatted_results)
    except Exception as e:
        logger.error(f"Error in knowledge_base_search tool: {e}")
        return f"Error retrieving information: {str(e)}"

tools = [knowledge_base_search]

agent_system_prompt = """You are a professional AI assistant for the AI Copilot application.
Your goal is to provide accurate and concise information based on the documents in your knowledge base.

- Use the `knowledge_base_search` tool ONLY when necessary to find relevant information.
- If the tool results don't contain the answer, state that you don't know based on the documents.
- Always include inline citations for information derived from the tool, e.g., "[Source: doc.pdf]".
- Maintain a helpful and professional tone."""

def build_agent_executor():
    logger.info("Building Tool-Calling Agent using modern LangChain 1.x / LangGraph...")
    
    agent = create_agent(
        model=llm, 
        tools=tools, 
        system_prompt=agent_system_prompt
    )
    
    return agent

_agent = build_agent_executor()

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

async def chat(query: str, session_id: str = "default"):
    try:
        logger.info(f"Querying Agent for session {session_id}")
        
        history = get_session_history(session_id)
        chat_history = history.messages
        
        messages = chat_history + [HumanMessage(content=query)]
        
        response = _agent.invoke(
            {"messages": messages},
            config={"configurable": {"thread_id": session_id}},
            verbose=True
        )
        
        answer_message = response["messages"][-1]
        answer = answer_message.content
        
        history.add_user_message(query)
        history.add_ai_message(answer)
        
        return answer
    except Exception as e:
        logger.error(f"Error in Agent invocation: {e}")
        return f"I encountered an error processing your request: {e}"

def refresh_agent():
    global _agent
    logger.info("Refreshing Agent context...")
    _agent = build_agent_executor()
