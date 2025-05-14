import os
import io
import logging
from typing import Dict, Any

import PyPDF2
import requests
from flask import Flask, request, jsonify

# Setup logger
def get_logger(name: str):
    logger = logging.getLogger(name)
    return logger

logger = get_logger(__name__)

# Create Flask app
app = Flask(__name__)

def extract_text_from_docx(docx_file) -> str:
    """Extract text content from a DOCX file."""
    try:
        doc = docx.Document(docx_file)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        logger.error(f"Failed to extract text from DOCX: {str(e)}")
        raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
        
def extract_text_from_pdf(pdf_file) -> str:
    """Extract text content from a PDF file."""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

@app.route("/extract_file_text/", methods=["POST"])
def extract_file_text():
    """
    Extract text content from a PDF or DOCX file URL.
    JSON Body should contain: { "url": "...", "type": "pdf" or "docx" }
    """
    try:
        data = request.get_json()
        url = data.get('url')
        file_type = data.get('type', '').lower()

        if not url or file_type not in ['pdf', 'docx']:
            return jsonify({"success": False, "error": "Missing or invalid 'url' or 'type'"}), 400

        response = requests.get(url)
        response.raise_for_status()
        file_bytes = io.BytesIO(response.content)

        if file_type == 'pdf':
            text = extract_text_from_pdf(file_bytes)
        elif file_type == 'docx':
            text = extract_text_from_docx(file_bytes)
        else:
            return jsonify({"success": False, "error": "Unsupported file type"}), 400

        return jsonify({
            "success": True,
            "data": {
                "text": text
            }
        })

    except Exception as e:
        logger.error(f"Text extraction failed: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
