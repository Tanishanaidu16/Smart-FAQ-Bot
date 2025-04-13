from flask import Blueprint, jsonify
from .middlewares import token_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    return jsonify({
        "message": f"Hello, {current_user.get('name', 'User')}!",
        "email": current_user['email']
    })
