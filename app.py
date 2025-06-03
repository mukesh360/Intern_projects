from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
from sentence_transformers import SentenceTransformer
import faiss
import PyPDF2
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = 'pdfs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')



@app.route('/')
def home():
    return render_template('index.html')


# ---------- UPLOAD ----------
@app.route('/upload')
def upload_form():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file and file.filename.lower().endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('upload_form'))
    else:
        return redirect(request.url)


# ---------- SHOW FILES ----------
@app.route('/showfiles', methods=['GET', 'POST'])
def showfiles():
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith('.pdf')]
    return render_template('showfiles.html', files=files)


@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ---------- DELETE ----------
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('showfiles'))


# ---------- UTILITY FUNCTIONS ----------
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text


def get_top_k_answers(text, question, top_k=5):
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    embeddings = model.encode(chunks)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    question_embedding = model.encode([question])
    D, I = index.search(question_embedding, top_k)

    answers = [chunks[i] for i in I[0]]
    return answers


# ---------- ASK QUESTION ----------
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')
    pdf_name = data.get('pdf_name')

    if not question or not pdf_name:
        return jsonify({'error': 'Please provide both a question and PDF filename.'})

    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)
    if not os.path.exists(pdf_path):
        return jsonify({'error': 'PDF not found.'})

    text = extract_text_from_pdf(pdf_path)
    answers = get_top_k_answers(text, question, top_k=5)

    return jsonify({'answers': answers})



if __name__ == '__main__':
    app.run(debug=True)
