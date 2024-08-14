import openai
from WhisperAI import *
from documentfunction import *

openai.api_key = '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'
def transcribe_audio_with_whisper(audio_path, openai_api_key):
    
    with open(audio_path, "rb") as f:
        response = openai.Audio.transcribe("whisper-1", f)
    
        summary = summarize_with_gpt3(response)
        return summary

if __name__ == '__main__':
    audio_path = input("Enter the path to your audio file: ")
    transcript = transcribe_audio_with_whisper(audio_path)
    print("Transcription:\n", transcript)
