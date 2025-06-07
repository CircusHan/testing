from flask import Flask, jsonify, request, render_template
import os
import google.generativeai as genai
import json # For parsing Gemini's response

app = Flask(__name__)

# Configure Gemini API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY environment variable not set. Using placeholder.")
    GOOGLE_API_KEY = "YOUR_API_KEY" # Placeholder

# It's important to configure before trying to use the model
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    GEMINI_INITIALIZED = True
except Exception as e:
    print(f"Error initializing Gemini: {e}")
    GEMINI_INITIALIZED = False
    model = None


patients_db = {}  # (name, rrn) -> {'status': 'status_value'}

# --- Backend Functions (unchanged from previous step) ---
def register_patient(name, rrn):
    if (name, rrn) in patients_db:
        return (False, "Patient already registered.")
    patients_db[(name, rrn)] = {'status': 'Registered'}
    return (True, "Patient registered successfully.")

def register_prescription(name, rrn):
    if (name, rrn) not in patients_db:
        return (False, "Patient not found.")
    if patients_db[(name, rrn)]['status'] != 'Registered':
        return (False, "Patient must be registered before prescription.")
    patients_db[(name, rrn)]['status'] = 'Prescripted'
    return (True, "Prescription registered successfully.")

def process_payment(name, rrn):
    if (name, rrn) not in patients_db:
        return (False, "Patient not found.")
    if patients_db[(name, rrn)]['status'] != 'Prescripted':
        return (False, "Prescription must be registered before payment.")
    patients_db[(name, rrn)]['status'] = 'Paid'
    return (True, "Payment processed successfully.")

def print_certificate(name, rrn):
    if (name, rrn) not in patients_db:
        return (False, "Patient not found.")
    if patients_db[(name, rrn)]['status'] != 'Paid':
        return (False, "Payment must be processed before printing certificate.")
    patients_db[(name, rrn)]['status'] = 'Completed'
    return (True, "Certificate generated successfully.")

# --- Flask Routes for backend functions (unchanged) ---
@app.route('/register_patient', methods=['POST'])
def route_register_patient():
    data = request.get_json()
    if not data or 'name' not in data or 'rrn' not in data:
        return jsonify({"success": False, "message": "Missing name or rrn in request."}), 400
    name, rrn = data['name'], data['rrn']
    success, message = register_patient(name, rrn)
    status_code = 201 if success else (409 if "already registered" in message else 400)
    return jsonify({"success": success, "message": message}), status_code

@app.route('/register_prescription', methods=['POST'])
def route_register_prescription():
    data = request.get_json()
    if not data or 'name' not in data or 'rrn' not in data:
        return jsonify({"success": False, "message": "Missing name or rrn in request."}), 400
    name, rrn = data['name'], data['rrn']
    success, message = register_prescription(name, rrn)
    status_code = 200 if success else (404 if "not found" in message else 400)
    return jsonify({"success": success, "message": message}), status_code

@app.route('/process_payment', methods=['POST'])
def route_process_payment():
    data = request.get_json()
    if not data or 'name' not in data or 'rrn' not in data:
        return jsonify({"success": False, "message": "Missing name or rrn in request."}), 400
    name, rrn = data['name'], data['rrn']
    success, message = process_payment(name, rrn)
    status_code = 200 if success else (404 if "not found" in message else 400)
    return jsonify({"success": success, "message": message}), status_code

@app.route('/print_certificate', methods=['POST'])
def route_print_certificate():
    data = request.get_json()
    if not data or 'name' not in data or 'rrn' not in data:
        return jsonify({"success": False, "message": "Missing name or rrn in request."}), 400
    name, rrn = data['name'], data['rrn']
    success, message = print_certificate(name, rrn)
    status_code = 200 if success else (404 if "not found" in message else 400)
    return jsonify({"success": success, "message": message}), status_code

# --- Chatbot Route ---
@app.route('/chat', methods=['POST'])
def chat():
    if not GEMINI_INITIALIZED:
        return jsonify({"reply": "Chatbot is not available due to initialization error."}), 503

    data = request.get_json()
    user_message = data.get('message')
    name = data.get('name')
    rrn = data.get('rrn')

    if not user_message:
        return jsonify({"reply": "No message provided."}), 400

    # Construct prompt for Gemini
    # We are simplifying here: client should send name/rrn if action is intended.
    # Gemini's main role is intent classification.
    prompt = f"""
    You are a helpful assistant for a medical clinic.
    Your task is to understand the user's message and classify it into one of the following actions:
    'register_patient', 'register_prescription', 'process_payment', 'print_certificate', or 'general_conversation'.

    Return your answer as a JSON object with a single key 'action'.
    For example: {{"action": "register_patient"}} or {{"action": "general_conversation"}}.

    User's message: "{user_message}"
    """

    try:
        gemini_response = model.generate_content(prompt)

        # Debug: Print raw Gemini response text
        print(f"Gemini raw response: {gemini_response.text}")

        # Attempt to parse the JSON from Gemini's response
        # Gemini might return the JSON within backticks or with other text.
        cleaned_response_text = gemini_response.text.strip().replace("```json", "").replace("```", "").strip()

        # Handle cases where Gemini might not return valid JSON or returns an empty response
        if not cleaned_response_text:
            action_data = {"action": "general_conversation", "detail": "Could not understand the request clearly."}
        else:
            try:
                action_data = json.loads(cleaned_response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as general conversation or try to find action keyword
                print(f"JSONDecodeError parsing: {cleaned_response_text}")
                if "register_patient" in cleaned_response_text.lower():
                    action_data = {"action": "register_patient"}
                elif "register_prescription" in cleaned_response_text.lower():
                    action_data = {"action": "register_prescription"}
                elif "process_payment" in cleaned_response_text.lower():
                    action_data = {"action": "process_payment"}
                elif "print_certificate" in cleaned_response_text.lower():
                    action_data = {"action": "print_certificate"}
                else:
                    action_data = {"action": "general_conversation", "detail": gemini_response.text}


        action = action_data.get('action')

        # --- Action Handling ---
        if action == 'register_patient':
            if not name or not rrn:
                return jsonify({"reply": "Please provide name and RRN for patient registration."}), 400
            success, message = register_patient(name, rrn)
            return jsonify({"reply": message, "success": success, "action_performed": action})

        elif action == 'register_prescription':
            if not name or not rrn:
                return jsonify({"reply": "Please provide name and RRN for prescription."}), 400
            success, message = register_prescription(name, rrn)
            return jsonify({"reply": message, "success": success, "action_performed": action})

        elif action == 'process_payment':
            if not name or not rrn:
                return jsonify({"reply": "Please provide name and RRN for payment processing."}), 400
            success, message = process_payment(name, rrn)
            return jsonify({"reply": message, "success": success, "action_performed": action})

        elif action == 'print_certificate':
            if not name or not rrn:
                return jsonify({"reply": "Please provide name and RRN for certificate printing."}), 400
            success, message = print_certificate(name, rrn)
            return jsonify({"reply": message, "success": success, "action_performed": action})

        elif action == 'general_conversation':
            # If Gemini provided a detailed answer within the parsed action_data (e.g. from a failed JSON parse)
            if action_data.get("detail"):
                 return jsonify({"reply": action_data.get("detail"), "action_performed": "general_conversation"})
            # Fallback general response
            return jsonify({"reply": "I can help with patient registration, prescription, payment, and certificates. How can I assist you today?", "action_performed": "general_conversation"})

        else: # Unknown action
            print(f"Unknown action from Gemini: {action}")
            return jsonify({"reply": f"Sorry, I understood the action as '{action}' but I don't know how to handle that. Please try rephrasing.", "action_performed": "unknown"}), 500

    except Exception as e:
        print(f"Error during Gemini API call or processing: {e}")
        # Check if the error is due to the API key being the placeholder
        if GOOGLE_API_KEY == "YOUR_API_KEY":
            return jsonify({"reply": "Chatbot is not available. The API key is a placeholder."}), 503
        return jsonify({"reply": "Sorry, I encountered an error processing your request."}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
