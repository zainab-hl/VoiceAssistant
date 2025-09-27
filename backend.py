import os
import asyncio
import numpy as np
from dotenv import load_dotenv
import uvicorn
import wavio
from fastapi import FastAPI, UploadFile, File
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from deepgram import Deepgram
from elevenlabs.client import ElevenLabs

# Load API keys
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Clients
genie_client = genai.Client(api_key=GEMINI_API_KEY)
dg_client = Deepgram(DEEPGRAM_API_KEY)
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Assistant context, change it based on your use case (your name, the assistant's name and personality)
context = "You are jarvis, Zainab's friendly AI assistant. Keep answers short and kind."

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str

async def transcribe_audio(file_path):
    with open(file_path, "rb") as f:
        source = {"buffer": f, "mimetype": "audio/wav"}  
        response = await dg_client.transcription.prerecorded(source)
        words = response["results"]["channels"][0]["alternatives"][0]["words"]
        return " ".join([w["word"] for w in words])

def request_gemini(prompt: str):
    response = genie_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def speak(text, output_file="audio/response.wav"):
    audio_generator = eleven_client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="pcm_16000"
    )
    audio_bytes = b"".join(audio_generator)
    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
    os.makedirs("audio", exist_ok=True)
    wavio.write(output_file, audio_array, 16000, sampwidth=2)
    return output_file

# Endpoints 

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    file_path = f"audio/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    text = await transcribe_audio(file_path)
    return {"transcript": text}


app.mount("/audio", StaticFiles(directory="audio"), name="audio")

@app.post("/ask")
async def ask(message: Message, request: Request):
    global context
    context += f"\nZainab: {message.text}\njarvis : "
    response = request_gemini(context)
    context += response
    audio_file = speak(response)

    base_url = str(request.base_url).rstrip("/")  
    return {
        "response": response,
        "audio_file": f"{base_url}/{audio_file}"
    }
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)