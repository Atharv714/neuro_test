# NeuroWellness AI

## Abstract 

NeuroWellness AI is an innovative platform designed to provide comprehensive, real-time support for both mental and physical health. It leverages cutting-edge technologies like Whisper for speech recognition, GPT-4 for contextual understanding, and VADER sentiment analysis for emotional evaluation. This combination creates a unique, connected approach to emotional companionship and mental health monitoring.

Powered by a robust architecture that integrates both Flask and FastAPI, NeuroWellness AI ensures fast and seamless communication between users and the platform. Key features include the Neurify Bot, a 24/7 empathetic virtual companion, and the AI Health Diagnosis, both of which offer personalized care. The platform is equipped to not only respond to immediate emotional wellbeing but also provides preventive care, bridging the gap between mental and physical well-being. NeuroWellness AI delivers compassionate, real-time support for those seeking both crisis intervention and ongoing wellness management.

## Tech Stack

- Flask
- Open AI
    - Speech to Text Model
    - Generative model
    - Text to Speech Model

- Vedar Sentimental Analysis
- Web Audio API

## Running the code 

On macOS/Linux
```
pip3 install -r requirements.txt
```

On Windows : 

```
pip install -r requirements.txt
```

Run `main.py` file from the route

> Note : You have to provide your own OpenAI key in "Open_AI_Key" text area

----

## Gender Classificiation using Voice

- Used TensorFlow/Keras to classify audio features extracted using librosa. The model is trained and evaluated on custom audio datasets, include features like MFCC, Chroma, and MEL Spectrogram Frequency.
- 
### Tech Stack
    - Librosa: audio feature extraction (MFCC, MEL spectrogram, Chroma, etc.)
    - TensorFlow/Keras: building, training, and evaluating the machine learning model
    - Pandas, NumPy: For data manipulation and processing
    - TensorBoard: For visualization of model training metrics
 
### Running the model

```
pip install -r requirements.txt
```

### Run the script

```
python3 test.py
```

---

## AI Diagnosis

It aims to ask a series of questions to user, to better help user understand his/her feelings, also generates the reports, using AI, to summarise User's Diagnosis, and also can be given to doctors

### Tech Stack

- Flask
- JavaScript
- Trained GPT API


### Running the program

```
pip install -r requirements.txt
```

```
python3 app.py
```

> You have to manually click on aidiagnosis.html and diagnosis_result, for output


