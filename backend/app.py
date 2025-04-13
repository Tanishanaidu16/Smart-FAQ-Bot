from flask import Flask
from flask_cors import CORS
import os
import datetime
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

# Initialize Flask app
app = Flask(__name__)

# CORS setup
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)

# App configs
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecret')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MongoDB setup
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/chatbot_platform')
client = MongoClient(mongo_uri)
db = client.get_database()

# Attach collections to app
app.mongo_db = db
app.college_users = db.college_users
app.super_admins = db.super_admins

# =========================
# Register Blueprints
# =========================
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.user import user_bp
from blueprints.file_manager import file_bp
from blueprints.change_password import change_password_bp  # 👈 NEW IMPORT

# Register with appropriate prefixes
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/college-users')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(file_bp, url_prefix='/api')
app.register_blueprint(change_password_bp, url_prefix='/api')  # 👈 REGISTER NEW BLUEPRINT

# =========================
# CORS Headers for all responses
# =========================
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

# =========================
# Default Super Admin Creator
# =========================
def init_super_admin():
    default_email = "admin@platform.com"
    default_password = "admin123"

    if not app.super_admins.find_one({"email": default_email}):
        hashed_pw = generate_password_hash(default_password)
        app.super_admins.insert_one({
            "email": default_email,
            "password": hashed_pw,
            "created_at": datetime.datetime.utcnow()
        })
        print("[Init] Default super admin created.")
    else:
        print("[Init] Super admin already exists.")

# =========================
# Start App
# =========================
if __name__ == '__main__':
    init_super_admin()
    app.run(debug=True)
