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

app = Flask(_name_)
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