from flask import Blueprint, request, jsonify, current_app
from notebook.college_ragv1 import generate_response_from_rag


chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api/chatbot')

# Validate init_key (UUID)
def is_valid_init_key(key):
    if not key:
        return False
    college_users_collection = current_app.college_users
    user = college_users_collection.find_one({"access_key": key})
    return user is not None

# Middleware to check init_key
@chatbot_bp.before_request
def check_init_key():
    init_key = request.headers.get("Authorization")
    if not is_valid_init_key(init_key):
        return jsonify({"error": "Unauthorized"}), 401

# Greeting route
@chatbot_bp.route('/greeting', methods=['GET'])
def greeting():
    return jsonify({ "bot": "Hello! How are you today? 👋" })

# Updated Chat message route using Gemini RAG
@chatbot_bp.route('/message', methods=['POST'])
def message():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({ "reply": "Please enter a valid message." })

        # ✅ Call the function from college_ragv1.py
        response = generate_response_from_rag(user_message)
        print("Calling RAG system with:", user_message)
        if not response.strip() or "Error generating answer" in response:
            return jsonify({ "reply": "Sorry, I couldn’t find an answer for that. Try asking something else!" })

        return jsonify({ "reply": response })

    except Exception as e:
        return jsonify({ "reply": "Oops, something went wrong on our end. Please try again later. ⚠️" }), 500
