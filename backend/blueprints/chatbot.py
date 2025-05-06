from flask import Blueprint, request, jsonify, current_app
from notebook.college_ragv1 import generate_response_from_rag
import traceback

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api/chatbot')

# Validate init_key (UUID)
def is_valid_init_key(key):
    if not key:
        current_app.logger.error("Error: No key provided.")
        return False
    college_users_collection = current_app.college_users
    user = college_users_collection.find_one({"access_key": key})
    if not user:
        current_app.logger.error(f"Error: No user found for key {key}.")
    return user is not None

# Middleware to check init_key
@chatbot_bp.before_request
def check_init_key():
    init_key = request.headers.get("Authorization")
    if not is_valid_init_key(init_key):
        current_app.logger.warning(f"Unauthorized access attempt with key: {init_key}")
        return jsonify({"error": "Unauthorized"}), 401

# Greeting route
@chatbot_bp.route('/greeting', methods=['GET'])
def greeting():
    current_app.logger.info("Greeting route accessed.")
    return jsonify({"bot": "Hello! How are you today? 👋"})

# Chat message route
@chatbot_bp.route('/message', methods=['POST'])
def message():
    try:
        current_app.logger.info("Chat message route hit.")

        data = request.get_json()
        if not data:
            current_app.logger.error("Error: No JSON data received.")
            return jsonify({"reply": "No data received."}), 400

        user_message = data.get("message", "").strip()
        if not user_message:
            current_app.logger.error("Error: Empty message received.")
            return jsonify({"reply": "Please enter a valid message."}), 400

        current_app.logger.info(f"Calling generate_response_from_rag with message: {user_message}")
        response, source = generate_response_from_rag(user_message)
        current_app.logger.info("RAG Response received.")

        if not response.strip() or "Error generating answer" in response:
            return jsonify({"reply": "Sorry, I couldn’t find an answer for that. Try asking something else!"})

        return jsonify({"reply": response, "source": source})

    except Exception as e:
        current_app.logger.error("❌ Exception occurred in /message endpoint:")
        traceback.print_exc()
        return jsonify({"reply": "Oops, something went wrong on our end. Please try again later. ⚠️"}), 500
