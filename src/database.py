from supabase import create_client, Client
from src.logging.logger import logger
from config import config

SUPABASE_URL = config.SUPABASE_URL
SUPABASE_KEY = config.SUPABASE_KEY

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("Supabase credentials not found in config. Database operations will fail.")

def get_supabase_client() -> Client:
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase URL and Key are required to create a client.")
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        raise

def insert_document_record(filename: str):
    try:
        supabase = get_supabase_client()
        data = supabase.table("documents").insert({"filename": filename}).execute()
        
        if data.data:
            logger.info(f"Successfully inserted document record: {filename}")
            return data.data[0].get("id")
        return None
    except Exception as e:
        logger.error(f"Error inserting document record: {e}")
        return None

def delete_document_record(file_id: str):
    try:
        supabase = get_supabase_client()
        supabase.table("documents").delete().eq("id", file_id).execute()
        logger.info(f"Deleted document record: {file_id}")
    except Exception as e:
        logger.error(f"Error deleting document record: {e}")
