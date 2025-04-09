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

            current_user = None
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
            return jsonify({'error': 'An error occurred while decoding the token.', 'details': str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# Middleware to verify if the logged-in user is a super admin
def super_admin_token_required(f):
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
            user_role = data.get('role')
            if user_role != 'superAdmin':
                return jsonify({'error': 'Admin access required!'}), 403
            user_email = data.get('email')
            current_user = super_admins.find_one({'email': user_email})
            if not current_user:
                return jsonify({'error': 'Super admin not found!'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        except Exception as e:
            return jsonify({'error': 'An error occurred while decoding the token.', 'details': str(e)}), 401

        return f(*args, **kwargs)
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
        return jsonify({
            "token": token,
            "role": "superAdmin",
            "userProfile": {"username": "Super Admin", "email": email} # Basic admin profile
        }), 200

    # Check if it's a college user
    college_user = college_users.find_one({"email": email})
    if college_user and check_password_hash(college_user['password'], password):
        token = jwt.encode({
            'email': email,
            'role': 'collegeUser',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({
            "token": token,
            "role": "collegeUser",
            "userProfile": {"username": college_user.get('name', ''), "email": email}
        }), 200

    return jsonify({"error": "Invalid credentials."}), 401

# CRUD API: College Users (Accessible only by Super Admins)
# Get all college users
@app.route('/api/college-users', methods=['GET'])
@super_admin_token_required
def get_college_users():
    users = list(college_users.find())
    for user in users:
        user['_id'] = str(user['_id'])
        user.pop('password', None) # Remove password from the response
    return jsonify(users)

# Create new college user
@app.route('/api/college-users', methods=['POST'])
@super_admin_token_required
def create_college_user():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields."}), 400

    if college_users.find_one({"email": email}):
        return jsonify({"error": "Email already exists."}), 400

    hashed_pw = generate_password_hash(password)
    user_id = college_users.insert_one({
        "name": name,
        "email": email,
        "password": hashed_pw,
        "created_at": datetime.datetime.utcnow()
    }).inserted_id

    return jsonify({"message": "User created.", "id": str(user_id)}), 201

# Get a specific college user
@app.route('/api/college-users/<user_id>', methods=['GET'])
@super_admin_token_required
def get_single_college_user(user_id):
    user = college_users.find_one({"_id": ObjectId(user_id)})
    if user:
        user['_id'] = str(user['_id'])
        user.pop('password', None)
        return jsonify(user), 200
    return jsonify({"error": "User not found."}), 404

# Update college user
@app.route('/api/college-users/<user_id>', methods=['PUT'])
@super_admin_token_required
def update_college_user(user_id):
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    update_data = {}
    if name:
        update_data['name'] = name
    if email:
        if college_users.find_one({"email": email, "_id": {"$ne": ObjectId(user_id)}}):
            return jsonify({"error": "Email already exists."}), 400
        update_data['email'] = email
    if password:
        update_data['password'] = generate_password_hash(password)

    result = college_users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    if result.modified_count > 0:
        return jsonify({"message": "User updated."}), 200
    return jsonify({"error": "User not found or no changes made."}), 404

# Delete college user
@app.route('/api/college-users/<user_id>', methods=['DELETE'])
@super_admin_token_required
def delete_college_user(user_id):
    result = college_users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count > 0:
        return jsonify({"message": "User deleted."}), 200
    return jsonify({"error": "User not found."}), 404

# Protected route for college users (example)
@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    if current_user and 'password' in current_user and 'created_at' in current_user:
        return jsonify({"message": f"Hello, {current_user.get('name', 'User')}! This is your profile.", "email": current_user['email']})
    elif current_user and 'password' in current_user and 'created_at' in current_user: # Redundant condition, kept for original logic
        return jsonify({"message": f"Hello, Super Admin {current_user['email']}! This is your profile."})
    else:
        return jsonify({"error": "Could not retrieve profile information."}), 500

if __name__ == '__main__':
    init_super_admin()
    app.run(debug=True)