import os
import io
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from openai import OpenAI

app = FastAPI()

# Cloud environment se secret API key read karega
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def home():
    return {"status": "AI Assistant Backend Online"}

@app.websocket("/ws/audio")
async def audio_stream(websocket: WebSocket):
    await websocket.accept()
    print("ESP32 Connected via WebSocket!")
    
    try:
        while True:
            # 1. ESP32 se raw recorded audio aayega
            audio_bytes = await websocket.receive_bytes()
            print(f"Received audio packet: {len(audio_bytes)} bytes")
            
            # Temporary audio file bana kar Whisper STT ko bhejna
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "input.wav"
            
            # 2. Speech-to-Text (STT)
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            user_text = transcription.text
            print(f"User said: {user_text}")
            
            if not user_text.strip():
                continue
            
            # 3. ChatGPT Intelligence (LLM)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a witty, concise voice assistant like Alexa. Keep answers under 2 sentences."},
                    {"role": "user", "content": user_text}
                ]
            )
            ai_text = response.choices[0].message.content
            print(f"AI response: {ai_text}")
            
            # 4. Text-to-Speech (TTS)
            tts_response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                response_format="pcm", # raw PCM stream for ESP32 MAX98357A
                input=ai_text
            )
            
            # 5. Audio wapas ESP32 ko stream karna
            await websocket.send_bytes(tts_response.content)
            print("Response audio sent to ESP32!")
            
    except WebSocketDisconnect:
        print("ESP32 Disconnected")
    except Exception as e:
        print(f"Error: {e}")