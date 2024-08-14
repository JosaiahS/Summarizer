import os
from flask import Flask, request, jsonify
from WhisperAI import *

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

@app.route('/upload', methods=['POST'])

def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    if not (file.filename.endswith('.pdf') or file.filename.endswith('.docx') 
            or file.filename.endswith('.json') or file.filename.endswith('.mp4')
            or file.filename.endswith('.mp3')):
        return jsonify({"error": "Invalid file type"}), 400
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    if file.filename.endswith('.mp4'):
        if not is_mp4(filepath):
            return jsonify({"error": "Invalid MP4 file"}), 400

        compressed_video_path = os.path.join(UPLOAD_FOLDER, "compressed_" + file.filename)
        compress_video(filepath, compressed_video_path)

        audio_output_path = os.path.join(UPLOAD_FOLDER, "extracted_" + os.path.splitext(file.filename)[0] + ".wav")
        extract_audio_from_video(compressed_video_path, audio_output_path)
        transcriptUN = transcribe_audio_with_whisper(audio_output_path, "API key") 


    else: 
        pass

    return jsonify({"message": "File processed successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
