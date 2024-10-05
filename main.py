from flask import Flask, render_template, request, jsonify, send_from_directory
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

avaj = 'echo'