import os
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
from google.generativeai import GenerativeModel
import google.generativeai as genai

# Set your Gemini API Key
genai.configure(api_key="AIzaSyAv2vEdJGNZadv86nHRJWfjD2Yt_JX_pmM")
model = SentenceTransformer("all-MiniLM-L6-v2")
gemini = GenerativeModel("gemini-1.5-flash")

# --- Existing Functions ---

def scrape_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except Exception as e:
        return ""

def load_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return ""

def split_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def create_index(chunks):
    embeddings = model.encode(chunks)
    return embeddings, chunks

def query_index(embeddings, query, top_k=3):
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return top_indices

def query_gemini_rag(query, context):
    try:
        prompt = f"""
        Based on the following content, answer the user's question in a helpful and clear way:

        --- Content Start ---
        {context}
        --- Content End ---

        User's Question: {query}
        """

        response = gemini.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "Error generating answer"

# --- ✅ NEW FUNCTION TO BE USED BY chatbot.py ---

def generate_response_from_rag(user_query: str) -> str:
    try:
        # 🔒 Hardcoded sources
        website_urls = ["https://www.sahyadri.edu.in/"]
        pdf_paths = [
            r"C:\Users\sameer.kavale\Downloads\Files\Artificial Intelligence 1.pdf",
            r"C:\Users\sameer.kavale\Downloads\Files\Big Data Analytics 1.pdf"
        ]

        all_chunks = []

        for url in website_urls:
            text = scrape_website(url)
            all_chunks.extend(split_text(text))

        for path in pdf_paths:
            if os.path.exists(path):
                text = load_pdf(path)
                all_chunks.extend(split_text(text))

        if not all_chunks:
            return "Sorry, I couldn’t find any useful content to answer that. 📄❌"

        index, chunk_data = create_index(all_chunks)
        top_indices = query_index(index, user_query)
        top_chunks = [chunk_data[i] for i in top_indices]
        context = "\n".join(top_chunks)

        return query_gemini_rag(user_query, context)

    except Exception:
        return "Error generating answer"
