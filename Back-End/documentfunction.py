import os
import PyPDF2
import re
import openai
from docx import Document
import json



MAX_TOKENS = 1200


def summarize_with_gpt3(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Summarize the following text for me."},
            {"role": "user", "content": f"{text}"}
        ],
        max_tokens=150  
    )
    summary = response.choices[0].message.content
    return summary

def process_pdf_for_summary(pdf_file_path, pages_per_chunk=5):
    pdf_summary_text = ""
    
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        
        for start_page in range(0, total_pages, pages_per_chunk):
            chunk_text = ""
            end_page = min(start_page + pages_per_chunk, total_pages)
            
            for page_num in range(start_page, end_page):
                chunk_text += pdf_reader.pages[page_num].extract_text().lower()
            
            if len(chunk_text) > MAX_TOKENS:  
                chunk_text = chunk_text[:MAX_TOKENS]
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a journalist."},
                    {"role": "user", "content": f"Summarize this: {chunk_text}"}
                ]
            )
            
            chunk_summary = response["choices"][0]["message"]["content"]
            pdf_summary_text += chunk_summary + "\n"
    
    pdf_summary_file_path = pdf_file_path.replace(os.path.splitext(pdf_file_path)[1], "_summary.txt")
    with open(pdf_summary_file_path, "w+") as summary_file:
        summary_file.write(pdf_summary_text)
    
    return pdf_summary_text, pdf_summary_file_path

def extract_text_from_json(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)

    strings = extract_strings_from_dict(data)
    return ' '.join(strings)


def extract_strings_from_dict(d):
    strings = []

    for key, value in d.items():
        if isinstance(value, str):
            strings.append(value)
        elif isinstance(value, dict):
            strings.extend(extract_strings_from_dict(value))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    strings.append(item)
                elif isinstance(item, dict):
                    strings.extend(extract_strings_from_dict(item))

    return strings


def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def process_docx(docx_path):
    extracted_text = extract_text_from_docx(docx_path)
    summary = summarize_with_gpt3(extracted_text)
    return summary

def process_json(json_path):
    extracted_text = extract_text_from_json(json_path)
    summary = summarize_with_gpt3(extracted_text)
    return summary

