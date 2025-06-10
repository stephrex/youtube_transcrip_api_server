import os
import io
import logging
from typing import Dict, Any
import docx
import PyPDF2
import requests
from flask import Flask, request, jsonify
import asyncio
from urllib.parse import urlparse, urlunparse

import markdownify
import readabilipy.simple_json
from protego import Protego
from httpx import AsyncClient, HTTPError

app = Flask(__name__)

DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; StandaloneFetcher/1.0)"

# Global shared client
shared_client = AsyncClient(follow_redirects=True, timeout=10.0)

def extract_content_from_html(html: str) -> str:
    ret = readabilipy.simple_json.simple_json_from_html_string(html, use_readability=True)
    if not ret["content"]:
        return "<error>Failed to simplify HTML content</error>"
    return markdownify.markdownify(ret["content"], heading_style=markdownify.ATX)


def get_robots_txt_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))


async def check_robots_txt(url: str, user_agent: str):
    robots_url = get_robots_txt_url(url)
    try:
        response = await shared_client.get(robots_url, headers={"User-Agent": user_agent})
    except HTTPError as e:
        print(f"Warning: Failed to fetch robots.txt: {e}")
        return

    if response.status_code in (401, 403):
        raise Exception(f"Access denied to robots.txt at {robots_url}")
    elif 400 <= response.status_code < 500:
        return

    robot_txt = "\n".join(
        line for line in response.text.splitlines() if not line.strip().startswith("#")
    )
    parser = Protego.parse(robot_txt)
    if not parser.can_fetch(url, user_agent):
        raise Exception(f"Blocked by robots.txt at {robots_url}")

def get_logger(name: str):
    logger = logging.getLogger(name)
    return logger

logger = get_logger(__name__)

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

@app.route("/fetch_url/", methods=["POST"])
def fetch_url_content():
    try:
        data = request.get_json()
        url = data.get("url")
        user_agent = data.get("user_agent", DEFAULT_USER_AGENT)
        force_raw = data.get("force_raw", False)
        ignore_robots = data.get("ignore_robots", False)

        if not url:
            return jsonify({"success": False, "error": "Missing 'url' in request"}), 400

        async def fetch():
            if not ignore_robots:
                await check_robots_txt(url, user_agent)

            try:
                response = await shared_client.get(url, headers={"User-Agent": user_agent})
            except HTTPError as e:
                return {"error": f"Failed to fetch URL: {str(e)}"}, 500

            if response.status_code >= 400:
                return {"error": f"Failed to fetch URL - Status Code: {response.status_code}"}, response.status_code

            content_type = response.headers.get("content-type", "")
            text = response.text

            if "<html" in text[:100].lower() or "text/html" in content_type or not content_type:
                if force_raw:
                    return {"text": text}, 200
                simplified = extract_content_from_html(text)
                return {"text": simplified}, 200
            else:
                return {
                    "content_type": content_type,
                    "text": text
                }, 200

        result, status_code = asyncio.run(fetch())
        if "error" in result:
            return jsonify({"success": False, "error": result["error"]}), status_code
        return jsonify({"success": True, "data": result}), status_code

    except Exception as e:
        logger.error(f"Error in fetch_url_content: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
