from flask import Blueprint, request, jsonify
import os
import requests
from bs4 import BeautifulSoup # type: ignore
import google.generativeai as genai # type: ignore
from sentence_transformers import SentenceTransformer # type: ignore
import faiss # type: ignore
import numpy as np
import re
from pypdf import PdfReader # type: ignore
 
# Initialize Blueprint
rag_bp = Blueprint("rag_bp", __name__)
 
# Configure Gemini API
genai.configure(api_key="AIzaSyCZ8CPoUeuQBp9rbahqfiMES2X37JHc7Fg")  # Replace with env variable in prod
model = genai.GenerativeModel("gemini-1.5-flash")
 
# Util: Scrape Website
def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all(['p', 'div', 'span', 'article'])
        return ' '.join([el.get_text(strip=True) for el in elements])
    except Exception as e:
        print(f"[Error] Website scrape failed: {e}")
        return ""
 
# Util: Load PDF
def load_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        print(f"[Error] PDF read failed: {e}")
        return ""
 
# Util: Split Text into Chunks
def split_text(text, chunk_size=500):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) + (1 if current else 0) <= chunk_size:
            current += (" " + sentence if current else sentence)
        else:
            if current:
                chunks.append(current.strip())
            current = sentence
    if current:
        chunks.append(current.strip())
    return [chunk for chunk in chunks if chunk]
 
# Embedding
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
def generate_vector(text):
    return embedding_model.encode([text])[0].astype('float32')
 
# Build FAISS index
def create_index(chunks):
    vectors = [generate_vector(chunk) for chunk in chunks]
    if not vectors:
        return None, []
    index = faiss.IndexFlatL2(len(vectors[0]))
    index.add(np.array(vectors))
    return index, chunks
 
# Query index
def query_index(index, query, top_k=5):
    query_vec = generate_vector(query)
    distances, indices = index.search(np.array([query_vec]), top_k)
    return indices[0]
 
# Gemini Response
def query_gemini_rag(query, context):
    prompt = f"Answer the question based on the provided context:\n\nContext:\n{context}\n\nQuestion: {query}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating answer: {e}"
 
# ✅ API Endpoint
@rag_bp.route('/chat', methods=['POST'])
def rag_chat_endpoint():
    try:
        data = request.get_json()
 
        prompt = data.get("prompt")
        website_urls = data.get("website_urls", [])
        pdf_paths = data.get("pdf_paths", [])
 
        if not prompt:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
 
        # Collect and chunk all content
        all_chunks = []
 
        for url in website_urls:
            if url:
                print(f"Scraping {url}")
                text = scrape_website(url)
                all_chunks.extend(split_text(text))
 
        for path in pdf_paths:
            if os.path.exists(path):
                print(f"Reading {path}")
                text = load_pdf(path)
                all_chunks.extend(split_text(text))
            else:
                print(f"[Warning] PDF not found: {path}")
 
        if not all_chunks:
            return jsonify({"error": "No valid content found from provided sources"}), 400
 
        index, chunk_data = create_index(all_chunks)
        top_indices = query_index(index, prompt)
        top_chunks = [chunk_data[i] for i in top_indices]
        context = "\n".join(top_chunks)
 
        # Get Gemini response
        answer = query_gemini_rag(prompt, context)
 
        return jsonify({
            "response": answer,
            "top_chunks_used": top_chunks  # Optional: useful for debug
        })
 
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500