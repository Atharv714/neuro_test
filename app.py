from fastapi import FastAPI, UploadFile, File
import io
import pickle
from pydub import AudioSegment
from fastapi.responses import JSONResponse
from openai import OpenAI
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict it later to your frontend's domain)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAIKEY'))

# FastAPI route for processing audio
@app.post("/process_audio/")
async def process_audio(file: UploadFile = File(...)):
    try:
        # Read the uploaded audio file
        audio_data = await file.read()

        # Convert the uploaded file to .mp3 format using pydub
        audio = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
        output_io = io.BytesIO()
        audio.export(output_io, format="mp3")
        output_io.seek(0)
        
        # Create a BytesIO object for transcription
        audio_file = io.BytesIO(output_io.read())
        audio_file.name = "output.mp3"

        # Save the output_io object for debugging 
        with open("output_io.pkl", "wb") as f:
            pickle.dump(output_io, f)

        # Save the MP3 file locally for testing purposes 
        with open("output.mp3", "wb") as f:
            f.write(output_io.getvalue())

        # OpenAI whisper
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
        transcript = transcription.text
 
        transcriptor_prompt = "You are the best transcriber correcter, you will fix the transcriptions in the most accurate way possible, and also in the language in which transcription is provided, you are proficient in english, hindi, marathi, gujrati, bengali, and other various indian languages and you have to any how, fix the transcription, there should not be even a single discrepancy"

        fixtranscribe = client.chat.completions.create(
            model = "gpt-4o",
            messages = [
                {
                    "role": "system",
                    "content": transcriptor_prompt
                },

                {
                    "role": "user",
                    "content": transcript
                }
            ]
        )

        fixtranscribereturn = fixtranscribe.choices[0].message.content
        print(fixtranscribereturn)

        # only for verification
        response_data = {
            "transcription": transcript,
            "audioUrl": "http://127.0.0.1:8000/output.mp3"  
        }

        return JSONResponse(content=response_data)

    except Exception as e:
        return {"error": str(e)}

