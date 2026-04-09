import os
import traceback
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.retriever import load_vectorstore, VECTORSTORE_PATH
from src.logging.logger import logger

def ingest_document(file_path):
    logger.info(f"Ingesting document: {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == '.pdf':
            loader = PyPDFLoader(file_path)
            docs = loader.load()
        elif file_extension == '.docx':
            loader = Docx2txtLoader(file_path)
            docs = loader.load()
        else:
            logger.error(f"Unsupported file format: {file_extension}")
            return False

        if not docs:
            logger.warning(f"No content loaded from {file_path}")
            return False

        logger.info(f"Loaded {len(docs)} pages/sections from {file_path}")

        for doc in docs:
            if 'source' in doc.metadata:
                doc.metadata['source'] = os.path.basename(doc.metadata['source'])
            else:
                doc.metadata['source'] = os.path.basename(file_path)

        splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        split_docs = splitter.split_documents(docs)
        
        if not split_docs:
            logger.warning(f"Document split resulted in 0 chunks for {file_path}")
            return False
            
        logger.info(f"Split document into {len(split_docs)} chunks")

        logger.info("Accessing vectorstore for update...")
        vectorstore = load_vectorstore()
        
        logger.info(f"Adding {len(split_docs)} documents to vectorstore...")
        vectorstore.add_documents(split_docs)
        
        logger.info("Saving vectorstore locally...")
        vectorstore.save_local(VECTORSTORE_PATH)
        
        logger.info(f"SUCCESS: Ingested {len(split_docs)} chunks from {file_path} into vectorstore.")
        return True
    except Exception as e:
        logger.error(f"Error during ingestion: {e}\n{traceback.format_exc()}")
        return False
