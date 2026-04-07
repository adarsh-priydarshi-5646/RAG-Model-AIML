import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it before running the application.\nFor Groq: export OPENAI_API_KEY=gsk_your_key_here")

DATA_PATH = "data/raw/"
VECTOR_DB_PATH = "vectorstore/db/"