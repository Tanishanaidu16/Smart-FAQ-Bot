from flask import Blueprint, request, jsonify, current_app

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

# Chat message route
@chatbot_bp.route('/message', methods=['POST'])
def message():
    import random, time
    data = request.get_json()
    user_message = data.get("message", "")
    time.sleep(1.5)
    reply = random.choice([
        "I'm just a friendly bot, how can I assist? 😊",
        "That’s interesting! Tell me more.",
        "I'm still learning, but I’ll try my best!",
        "Hmm... I don't know how to respond to that. 🤖",
        "Let's try a different question. 🙃",
        "Oops! I didn’t get that. 😅"
    ])
    return jsonify({ "reply": reply })
