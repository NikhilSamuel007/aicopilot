import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HUGGING_FACE_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

config = Config()
