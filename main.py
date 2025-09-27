import os
import asyncio
from time import time
import pygame
from dotenv import load_dotenv
from google import genai
from deepgram import Deepgram
from pygame import mixer
from elevenlabs.client import ElevenLabs
from recordor import record_until_silence
import numpy as np
import wavio

# Load APIs keys from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Initializing
genie_client = genai.Client(api_key=GEMINI_API_KEY)
dg_client = Deepgram(DEEPGRAM_API_KEY)
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY) 

#mixer is a pygame module for playing sounds
mixer.init()

# Assistant context, depending on your use case
context = "You are Assoral, Zainab's friendly and supportive AI assistant. Keep answers short and kind."

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

def speak(text):
    """
    Generate speech from text using ElevenLabs and play instantly with Pygame
    """
    # new elevenlabs method to get audio as a generator, (old methode : elevenlabs.generate)
    audio_generator = eleven_client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="pcm_16000"  
    )

    audio_bytes = b"".join(audio_generator)
    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

    # Saving
    output_file = "audio/response.wav"
    wavio.write(output_file, audio_array, 16000, sampwidth=2)

    # instant playing
    sound = mixer.Sound(output_file)
    sound.play()
    pygame.time.wait(int(sound.get_length() * 1000))

    return output_file

if __name__ == "__main__":
    print("=== jarvis Voice Assistant ===\nSay something to start the conversation.\n")
    conv_file = "conv.txt"

    if not os.path.exists(conv_file):
        with open(conv_file, "w") as f:
            f.write("")

    while True:
        # Record
        audio_file = record_until_silence()
        if not audio_file:
            continue

        # Transcribe
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        transcript = loop.run_until_complete(transcribe_audio(audio_file))

        print(f"\nZaina: {transcript}")

        with open(conv_file, "a", encoding="utf-8") as f:
            f.write(f"{transcript}\n")

        # Generate AI response
        context += f"\nZaina: {transcript}\n Jarvis: "
        response = request_gemini(context)
        context += response
        print(f"Jarvis: {response}")

        with open(conv_file, "a", encoding="utf-8") as f:
            f.write(f"{response}\n")

        # Convert response to speech & play
        speak(response)
