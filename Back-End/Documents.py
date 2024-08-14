import os
import PyPDF2
import re
import openai
from docx import Document
import json

MAX_TOKENS = 1200



def summarize_with_gpt3(text, api_key):
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



def extract_text_from_json(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
    return str(data)


def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

pdf_summary_text = ""
pdf_file_path = 
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
