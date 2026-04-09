import os
import traceback
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.logging.logger import logger
from config import config

VECTORSTORE_PATH = "embeddings/"

def get_embeddings():
    logger.info("Initializing HuggingFace embeddings...")
    return HuggingFaceEndpointEmbeddings(
        model='MongoDB/mdbr-leaf-ir',
        huggingfacehub_api_token=config.HUGGINGFACE_API_KEY
    )

def create_vectorstore():
    logger.info("Creating a new vectorstore...")
    try:
        embeddings = get_embeddings()
        os.makedirs("data", exist_ok=True)
        
        if os.path.exists("data/sample.txt"):
            logger.info("Loading from data/sample.txt...")
            loader = TextLoader("data/sample.txt", encoding="utf-8")
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
            split_docs = splitter.split_documents(docs)
            vectorstore = FAISS.from_documents(split_docs, embeddings)
        else:
            logger.info("No sample.txt found. Creating minimal initial vectorstore.")
            vectorstore = FAISS.from_texts(
                ["Knowledge base initialized."], 
                embeddings,
                metadatas=[{"source": "system"}]
            )
        
        os.makedirs(VECTORSTORE_PATH, exist_ok=True)
        vectorstore.save_local(VECTORSTORE_PATH)
        logger.info(f"Vectorstore created and saved to {VECTORSTORE_PATH}")
        return vectorstore
    except Exception as e:
        logger.error(f"Error in create_vectorstore: {e}\n{traceback.format_exc()}")
        raise

def load_vectorstore():
    try:
        embeddings = get_embeddings()
        if not os.path.exists(VECTORSTORE_PATH):
            return create_vectorstore()
        
        logger.info(f"Loading existing vectorstore from {VECTORSTORE_PATH}")
        return FAISS.load_local(
            VECTORSTORE_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        logger.error(f"Error loading vectorstore: {e}. Recreating...")
        logger.debug(traceback.format_exc())
        return create_vectorstore()

def get_retriever_tool():
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    tool = create_retriever_tool(
        retriever,
        "knowledge_base_search_tool",
        "Search and return information from the uploaded documents and workbooks."
    )
    return tool