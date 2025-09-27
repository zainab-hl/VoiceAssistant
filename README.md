Your personal Ai voice assistant: Voice to Text to LLM to Speech, displayed in a mobile interface.

## Features
- The user speaks into the microphone (mobile)
- Voice is converted to text using Deepgram
- Text is sent to Google's gemini-2.5-flash API to generate a response
- Response is converted to speech using ElevenLabs
- Speech is played using Pygame
- Conversation is displayed in a mobile interface using tsx

## Requirements
Make sure you have the following API keys:
Deepgram
Gemini
Elevenlabs

Create a .env file in the root directory and add the following variables:
```env
DEEPGRAM_API_KEY=XXX...XXX
OPENAI_API_KEY=sk-XXX...XXX
ELEVENLABS_API_KEY=XXX...XXX
```

## How to use 
1. Install the requirements:

```
pip install -r requirements.txt
```
- change the github url to (github.dev) to test in visual studio code by running in the terminal:
```
python backend.py
```
then
```
cd chatUI
npx install
npx expo start
```
Or simply clone the repository
```
git clone https://github.com/zainab-hl/VoiceAssistant.git
```

