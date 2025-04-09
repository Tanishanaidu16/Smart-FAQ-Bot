from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

# Secret key for JWT
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecret')

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['chatbot_platform']
super_admins = db['super_admins']
college_users = db['college_users']

# Default super admin user (on startup)
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

# Super Admin Login
@app.route('/api/super-admin/login', methods=['POST'])
def super_admin_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    admin = super_admins.find_one({"email": email})
    if not admin or not check_password_hash(admin['password'], password):
        return jsonify({"error": "Invalid credentials."}), 401

    token = jwt.encode({
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({"token": token}), 200

# CRUD API: College Users

# Get all college users
@app.route('/api/college-users', methods=['GET'])
def get_college_users():
    users = list(college_users.find())
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify(users)

# Create new college user
@app.route('/api/college-users', methods=['POST'])
def create_college_user():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = generate_password_hash(data.get('password'))

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields."}), 400

    user_id = college_users.insert_one({
        "name": name,
        "email": email,
        "password": password,
        "created_at": datetime.datetime.utcnow()
    }).inserted_id

    return jsonify({"message": "User created.", "id": str(user_id)}), 201

# Update college user
@app.route('/api/college-users/<user_id>', methods=['PUT'])
def update_college_user(user_id):
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    update_data = {}
    if name:
        update_data['name'] = name
    if email:
        update_data['email'] = email
    if password:
        update_data['password'] = generate_password_hash(password)

    college_users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    return jsonify({"message": "User updated."}), 200

# Delete college user
@app.route('/api/college-users/<user_id>', methods=['DELETE'])
def delete_college_user(user_id):
    college_users.delete_one({"_id": ObjectId(user_id)})
    return jsonify({"message": "User deleted."}), 200

if __name__ == '__main__':
    with app.app_context():
        init_super_admin()
    app.run(debug=True, port=5000)
