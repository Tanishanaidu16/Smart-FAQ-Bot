from flask import Blueprint, jsonify, request, current_app
from .middlewares import token_required

user_bp = Blueprint('user', __name__)

# Endpoint to retrieve the profile (GET)
@user_bp.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    return jsonify({
        "message": f"Hello, {current_user.get('name', 'User')}!",
        "email": current_user['email']
    })

# Endpoint to update the profile (PUT)
@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    # Get data from request
    data = request.get_json()

    # Validate the input data
    if not data.get('username') or not data.get('email'):
        return jsonify({"message": "Username and email are required"}), 400

    # Access the database using current_app to get the database connection
    college_users_collection = current_app.mongo_db.college_users

    # Update user profile in the database
    user = college_users_collection.find_one({"email": current_user['email']})
    if not user:
        return jsonify({"message": "User not found"}), 404

    updated_user = {
        "username": data['username'],
        "email": data['email']
    }

    college_users_collection.update_one(
        {"email": current_user['email']},
        {"$set": updated_user}
    )

    # Return success response
    return jsonify({
        "message": "Profile updated successfully!",
        "username": updated_user['username'],
        "email": updated_user['email']
    })
