import os
from Documents import *
from flask import Flask, request, jsonify
from WhisperAI import *
from docx import Document
import json
import PyPDF2
import re
import openai


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_audio_and_transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        if file.filename.endswith('.mp4'):
            if not is_mp4(filepath):
                return jsonify({"error": "Invalid MP4 file"}), 400

            compressed_video_path = os.path.join(UPLOAD_FOLDER, "compressed_" + file.filename)
            audio_output_path = os.path.join(UPLOAD_FOLDER, "extracted_" + os.path.splitext(file.filename)[0] + ".wav")

            compress_video(filepath, compressed_video_path)
            extract_audio_from_video(compressed_video_path, audio_output_path)
            
            transcript = transcribe_audio_with_whisper(audio_output_path, openai_api_key=API_key)
            summarizedScript_mp4 = summarize_with_gpt3(transcript, API_key)

            return jsonify({"transcript": transcript}), 200

        elif file.filename.endswith(('mp3', 'wav', 'flac')):
            transcript = transcribe_audio_with_whisper(filepath, openai_api_key=API_key)
            summarizedScript_audio = summarize_with_gpt3(transcript, API_key)

            return jsonify({"transcript": transcript}), 200

        elif file.filename.endswith('.pdf'):
            pdf_summary_text = ""
            pdf_file_path = filepath
            pdf_file = open(pdf_file_path, 'rb')
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            for page_num in range(len(pdf_reader.pages)):

                page_text = pdf_reader.pages[page_num].extract_text().lower()

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a journalist."},
                        {"role": "user", "content": f"Summarize this: {page_text}"},
                            ],
            
                )
            page_summary = response["choices"][0]["message"]["content"]
            pdf_summary_text+=page_summary + "\n"
            
            pdf_summary_file = pdf_file_path.replace(os.path.splitext(pdf_file_path)[1], "_summary.txt")
            with open(pdf_summary_file, "w+") as file:
                file.write(pdf_summary_text)

            pdf_file.close()

            with open(pdf_summary_file, "r") as file:
                print(file.read())


        elif file.filename.endswith('.docx'):
            transcript = extract_text_from_docx(filepath)
            summarizedScript_docx = summarize_with_gpt3(transcript, API_key)
        
        
        
        elif file.filename.endswith('.json'):
            transcript = extract_text_from_json(filepath)
            summarizedScript_json = summarize_with_gpt3(transcript, API_key)


        output_file_path = os.path.join(UPLOAD_FOLDER, "summarized_" + os.path.splitext(file.filename[0] + ".txt"))
        with open(output_file_path, "w") as out_file:
            if file.filename.endswith('.mp4'):
                out_file.write(summarizedScript_mp4)
            elif file.filename.endswith(('mp3', 'wav', 'flac')):
                out_file.write(summarizedScript_audio)
            elif file.filename.endswith('.pdf'):
                out_file.write(pdf_summary_text)
            elif file.filename.endswith('.docx'):
                out_file.write(summarizedScript_docx)
            elif file.filename.endswith('.json'):
                out_file.write(summarizedScript_json)

            return jsonify({"success": "File uploaded and processed successfully", "summary_file": output_file_path}), 200
    
    return jsonify({"error": "File upload failed"}), 500
