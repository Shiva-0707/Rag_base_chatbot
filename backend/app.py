from flask import Flask, request, jsonify
from utils import process_file, get_answer
import os

app = Flask(__name__)
UPLOAD_FOLDER = "../uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage
DATA = {"vectorstore": None}


@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "Test endpoint is working!"})

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part in the request."}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file."}), 400
        file.seek(0)  # Ensure file pointer is at the start before saving
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        _, vectorstore = process_file(filepath)
        DATA["vectorstore"] = vectorstore
        return jsonify({"message": "File uploaded and processed successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/query", methods=["POST"])
def query_doc():
    question = request.json.get("question", "")
    if DATA["vectorstore"] is None:
        return jsonify({"answer": "Please upload a file first."})
    
    answer = get_answer(question, DATA["vectorstore"])
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
