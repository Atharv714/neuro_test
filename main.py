from flask import Flask, render_template, request, jsonify, send_from_directory, session
import os
import re
from openai import OpenAI
from pydub import AudioSegment
import io
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

load_dotenv()

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    sentiment_score = analyzer.polarity_scores(text)
    return sentiment_score['compound']

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session handling

avaj = 'echo'

def get_conversation_history():
    return session.get("conversation_history", [])

# Function to update conversation history
def update_conversation_history(role, content):
    conversation_history = get_conversation_history()
    conversation_history.append({"role": role, "content": content})
    session["conversation_history"] = conversation_history

# Function to clear conversation history
def clear_conversation_history():
    session.pop("conversation_history", None)



def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

def send_message(message):
    if not isinstance(message, str):
        raise ValueError("Message must be a string")
    
    update_conversation_history("user", message)

    conversation_history = get_conversation_history()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": open_file('prompts.md')}, 
            *conversation_history
            # {"role": "user", "content": conversation_history}
        ],
    )

    neurify = response.choices[0].message.content
    update_conversation_history("assistant", neurify)


    return neurify


def send_message1(message):
    sentiment_score = analyze_sentiment(message)
    depression_flag = sentiment_score < -0.5
    return depression_flag

# Function to check if the sentiment indicates sadness
def send_message2(message):
    sentiment_score = analyze_sentiment(message)
    sadness_flag = sentiment_score < -0.2
    return sadness_flag


import time
def convert_to_speech(text):
    speech_file_path = "static/output.mp3"
    
    response = client.audio.speech.create(
        model="tts-1",
        voice=avaj,
        input=text
    )


    response.stream_to_file(speech_file_path)


    return f"/output.mp3?{int(time.time())}"

def transcribe_audio(audio_file):
    try:
        audio_data = audio_file.read()

        # Convert the uploaded file to .mp3 format using pydub
        audio = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
        output_io = io.BytesIO()
        audio.export(output_io, format="mp3")
        output_io.seek(0)

        # Create a BytesIO object for transcription
        audio_file = io.BytesIO(output_io.read())
        audio_file.name = "output.mp3"

        # Save the MP3 file locally for testing purposes
        with open("output.mp3", "wb") as f:
            f.write(output_io.getvalue())

        # OpenAI whisper
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
        transcript = transcription.text
 
        transcriptor_prompt = "You are an expert transcriber specializing in Indian accents and languages. Your job is to refine transcriptions provided by the Whisper model, correcting errors that occur due to Indian accents or mixed language usage. Ensure that the final transcription accurately represents the original audio by fixing misheard words, handling code-switching (e.g., English mixed with Hindi or other Indian languages), and making minor punctuation or grammatical corrections as needed. Maintain the natural flow and meaning of the original speech while ensuring clarity and readability, exclude urdu"

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

        return usertranscript

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/save-transcription', methods=['POST'])
def save_transcription():
    file = request.files['file']

    transcription = transcribe_audio(file)

    chat_response = send_message(transcription)

    depressed_detector = send_message1(transcription)
    sad_detector = send_message2(transcription)
    

    audio_url = convert_to_speech(chat_response)
    

    return jsonify({'message': 'Transcription saved successfully', 'chat_response': chat_response, 'audio_url': audio_url, 'depressed_flag': depressed_detector, 'sad_detector': sad_detector})


@app.route('/output.mp3')
def serve_audio():
    return send_from_directory('static', 'output.mp3')


if __name__ == '__main__':
    app.run(debug=True, port=5050)
