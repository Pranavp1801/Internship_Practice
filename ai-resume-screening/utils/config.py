from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

load_dotenv()

def get_llm(temperature=0.2):
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=temperature
    )