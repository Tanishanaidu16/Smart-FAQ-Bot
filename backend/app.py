from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from functools import wraps
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Updated CORS Configuration
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)

# Secret key for JWT
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecret')

# MongoDB connection setup
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/chatbot_platform')
client = MongoClient(mongo_uri)
db = client.get_database()
college_users = db.college_users
super_admins = db.super_admins

# JWT token verification middleware
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

# Middleware to verify if the user is a super admin
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

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

# Initialize default super admin
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

# Login route
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

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
            "userProfile": {"username": "Super Admin", "email": email}
        }), 200

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

# College User CRUD APIs (super admin only)
@app.route('/api/college-users', methods=['GET'])
@super_admin_token_required
def get_college_users():
    users = list(college_users.find())
    for user in users:
        user['_id'] = str(user['_id'])
        user.pop('password', None)
    return jsonify(users)

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

@app.route('/api/college-users/<user_id>', methods=['GET'])
@super_admin_token_required
def get_single_college_user(user_id):
    user = college_users.find_one({"_id": ObjectId(user_id)})
    if user:
        user['_id'] = str(user['_id'])
        user.pop('password', None)
        return jsonify(user), 200
    return jsonify({"error": "User not found."}), 404

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

@app.route('/api/college-users/<user_id>', methods=['DELETE'])
@super_admin_token_required
def delete_college_user(user_id):
    result = college_users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count > 0:
        return jsonify({"message": "User deleted."}), 200
    return jsonify({"error": "User not found."}), 404

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    if current_user and 'password' in current_user and 'created_at' in current_user:
        return jsonify({
            "message": f"Hello, {current_user.get('name', 'User')}! This is your profile.",
            "email": current_user['email']
        })
    else:
        return jsonify({"error": "Could not retrieve profile information."}), 500


#below are the knowlegde managment api............

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

collection = db['pdf_files']

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    file_data = {
        'filename': filename,
        'path': filepath
    }
    result = collection.insert_one(file_data)
    return jsonify({'message': 'PDF uploaded', 'file_id': str(result.inserted_id)})

@app.route('/files', methods=['GET'])
def list_files():
    files = []
    for file_doc in collection.find():
        files.append({
            'id': str(file_doc['_id']),
            'filename': file_doc['filename']
        })
    return jsonify(files)

@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    file_doc = collection.find_one({'_id': ObjectId(file_id)})
    if not file_doc:
        return jsonify({'error': 'File not found'}), 404

    return send_from_directory(app.config['UPLOAD_FOLDER'], file_doc['filename'], as_attachment=True)

@app.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    file_doc = collection.find_one({'_id': ObjectId(file_id)})
    if not file_doc:
        return jsonify({'error': 'File not found'}), 404

    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_doc['filename']))
    except Exception as e:
        print(f"File deletion error: {e}")

    collection.delete_one({'_id': ObjectId(file_id)})
    return jsonify({'message': 'File deleted'})

# Run the app
if __name__ == '__main__':
    init_super_admin()
    app.run(debug=True)
