import os
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from .middlewares import token_required
from database_connection import KM_documents_collection, KM_URLs_collection
 
file_bp = Blueprint('file', __name__)
 
# Upload PDF file with description
@file_bp.route('/upload-pdf', methods=['POST'])
@token_required
def upload_pdf(current_user):
    file = request.files.get('file')
    description = request.form.get('description', '')
 
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files allowed'}), 400
 
    filename = file.filename
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
 
    KM_documents_collection.insert_one({
        'filename': filename,
        'path': path,
        'description': description,
        'email': current_user['email']
    })
    return jsonify({'message': 'PDF uploaded successfully'}), 200
 
# List uploaded PDF files
@file_bp.route('/pdfs', methods=['GET'])
@token_required
def list_pdfs(current_user):
    files = KM_documents_collection.find({'email': current_user['email']})
    return jsonify([{'id': str(f['_id']), 'filename': f['filename'], 'description': f.get('description', '')} for f in files])
 
# Delete a PDF
@file_bp.route('/delete-pdf/<file_id>', methods=['DELETE'])
@token_required
def delete_pdf(current_user, file_id):
    record = KM_documents_collection.find_one({'_id': ObjectId(file_id), 'email': current_user['email']})
    if not record:
        return jsonify({'error': 'Unauthorized or not found'}), 404
 
    try:
        os.remove(record['path'])
    except:
        pass
    KM_documents_collection.delete_one({'_id': ObjectId(file_id)})
    return jsonify({'message': 'PDF deleted successfully'})
 
# Add a website URL with description
@file_bp.route('/add-url', methods=['POST'])
@token_required
def add_url(current_user):
    data = request.get_json()
    url = data.get('url')
    description = data.get('description', '')
 
    if not url:
        return jsonify({'error': 'URL is required'}), 400
 
    KM_URLs_collection.insert_one({
        'url': url,
        'description': description,
        'email': current_user['email']
    })
    return jsonify({'message': 'URL added successfully'}), 200
 
# List all URLs
@file_bp.route('/urls', methods=['GET'])
@token_required
def list_urls(current_user):
    urls = KM_URLs_collection.find({'email': current_user['email']})
    return jsonify([{'id': str(u['_id']), 'url': u['url'], 'description': u.get('description', '')} for u in urls])
 
# Delete a URL
@file_bp.route('/delete-url/<url_id>', methods=['DELETE'])
@token_required
def delete_url(current_user, url_id):
    result = KM_URLs_collection.delete_one({'_id': ObjectId(url_id), 'email': current_user['email']})
    if result.deleted_count == 0:
        return jsonify({'error': 'URL not found or unauthorized'}), 404
    return jsonify({'message': 'URL deleted successfully'})