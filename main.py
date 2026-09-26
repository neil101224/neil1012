import os
from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# Render environment se secret key lega
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

class PromptRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"status": "AI Assistant Backend Online"}

@app.post("/chat")
def chat_endpoint(req: PromptRequest):
    try:
        prompt = f"Answer in under 2 sentences like a smart, witty voice assistant: {req.message}"
        response = model.generate_content(prompt)
        return {"status": "success", "reply": response.text.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
