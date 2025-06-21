import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
# 🔐 Set your OpenAI API Key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#client = OpenAI(api_key="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")  # Replace with your actual key

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Step 1: Extract raw text from PDF
def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    return "\n".join([page.get_text() for page in doc])

# Step 2: Break text into smaller chunks (context windows)
def chunk_text(text, max_length=500):
    sentences = text.split(". ")
    chunks, chunk = [], ""
    for sentence in sentences:
        if len(chunk) + len(sentence) <= max_length:
            chunk += sentence + ". "
        else:
            chunks.append(chunk.strip())
            chunk = sentence + ". "
    if chunk:
        chunks.append(chunk.strip())
    return chunks

# Step 3: Process file - chunking and indexing
def process_file(filepath):
    text = extract_text_from_pdf(filepath)
    chunks = chunk_text(text)
    embeddings = model.encode(chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return chunks, {"index": index, "chunks": chunks}

# Step 4: Use OpenAI to get answer based on top chunks
def get_answer(query, vectorstore):
    query_embedding = model.encode([query])
    D, I = vectorstore["index"].search(np.array(query_embedding), k=3)
    relevant_chunks = [vectorstore["chunks"][i] for i in I[0]]
    context = "\n".join(relevant_chunks)

    prompt = f"""You are a helpful assistant. Use the following context to answer the question.

Context:
{context}

Question: {query}
Answer:"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error while getting response from OpenAI: {str(e)}"
