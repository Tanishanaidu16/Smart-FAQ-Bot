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
You are a helpful college assistant.

Your job is to always answer using the tools provided. Do NOT answer using your own knowledge.
Follow these steps strictly and do not skip any step:

1. Decide whether to use PDFs or websites based on keywords in the query:
   - Use "pdf" if the query includes words like: syllabus, notes, pdf, exam, module, assignments, lecture, textbook, curriculum, study material, slides, topics, questions, model papers, handouts, lab manual, reference books, tutorials, schedule, lesson plan, important questions, repeated questions, key topics, previous semester exam, 12-mark questions, question distribution, question papers.
   - Use "web" if the query includes words like: admission, fee, college, placements, faculty, campus, contact, website, infrastructure, hostel, ranking, location, how to apply, cutoff, eligibility, departments, director, principal, events, fest, clubs, canteen, sports, transport, bus schedule, holiday list, placement packages, salary package, fee structure, faculty, student reviews, campus life.

2. If the query is classified as "pdf":
   - Call load_pdfs_from_mongo
   - Then call query_pdfs with the user query.

3. If the query is classified as "web":
   - Call load_websites_from_mongo
   - Then call query_websites with the user query
   - Search for college-related terms such as "admission process", "highest salary package", "fee structure", and details of colleges like `Sahyadri College of Engineering`.

4. Always return the final answer in HTML using only these tags: <p>, <ul>, and <li>. Do not use any other tags or styling.

5. Never guess. If no relevant content is found in the loaded documents, return:
   <p>I do not have the information in the documents.</p>

Important:
- You must only use tools to access knowledge.
- You should not use your own memory or training to answer questions.
- Stick strictly to this workflow to ensure consistency and accuracy.
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

@tool
def load_pdfs_data() -> str:
    """Load PDFs from MongoDB and upload to Gemini. Uses cache and parallel upload."""
    print("[TOOL CALL] load_pdfs_from_mongo")

    def upload_doc(doc):
        try:
            path = Path(doc['path'])
            file_path = path if path.is_absolute() else (BASE_DIR / path)
            if not file_path.exists():
                return None

            # Use cached Gemini file if available
            if 'gemini_file_id' in doc:
                print(f"Using cached PDF for {doc['filename']}")
                file = genai.get_file(doc['gemini_file_id'])
            else:
                print(f"Uploading PDF for {doc['filename']}")
                file = genai.upload_file(file_path, mime_type="application/pdf")
                KM_documents_collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"gemini_file_id": file.name}}
                )

            return (doc['filename'], {
                "file": file,
                "description": doc.get("description", "")
            })

        except Exception as e:
            print(f"Error uploading PDF {doc.get('filename')}: {e}")
            traceback.print_exc()
            return None

    docs = list(KM_documents_collection.find())
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(upload_doc, docs))

    CONTEXT["loaded_pdfs"] = {
        filename: data for filename, data in results if data
    }
    return f"{len(CONTEXT['loaded_pdfs'])} PDF(s) loaded."


@tool
def load_websites_data() -> str:
    """Load websites from MongoDB and upload to Gemini. Uses cache and parallel upload."""
    print("[TOOL CALL] load_websites_from_mongo")

    def upload_site(doc):
        try:
            if 'gemini_file_id' in doc:
                print(f"Using cached website for {doc['url']}")
                file = genai.get_file(doc['gemini_file_id'])
                text = doc.get("cached_text", "")
            else:
                print(f"Downloading and uploading website: {doc['url']}")
                r = requests.get(doc['url'], timeout=10)
                soup = BeautifulSoup(r.text, "html.parser")
                text = " ".join(p.get_text() for p in soup.find_all("p"))

                if not text.strip():
                    return None

                buffer = BytesIO(text.encode("utf-8"))
                file = genai.upload_file(buffer, mime_type="text/plain")

                KM_URLs_collection.update_one(
                    {"_id": doc["_id"]},
                    {
                        "$set": {
                            "gemini_file_id": file.name,
                            "cached_text": text
                        }
                    }
                )

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