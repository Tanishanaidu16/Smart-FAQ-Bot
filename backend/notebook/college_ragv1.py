import os
from pathlib import Path
from typing import Dict, Any
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from pymongo import MongoClient
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Tuple
from dotenv import load_dotenv
# -- API Key and Config --
# Load API key from .env
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Check if the key is loaded (optional debug)
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in .env file")

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)
 
SYSTEM_INSTRUCTION = """
You are a helpful assistant that provides academic and institutional information for college students.
 
Your task is to assist the user by providing accurate information related to their academic needs. These could include subject-related materials, exam notes, previous semester question papers, or other study-related content.
 
Before answering any query, follow these steps:
1. **Data Loading**:
   - If the query relates to **academic materials** such as **subjects**, **notes**, **exams**, or **previous papers**, load the relevant PDFs first using `load_pdfs_data()`.
   - If the query pertains to **college-related information** like **admission**, **fees**, **placements**, or **campus details**, load the college website data first using `load_websites_data()`.
 
2. **Querying Data**:
   - After loading the data, use the **`query_pdfs()`** function to search through the PDFs if the query is related to academic materials.
   - If the query is related to college information, use **`query_websites()`** to retrieve the information from the websites.
 
3. **Provide the Answer**:
   - Once the data is retrieved, generate the answer based on the content found in the loaded PDFs or websites.
 
4.  Output format:
   - Return final answer in HTML using <p>, <ul>, <li> tags only.
   - If no info found, return: <p>I do not have the information in the documents.</p>
 
Examples of possible queries include:
- "Give me sample questions from Artificial Intelligence."
- "Provide important 12-mark questions from the last semester's exam."
- "Give me notes on Object-Oriented Programming."
- "What is the syllabus for Data Structures?"
- "Tell me about the fee structure for ABC College."
- "What is the highest salary package offered in the last placement drive?"
 
You must ensure that the user’s query is handled accurately by:
1. Loading the relevant PDFs or websites.
2. Querying them to find the exact academic or college-related information.
3. Returning a precise and informative response.
 
If the necessary data is not available, inform the user politely that the data is missing or unavailable, and ask for the required PDFs or website links to proceed.
 
Do not use internal knowledge or assumptions to answer the queries.
"""

 


BASE_DIR = Path(os.getcwd()).resolve()
 
# Load .env file
load_dotenv()

# Get Mongo URI from environment
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB Atlas
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_default_database()
KM_documents_collection = db["KM_documents"]
KM_URLs_collection = db["KM_URLs"]
 
CONTEXT = {
    "loaded_pdfs": None,
    "loaded_websites": None
}
 
from concurrent.futures import ThreadPoolExecutor
import traceback
import fitz  # PyMuPDF
def extract_text_to_buffer(pdf_path: Path) -> BytesIO:
    """Extracts clean text from PDF and returns it as a BytesIO buffer."""
    try:
        doc = fitz.open(pdf_path)
        full_text = "\n".join([page.get_text() for page in doc])
        doc.close()

        if not full_text.strip():
            print(f"No text extracted from {pdf_path}")
            return None

        return BytesIO(full_text.encode("utf-8"))

    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

@tool
def load_pdfs_data() -> str:
    """Force-load PDFs from MongoDB and re-upload extracted text to Gemini (no caching)."""
    print("[TOOL CALL] load_pdfs_from_mongo (no caching)")

    def upload_doc(doc):
        try:
            path = Path(doc['path'])
            file_path = path if path.is_absolute() else (BASE_DIR / path)
            if not file_path.exists():
                print(f"File not found: {file_path}")
                return None

            # Always extract and upload fresh text buffer
            buffer = extract_text_to_buffer(file_path)
            if buffer is None:
                return None

            print(f"[UPLOAD] Uploading fresh extracted text from {doc['filename']}")
            file = genai.upload_file(buffer, mime_type="text/plain")

            # Optionally clear existing gemini_file_id in DB (to avoid confusion)
            KM_documents_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "gemini_file_id": file.name,  # Update with new one
                    # "cached_text": None  # Optional: remove any cached text if you had it
                }}
            )

            return (doc['filename'], {
                "file": file,
                "description": doc.get("description", "")
            })

        except Exception as e:
            print(f"[ERROR] Uploading {doc.get('filename')}: {e}")
            traceback.print_exc()
            return None

    docs = list(KM_documents_collection.find())
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(upload_doc, docs))

    CONTEXT["loaded_pdfs"] = {
        filename: data for filename, data in results if data
    }
    return f"{len(CONTEXT['loaded_pdfs'])} PDF(s) loaded (no cache used)."



@tool
def load_websites_data() -> str:
    """Load websites from MongoDB and upload to Gemini. Always downloads fresh content, no caching used."""
    print("[TOOL CALL] load_websites_from_mongo")

    def upload_site(doc):
        try:
            print(f"Downloading and uploading website: {doc['url']}")
            r = requests.get(doc['url'], timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            text = " ".join(p.get_text() for p in soup.find_all("p"))

            if not text.strip():
                return None

            buffer = BytesIO(text.encode("utf-8"))
            file = genai.upload_file(buffer, mime_type="text/plain")

            return (doc['url'], {
                "file": file,
                "description": doc.get("description", ""),
                "text": text
            })

        except Exception as e:
            print(f"Error uploading website {doc.get('url')}: {e}")
            traceback.print_exc()
            return None

    docs = list(KM_URLs_collection.find())
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(upload_site, docs))

    CONTEXT["loaded_websites"] = {
        url: data for url, data in results if data
    }
    return f"{len(CONTEXT['loaded_websites'])} website(s) loaded."


 
@tool
def query_pdfs(query: str) -> str:
    """Query loaded PDFs for the given question."""
    print("[TOOL CALL] query_pdfs")
    files = [d["file"] for d in (CONTEXT["loaded_pdfs"] or {}).values()]
    if not files: return "<p>No PDFs loaded.</p>"
    return genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_INSTRUCTION).generate_content([*files, query]).text.strip()
 
@tool
def query_websites(query: str) -> str:
    """Query loaded websites for the given question."""
    print("[TOOL CALL] query_websites")
    files = [d["file"] for d in (CONTEXT["loaded_websites"] or {}).values() if d.get("file")]
    if not files: return "<p>No websites loaded.</p>"
    return genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_INSTRUCTION).generate_content([*files, query]).text.strip()
 
 
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_INSTRUCTION),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])
 
tools = [load_pdfs_data, load_websites_data, query_pdfs, query_websites]
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, google_api_key=os.environ["GOOGLE_API_KEY"])
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
 
def generate_response_from_rag(query: str) -> Tuple[str, str]:  # ✅ Valid
    try:
        result = agent_executor.invoke({"input": query})
        output = result["output"]
 
        if "query_pdfs" in output:
            return output, "PDF"
        elif "query_websites" in output:
            return output, "Website"
        else:
            return output, "Unknown"
    except Exception as e:
        print(f"[ERROR] generate_response_from_rag: {e}")
        return "<p>Something went wrong. Please try again.</p>", "Error"
    


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