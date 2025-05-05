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

@app.route("/extract_pdf_text/", methods=["POST"])
def extract_pdf_text():
    """Extract text content from a PDF URL."""
    try:
        # Get the URL from the JSON body of the request
        data = request.get_json()
        url = data.get('url')

        # Fetch the PDF from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raises exception for 4xx/5xx responses
        pdf_file = io.BytesIO(response.content)

        # Extract text from the PDF
        text = extract_text_from_pdf(pdf_file)

        # Return the extracted text
        return jsonify({
            "success": True,
            "data": {
                "text": text
            }
        })
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch PDF from URL: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to fetch PDF from URL: {str(e)}"
        }), 400
    except Exception as e:
        logger.error(str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
