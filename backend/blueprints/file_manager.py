import os
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from .middlewares import token_required
from database_connection import pdf_files_collection
 
file_bp = Blueprint('file', __name__)
 
@file_bp.route('/upload', methods=['POST'])
@token_required
def upload(current_user):
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files allowed'}), 400
 
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)
    pdf_files_collection.insert_one({
        'filename': file.filename,
        'path': path,
        'email': current_user['email']
    })
    return jsonify({'message': 'Uploaded successfully'}), 200
 
@file_bp.route('/files', methods=['GET'])
@token_required
def list_files(current_user):
    files = pdf_files_collection.find({'email': current_user['email']})
    return jsonify([{'id': str(f['_id']), 'filename': f['filename']} for f in files])
 
@file_bp.route('/delete/<file_id>', methods=['DELETE'])
@token_required
def delete_file(current_user, file_id):
    record = pdf_files_collection.find_one({'_id': ObjectId(file_id), 'email': current_user['email']})
    if not record:
        return jsonify({'error': 'Unauthorized or not found'}), 404
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], record['filename']))
    except:
        pass
    pdf_files_collection.delete_one({'_id': ObjectId(file_id)})
    return jsonify({'message': 'File deleted'})