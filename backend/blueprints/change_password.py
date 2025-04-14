from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from .middlewares import token_required
from database_connection import college_users_collection
 
change_password_bp = Blueprint('change_password', __name__)
 
@change_password_bp.route('/profile/change-password', methods=['PUT', 'OPTIONS'])
def change_password():
    if request.method == 'OPTIONS':
        return '', 200
    return _change_password_handler()
 
@token_required
def _change_password_handler(current_user):
    data = request.get_json()
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
 
    if not current_password or not new_password:
        return jsonify({"message": "Current and new passwords are required"}), 400
 
    if not check_password_hash(current_user['password'], current_password):
        return jsonify({"message": "Incorrect current password"}), 400
 
    hashed_new_password = generate_password_hash(new_password)
    college_users_collection.update_one(
        {'email': current_user['email']},
        {"$set": {'password': hashed_new_password}}
    )
 
    return jsonify({"message": "Password updated successfully"}), 200