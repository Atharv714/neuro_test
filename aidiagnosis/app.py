from flask import Flask, request, jsonify
import time
from openai import OpenAI
import os
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()



app = Flask(__name__)
CORS(app) 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Local dictionary to simulate user data
conversations = {}
diagnosis_data_store = {}  # This will store diagnosis data in memory

# Helper function to open files
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

# Helper function to communicate with OpenAI's API
def chatbot(conversation, model="gpt-4o-mini", temperature=0, max_tokens=2000):
    try:
        response = client.chat.completions.create(
            model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens
        )
        text = response.choices[0].message.content
        return text, response.usage.total_tokens
    except Exception as oops:
        print(f'Error communicating with OpenAI: "{oops}"')
        return None, 0

# AI Diagnosis Route
@app.route('/aidiagnosis', methods=['POST'])
def ai_diagnosis():
    user_id = request.json.get('user_id')
    user_message = request.json.get('message')

    # Initialize conversation if it doesn't exist for the user
    if user_id not in conversations:
        conversations[user_id] = [{'role': 'system', 'content': open_file('aidiagnosis/medical_notes/system_01_intake.md')}]

    # Check if the user wants to end the chat
    if user_message.lower() == 'done':
        conversation = conversations[user_id]
        conversation.append({'role': 'system', 'content': open_file('aidiagnosis/medical_notes/system_02_prepare_notes.md')})
        chat_log = '<<BEGIN PATIENT INTAKE CHAT>>\n' + '\n'.join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation if msg['role'] == 'user']) + '\n<<END PATIENT INTAKE CHAT>>'
        conversation.append({'role': 'user', 'content': chat_log})
        notes, _ = chatbot(conversation)

        # Generating reports (Hypothesis, Clinical Evaluation, Referrals)
        conversation.append({'role': 'system', 'content': open_file('aidiagnosis/medical_notes/system_03_diagnosis.md')})
        conversation.append({'role': 'user', 'content': notes})
        report, _ = chatbot(conversation)

        conversation.append({'role': 'system', 'content': open_file('aidiagnosis/medical_notes/system_04_clinical.md')})
        clinical, _ = chatbot(conversation)

        conversation.append({'role': 'system', 'content': open_file('aidiagnosis/medical_notes/system_05_referrals.md')})
        referrals, _ = chatbot(conversation)

        # Store the diagnosis data locally
        diagnosis_data = {
            "chat_log": chat_log,
            "notes": notes,
            "report": report,
            "clinical": clinical,
            "referrals": referrals,
            "timestamp": time.time()
        }
        diagnosis_data_store[user_id] = diagnosis_data

        del conversations[user_id]
        return jsonify({"message": "Diagnosis completed", "data": diagnosis_data}), 200

    # If user has not typed 'done', continue the chat
    conversations[user_id].append({'role': 'user', 'content': user_message})
    response, _ = chatbot(conversations[user_id])
    conversations[user_id].append({'role': 'assistant', 'content': response})

    return jsonify({"message": response}), 200

# Endpoint to fetch diagnosis result
@app.route('/get_diagnosis_result', methods=['GET'])
def get_diagnosis_result():
    user_id = request.args.get('user_id')
    diagnosis = diagnosis_data_store.get(user_id)

    if not diagnosis:
        return jsonify({"error": "No diagnosis found"}), 404
    
    diagnosis.pop('chat_log', None)
    return jsonify(diagnosis), 200

if __name__ == "__main__":
    app.run(debug=True)
