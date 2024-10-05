from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import re
from openai import OpenAI
from pydub import AudioSegment
import io
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv