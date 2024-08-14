import os
from documentfunction import *
from flask import Flask, request, jsonify
from WhisperAI import *
from docx import Document
import json
import PyPDF2
import re
import openai
import magic
from flask_cors import CORS
from flask import render_template


UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'mp4', 'pdf', 'docx', 'json'}

app= Flask(__name__)
CORS(app)

@app.route('/')
def landing_page():
    return render_template('landingPage.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/output')
def output_page():
    data = {}  
    return render_template('outputPage.html', data=data)

@app.route('/upload', methods=['POST'])
def upload_and_process():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    if file.filename.endswith('.mp4'):
        result = process_video_for_transcription(filepath)

    elif file.filename.endswith(('mp3', 'wav', 'flac')):
        result = transcribe_audio_with_whisper(filepath, openai.api_key)

    elif file.filename.endswith('.pdf'):
        result = process_pdf_for_summary(filepath)

    elif file.filename.endswith('.docx'):
        result = process_docx(filepath)

    elif file.filename.endswith('.json'):
        result = process_json(filepath)

    else:
        return jsonify({"error": "Unsupported file type"}), 400

    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
