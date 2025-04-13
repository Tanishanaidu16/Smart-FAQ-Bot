from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId
from .middlewares import super_admin_token_required
import datetime 

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('', methods=['GET'])
@super_admin_token_required
def get_college_users():
    users = list(current_app.college_users.find())
    for user in users:
        user['_id'] = str(user['_id'])
        user.pop('password', None)
    return jsonify(users)

@admin_bp.route('', methods=['POST'])
@super_admin_token_required
def create_college_user():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([name, email, password]):
        return jsonify({"error": "Missing required fields."}), 400

    if current_app.college_users.find_one({"email": email}):
        return jsonify({"error": "Email already exists."}), 400

    user_id = current_app.college_users.insert_one({
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "created_at": datetime.datetime.utcnow()
    }).inserted_id

    return jsonify({"message": "User created.", "id": str(user_id)}), 201

@admin_bp.route('/<user_id>', methods=['GET'])
@super_admin_token_required
def get_single_user(user_id):
    user = current_app.college_users.find_one({"_id": ObjectId(user_id)})
    if user:
        user['_id'] = str(user['_id'])
        user.pop('password', None)
        return jsonify(user)
    return jsonify({"error": "User not found."}), 404

@admin_bp.route('/<user_id>', methods=['PUT'])
@super_admin_token_required
def update_user(user_id):
    data = request.json
    update_data = {}
    if 'name' in data: update_data['name'] = data['name']
    if 'email' in data:
        if current_app.college_users.find_one({"email": data['email'], "_id": {"$ne": ObjectId(user_id)}}):
            return jsonify({"error": "Email already exists."}), 400
        update_data['email'] = data['email']
    if 'password' in data: update_data['password'] = generate_password_hash(data['password'])

    result = current_app.college_users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    if result.modified_count:
        return jsonify({"message": "User updated."})
    return jsonify({"error": "User not found or no changes made."}), 404

@admin_bp.route('/<user_id>', methods=['DELETE'])
@super_admin_token_required
def delete_user(user_id):
    result = current_app.college_users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count:
        return jsonify({"message": "User deleted."})
    return jsonify({"error": "User not found."}), 404
