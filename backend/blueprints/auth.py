from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from database_connection import college_users_collection, super_admins_collection
import jwt
import datetime
 
auth_bp = Blueprint('auth', __name__)
 
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
 
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
 
    super_admin = super_admins_collection.find_one({"email": email})
    if super_admin and check_password_hash(super_admin['password'], password):
        token = jwt.encode({
            'email': email,
            'role': 'superAdmin',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({
            "token": token,
            "role": "superAdmin",
            "userProfile": {"username": "Super Admin", "email": email}
        })
 
    college_user = college_users_collection.find_one({"email": email})
    if college_user and check_password_hash(college_user['password'], password):
        token = jwt.encode({
            'email': email,
            'role': 'collegeUser',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({
            "token": token,
            "role": "collegeUser",
            "userProfile": {"username": college_user.get('name', ''), "email": email}
        })
 
    return jsonify({"error": "Invalid credentials."}), 401
 
    