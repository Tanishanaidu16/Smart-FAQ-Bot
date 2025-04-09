from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from functools import wraps
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

# Secret key for JWT
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecret')

# MongoDB connection setup
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/chatbot_platform')
client = MongoClient(mongo_uri)
db = client.get_database()
college_users = db.college_users
super_admins = db.super_admins

# Middleware to verify JWT token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format!'}), 401

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user_email = data.get('email')
            user_role = data.get('role')

            if user_role == 'superAdmin':
                current_user = super_admins.find_one({'email': user_email})
            elif user_role == 'collegeUser':
                current_user = college_users.find_one({'email': user_email})
            else:
                return jsonify({'error': 'Invalid token role!'}), 401

            if not current_user:
                return jsonify({'error': 'User not found!'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        except Exception as e:
            return jsonify({'error': 'An error occurred while decoding the token.', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# Default super admin user initialization
def init_super_admin():
    default_email = "admin@platform.com"
    default_password = "admin123"

    existing_admin = super_admins.find_one({"email": default_email})
    if not existing_admin:
        hashed_pw = generate_password_hash(default_password)
        super_admins.insert_one({
            "email": default_email,
            "password": hashed_pw,
            "created_at": datetime.datetime.utcnow()
        })
        print("[Init] Default super admin created.")
    else:
        print("[Init] Super admin already exists.")

# Single Login Endpoint
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    # Check if it's a super admin
    super_admin = super_admins.find_one({"email": email})
    if super_admin and check_password_hash(super_admin['password'], password):
        token = jwt.encode({
            'email': email,
            'role': 'superAdmin',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"token": token, "role": "superAdmin"}), 200

    # Check if it's a college user
    college_user = college_users.find_one({"email": email})
    if college_user and check_password_hash(college_user['password'], password):
        token = jwt.encode({
            'email': email,
            'role': 'collegeUser',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"token": token, "role": "collegeUser"}), 200

    return jsonify({"error": "Invalid credentials."}), 401

# CRUD API: College Users (Accessible only by Super Admins)
# ... (Keep the /api/college-users routes as they are, protected by super_admin_token_required if needed)

# Protected route for college users (example)
@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    if getattr(current_user, '_fields', {}).get('password') is not None and 'created_at' in getattr(current_user, '_fields', {}):
        return jsonify({"message": f"Hello, College User {current_user['name']}! This is your profile."})
    elif getattr(current_user, '_fields', {}).get('password') is not None and 'created_at' in getattr(current_user, '_fields', {}):
        return jsonify({"message": f"Hello, Super Admin {current_user['email']}! This is your profile (admin)."})
    return jsonify({"message": "Hello, User!"})

if __name__ == '__main__':
    with app.app_context():
        init_super_admin()
    app.run(debug=True, port=5000)