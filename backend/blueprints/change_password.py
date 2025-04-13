from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from .middlewares import token_required  # if this is in another file, adjust import
from bson.objectid import ObjectId

change_password_bp = Blueprint('change_password', __name__)

@change_password_bp.route('/profile/change-password', methods=['PUT', 'OPTIONS'])
@token_required
def change_password(current_user):
    data = request.get_json()
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')

    if not current_password or not new_password:
        return jsonify({"message": "Current and new passwords are required"}), 400

    if not check_password_hash(current_user['password'], current_password):
        return jsonify({"message": "Incorrect current password"}), 400

    hashed_new_password = generate_password_hash(new_password)

    db = current_app.mongo_db
    db.college_users.update_one({'email': current_user['email']}, {"$set": {'password': hashed_new_password}})

    return jsonify({"message": "Password updated successfully"})
