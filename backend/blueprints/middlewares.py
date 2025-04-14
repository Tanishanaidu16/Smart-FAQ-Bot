from functools import wraps
from flask import request, jsonify, current_app
from database_connection import college_users_collection, super_admins_collection
import jwt
 
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
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user_email = data.get('email')
            user_role = data.get('role')
 
            current_user = None
            if user_role == 'superAdmin':
                current_user = super_admins_collection.find_one({'email': user_email})
            elif user_role == 'collegeUser':
                current_user = college_users_collection.find_one({'email': user_email})
            if not current_user:
                return jsonify({'error': 'User not found!'}), 401
 
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
 
        return f(current_user, *args, **kwargs)
    return decorated
 
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
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            if data.get('role') != 'superAdmin':
                return jsonify({'error': 'Admin access required!'}), 403
 
            current_user = super_admins_collection.find_one({'email': data['email']})
            if not current_user:
                return jsonify({'error': 'Super admin not found!'}), 401
 
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
 
        return f(*args, **kwargs)
    return decorated
 