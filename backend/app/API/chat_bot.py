from flask import Blueprint ,request,jsonify
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAI
import os,tiktoken,PyPDF2
from groq import Groq
from dotenv import load_dotenv
from langchain_core.documents import Document

from werkzeug.utils import secure_filename

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

UPLOAD_FOLDER = "UPLOAD"
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


def chunk_text(text: str,question:str):
    print(f"==>> text: {text}")
    """Split text into chunks for processing."""
    # loader = PDFPlumberLoader(f"/home/rohan/work_place/OpenCV_demo/backend/UPLOAD/{text}")
    # with open(text, "r") as f:
    #     contents = f.read()
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    chunk_size = 2000 
    chunk_overlap = 200
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_text = tokenizer.decode(tokens[start:end])
        chunks.append(Document(page_content=chunk_text))
        start += chunk_size - chunk_overlap
        db = Chroma.from_documents(chunks)
    return answer_with_groq(db,question)
 
def answer_with_groq(db,question, k=4):

    # 1. Retrieve most relevant chunks
    docs = db.similarity_search(question, k=k)

    # 2. Build the context text
    context = "\n\n".join([d.page_content for d in docs])
    # print("Context:  ",context)

    # 3. Build the prompt sent to Groq
    prompt = f"""
    You are a helpful assistant trained to provide accurate and relevant answers based on the context of the user's query.
    When a user asks a question, analyze the context carefully and respond in a way that directly addresses their need.
    Your responses should be clear, informative, and tailored to the specific nature of the user's question,
    whether it's general knowledge, technical assistance, academic inquiry, or something else.
    If the Question is Not realted to Context give Casually Answer to User

    Context:
    {context}

    Question:
    {question}

    Answer:
    """.strip()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # <-- BEST Groq model for QA
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    print(response.choices[0].message.content)
    return response.choices[0].message.content


# def documents_embeddings(documnt,question):
#     try:
#         loader = PDFPlumberLoader(f"UPLOAD/{documnt}")

#         docs = loader.load()

#         spliter = RecursiveCharacterTextSplitter(chunk_size = 500,chunk_overlap = 100)
#         chunks = spliter.split_documents(docs)

#         embediings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
#         vector_list = embediings.embed_documents([c.page_content for c in chunks])
#         print(vector_list)

#         db = Chroma.from_documents(chunks,embediings)    
#         return answer_with_groq(db,question)
#     except Exception as e:
#         print(f"==>> e: {e}")
#         return e

chat_bp = Blueprint("chat_bp",__name__)

def rag_pipeline(question):
#   docs = db.similarity_search(question, k=k)

#   context = "\n\n".join([d.page_content for d in docs])

  prompt = f"""
    You are a helpful assistant trained to provide accurate and relevant answers based on the context of the user's query.
    When a user asks a question, analyze the context carefully and respond in a way that directly addresses their need.
    Your responses should be clear, informative, and tailored to the specific nature of the user's question,
    whether it's general knowledge, technical assistance, academic inquiry, or something else.
    

    Question:
    {question}

    Answer:
    """.strip()

  response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

  final_answer = response.choices[0].message.content
  return final_answer



@chat_bp.route('/chat',methods=["POST"])
def start_chat():
    try:
        data = request.get_json()
        message = data.get("message")
        response = rag_pipeline(message)
        return jsonify({"response": response})
    except Exception as e:
       return jsonify ({"msg":e})
    


@chat_bp.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.json

        question = data.get("question")
        document_ids = data.get("document_ids")
        
        for file_id in document_ids:
            file_path = os.path.join("UPLOAD", file_id)
            if not os.path.exists(file_path):
                return jsonify({"msg": f"File not found: {file_id}"}), 404

        # Process the file
        all_text = ""
        for file_id in document_ids:
            file_path = os.path.join(UPLOAD_FOLDER, file_id)
            if not os.path.exists(file_path):
                return jsonify({"msg": f"File not found: {file_id}"}), 404
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    all_text += page.extract_text() or ""

        if not question:
            return jsonify({"msg": "Question is required"}), 400

        # Here you call your embeddings logic
        answer = chunk_text(all_text, question)

        return jsonify({"answer": answer}), 200

    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    

@chat_bp.route("/upload", methods=["POST"])
def upload_documents():
    try:
        if "files" not in request.files:
            return jsonify({"msg": "No files sent"}), 400

        files = request.files.getlist("files")
        saved_ids = []

        for f in files:
            filename = secure_filename(f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, filename))
            saved_ids.append(filename)

        return jsonify({"file_ids": saved_ids}), 200

    except Exception as e:
        return jsonify({"msg": str(e)}), 500