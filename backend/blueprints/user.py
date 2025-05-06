from flask import Blueprint, jsonify, request,make_response
from .middlewares import token_required
from database_connection import college_users_collection, super_admins_collection  # Importing collections
import uuid
import io
user_bp = Blueprint('user', __name__)
 
@user_bp.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    # Check if the user is a super admin
    is_super_admin = super_admins_collection.find_one({"email": current_user['email']}) is not None
   
    if is_super_admin:
        # Return only username and email for super admin
        return jsonify({
            "username": current_user.get('name', 'User'),
            "email": current_user['email']
        })
    else:
        # Handle college user profile display
        user_record = college_users_collection.find_one({"email": current_user['email']})
 
        if not user_record:
            return jsonify({"message": "User not found"}), 404
 
        access_key = user_record.get("access_key")
        college_name = user_record.get("college_name", "")
 
        return jsonify({
            "username": current_user.get('name', 'User'),
            "email": current_user['email'],
            "access_key": access_key,
            "college_name": college_name
        })
       
@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
 
    if not data.get('username') or not data.get('email'):
        return jsonify({"message": "Username and email are required"}), 400
 
    update_fields = {
        "username": data['username'],
        "email": data['email']
    }
 
    if data.get('college_name'):
        update_fields['college_name'] = data['college_name']
 
    college_users_collection.update_one(
        {"email": current_user['email']},
        {"$set": update_fields},
        upsert=True
    )
 
    return jsonify({
        "message": "Profile updated successfully!",
        "username": data['username'],
        "email": data['email'],
        "college_name": data.get('college_name', '')
    })
 
@user_bp.route('/generate-access-key', methods=['POST'])
@token_required
def generate_access_key(current_user):
    user_record = college_users_collection.find_one({"email": current_user['email']})
    if user_record and user_record.get("access_key"):
        return jsonify({"message": "Access key already exists", "access_key": user_record["access_key"]}), 400
 
    new_key = str(uuid.uuid4())
    college_users_collection.update_one(
        {"email": current_user['email']},
        {"$set": {"access_key": new_key}},
        upsert=True
    )
 
    return jsonify({"message": "Access key generated successfully", "access_key": new_key})
 
 

@user_bp.route('/download-config', methods=['GET'])
@token_required
def download_config(current_user):
    """
    Returns only the access key to the frontend.
    """
    user_record = college_users_collection.find_one({"email": current_user['email']})
    
    if not user_record or not user_record.get("access_key"):
        return jsonify({"message": "Access key not found for this user"}), 404
    
    access_key = user_record["access_key"]
    
    return jsonify({"access_key": access_key})