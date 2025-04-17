from flask import Flask
from flask_cors import CORS
import os
import datetime
from werkzeug.security import generate_password_hash
from database_connection import db, college_users_collection, super_admins_collection
from notebook.college_ragv1 import rag_bp  # Import the RAG blueprint
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.user import user_bp
from blueprints.file_manager import file_bp
from blueprints.change_password import change_password_bp
 
# Initialize Flask app
app = Flask(__name__)
 
# CORS setup
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)
 
# App configs
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecret')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
 
# MongoDB collections
app.mongo_db = db
app.college_users = college_users_collection
app.super_admins = super_admins_collection
 
# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/college-users')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(file_bp, url_prefix='/api')
app.register_blueprint(change_password_bp, url_prefix='/api')
app.register_blueprint(rag_bp, url_prefix='/api')  # Register the RAG blueprint
 
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response
 
# Initialize default super admin if not exists
def init_super_admin():
    default_email = "admin@platform.com"
    default_password = "admin123"
 
    if not super_admins_collection.find_one({"email": default_email}):
        hashed_pw = generate_password_hash(default_password)
        super_admins_collection.insert_one({
            "email": default_email,
            "password": hashed_pw,
            "created_at": datetime.datetime.utcnow()
        })
        print("[Init] Default super admin created.")
    else:
        print("[Init] Super admin already exists.")
 
# Run the app
if __name__ == '__main__':
    init_super_admin()
    app.run(debug=True)