# frontend/streamlit_app.py

import streamlit as st
import requests

st.set_page_config(page_title="🧠 RAG Chatbot - Shivansh", layout="centered")

st.title("📄 DocsBot")

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    with st.spinner("Uploading and processing file..."):
        response = requests.post(
            "http://localhost:5000/upload",
            files={"file": uploaded_file}
        )
        if response.status_code == 200:
            st.success("✅ File uploaded and processed successfully!")
        else:
            st.error("❌ Failed to process the file.")

# Ask questions
question = st.text_input("Ask a question from your PDF report:")

if st.button("Ask"):
    if not uploaded_file:
        st.warning("Please upload a file first.")
    elif question.strip() == "":
        st.warning("Please type a question.")
    else:
        with st.spinner("Thinking..."):
            response = requests.post(
                "http://localhost:5000/query",
                json={"question": question}
            )
            if response.status_code == 200:
                st.write("🧠 **Answer:**")
                st.success(response.json()["answer"])
            else:
                st.error("❌ Error while getting answer.")
