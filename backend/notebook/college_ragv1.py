import os
from pathlib import Path
from typing import Dict, Any
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from pymongo import MongoClient
from langchain.tools import tool

# -- Gemini API Key Configuration --
os.environ["GOOGLE_API_KEY"] = "AIzaSyAv2vEdJGNZadv86nHRJWfjD2Yt_JX_pmM"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# -- System Instruction --
SYSTEM_INSTRUCTION = (
    "You are a helpful college assistant. Only answer using the content from the provided "
    "college PDFs and website pages. If the answer is not available in the documents, "
    "clearly say that you don't have the information instead of guessing or making up answers."
    "Provide output in html format you can use only p,ul,li tags"
)

BASE_DIR = Path(os.getcwd()).resolve()

# -- MongoDB Connection --
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["chatbot_platform"]
KM_documents_collection = db["KM_documents"]
KM_URLs_collection = db["KM_URLs"]

# -- Load PDFs Tool --
@tool
def load_pdfs_from_mongo() -> Dict[str, Any]:
    """Load PDFs from MongoDB and upload them to Gemini."""
    pdfs = {}
    for doc in KM_documents_collection.find():
        try:
            # Handle absolute or relative paths gracefully
            raw_path = Path(doc['path'])
            file_path = raw_path if raw_path.is_absolute() else (BASE_DIR / raw_path)

            if not file_path.exists():
                print(f"[ERROR] File not found: {file_path}")
                continue

            file = genai.upload_file(file_path, mime_type="application/pdf")
            pdfs[doc['filename']] = {
                "file": file,
                "description": doc.get("description", "")
            }
        except Exception as e:
            print(f"[ERROR] Failed to load PDF {doc['filename']}: {e}")
    return pdfs

# -- Load Websites Tool --
@tool
def load_websites_from_mongo() -> Dict[str, Any]:
    """Load and process websites from MongoDB and upload text to Gemini."""
    webpages = {}
    for doc in KM_URLs_collection.find():
        try:
            response = requests.get(doc['url'], timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            text = " ".join(p.get_text() for p in soup.find_all("p")).strip()
            if not text:
                print(f"[WARN] No text content extracted from: {doc['url']}")
                continue
            buffer = BytesIO(text.encode("utf-8"))
            file = genai.upload_file(buffer, mime_type="text/plain")
            webpages[doc['url']] = {
                "file": file,
                "description": doc.get("description", ""),
                "text": text
            }
        except Exception as e:
            print(f"[ERROR] Could not load website {doc['url']}: {e}")
    return webpages

# -- Query PDFs --
@tool
def query_pdfs(query: str, loaded_pdfs: Dict[str, Any]) -> str:
    """Answer using Gemini over loaded PDF files."""
    if not loaded_pdfs:
        return "No PDF documents loaded."

    files = [data["file"] for data in loaded_pdfs.values()]
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )
    response = model.generate_content([*files, query])
    return response.text.strip()

# -- Query Websites --
@tool
def query_websites(query: str, loaded_websites: Dict[str, Any]) -> str:
    """Answer using Gemini over loaded websites."""
    if not loaded_websites:
        return "No website content loaded."

    files = [data["file"] for data in loaded_websites.values() if data.get("file")]
    if not files:
        return "No website content could be processed."

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )
    response = model.generate_content([*files, query])
    return response.text.strip()

# -- Classify Data Source --
@tool
def classify_data_source(query: str) -> str:
    """Decide if the question should be answered using PDFs or Websites."""
    keywords_pdf = ["syllabus", "notes", "pdf", "lecture", "module", "exam", "marks", "subject"]
    keywords_web = ["admission", "fee", "placements", "faculty", "website", "about", "college"]
    query_lower = query.lower()
    if any(k in query_lower for k in keywords_pdf):
        return "pdf"
    elif any(k in query_lower for k in keywords_web):
        return "web"
    return "pdf"

# -- Load sources once at module level --
loaded_pdfs = load_pdfs_from_mongo.invoke({})
loaded_websites = load_websites_from_mongo.invoke({})

# -- API Entry Function for Flask --
def generate_response_from_rag(query: str) -> str:
    try:
        source = classify_data_source.invoke(query)
        if source == "pdf":
            return query_pdfs.invoke({"query": query, "loaded_pdfs": loaded_pdfs})
        else:
            return query_websites.invoke({"query": query, "loaded_websites": loaded_websites})
    except Exception as e:
        print(f"[ERROR] generate_response_from_rag failed: {e}")
        return "Error generating answer. Please try again."





#things to try 
#Tell me about Sahyadri College of Engineering in Mangalore.
#What is the admission process at Sahyadri College?
#What is the highest salary package offered at Sahyadri College?
#What is the fee structure of Sahyadri College of Engineering?

#provide me sample questions from artifical intelligence 
#Provide important 12-mark questions from previous semester exams
#Give me sample questions from the Artificial Intelligence subject
#Give me all questions related to "Agents" across the pdfs
#List the repeated questions from object oriented programming
#Summarize the key topics covered in the last three OOP question papers.
#Give me the question distribution by marks for oops pdf
#