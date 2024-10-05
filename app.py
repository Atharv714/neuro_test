from fastapi import FastAPI, UploadFile, File
import io
import pickle
from pydub import AudioSegment
from fastapi.responses import JSONResponse, FileResponse
from openai import OpenAI
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

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
 
        transcriptor_prompt = "You are an expert transcriber specializing in Indian accents and languages. Your job is to refine transcriptions provided by the Whisper model, correcting errors that occur due to Indian accents or mixed language usage. Ensure that the final transcription accurately represents the original audio by fixing misheard words, handling code-switching (e.g., English mixed with Hindi or other Indian languages), and making minor punctuation or grammatical corrections as needed. Maintain the natural flow and meaning of the original speech while ensuring clarity and readability."

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

        usertranscript = fixtranscribe.choices[0].message.content
        print(usertranscript)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": open_file('prompts.md')},
                {"role": "user", "content": usertranscript}
            ],
            temperature=0.7
        )
        neurify = response.choices[0].message.content



        # only for verification
        # response_data = {
        #     "transcription": transcript,
        #     "audioUrl": "http://127.0.0.1:8000/output.mp3"  
        # }

        depressed_flag = is_depressed(usertranscript)
        sad_flag = is_sad(usertranscript)

        audio_url = convert_to_speech(neurify)

        response_data = {
            'chat_response': neurify,
            'audio_url': audio_url,
            'depressed_flag': depressed_flag,
            'sad_detector': sad_flag
        }

        # Print the response data to the console (or logs)
        print("Response being sent to frontend:", response_data)

        # Return the JSON response
        return JSONResponse(response_data)


    except Exception as e:
        return {"error": str(e)}

import time 

def convert_to_speech(text):
    speech_file_path = "output.mp3"
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )

    # Save the generated audio to a file
    response.stream_to_file(speech_file_path)

    # Return the URL to the saved audio file with a timestamp to avoid caching
    return f"/output.mp3?{int(time.time())}"

# vedar sentimental analysis

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    sentiment_score = analyzer.polarity_scores(text)
    return sentiment_score['compound']

def is_depressed(message):
    sentiment_score = analyze_sentiment(message)
    return sentiment_score < -0.5

def is_sad(message):
    sentiment_score = analyze_sentiment(message)
    return sentiment_score < -0.2


@app.get("/output.mp3")
def serve_audio():
    return FileResponse("output.mp3")

