from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Openrouter client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Personality presets
PERSONALITIES = {
    "study": """
You are a helpful study companion for college students.
You explain concepts clearly, encourage curiosity,
and keep answers concise.
When you don't know something, say so honestly.
""",

    "friend": """
You are a supportive and friendly AI companion.
You talk casually, warmly, and naturally like a close friend.
Keep conversations engaging and comforting.
""",

    "anime": """
You are a cheerful anime-style AI companion.
You are playful, expressive, energetic, and emotionally supportive.
Keep responses fun and conversational.
"""
}

# Temporary in-memory chat history
# (fine for MVP/demo project)
chat_history = []

# Request body model
class Message(BaseModel):
    content: str
    personality: str = "friend"


@app.get("/")
def root():
    return {"message": "AI Companion Backend Running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(message: Message):

    # Select personality
    system_prompt = PERSONALITIES.get(
        message.personality,
        PERSONALITIES["friend"]
    )

    # Add user message
    chat_history.append({
        "role": "user",
        "content": message.content
    })

    # Keep only recent messages
    recent_history = chat_history[-10:]

    try:
        # OpenAI API call
        response = client.chat.completions.create(
            model="google/gemma-4-31b-it:free",
            messages=[
                {"role": "system", "content": system_prompt}
            ] + recent_history,
            max_tokens=500,
            temperature=0.8,
        )

        reply = response.choices[0].message.content

        # Save assistant reply
        chat_history.append({
            "role": "assistant",
            "content": reply
        })

        return {
            "reply": reply,
            "personality": message.personality
        }

    except Exception as e:
        return {"error": str(e)}
        
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    timeout=30
)
