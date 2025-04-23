from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable
from youtube_transcript_api.formatters import TextFormatter
from youtube_transcript_api._errors import TooManyRequests
from youtube_transcript_api.proxies import GenericProxyConfig
import re
import os

app = Flask(__name__)

# Helper: Extract video ID from URL
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None

# Custom headers (User-Agent spoofing)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' 
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/123.0.0.0 Safari/537.36'
}

# Proxy config (optional, set via environment variable or leave as None)
proxy = os.environ.get("HTTP_PROXY")  # Format: http://username:password@ip:port
proxy_config = GenericProxyConfig(proxy_url=proxy) if proxy else None

@app.route('/transcript', methods=['POST'])
def get_transcript():
    url = request.json.get('url')
    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            proxies=proxy_config,
            cookies=None,
            headers=headers  # <- Custom user-agent header
        )

        # Format transcript to plain text
        formatter = TextFormatter()
        text_transcript = formatter.format_transcript(transcript)

        return jsonify({'transcript': text_transcript})

    except TranscriptsDisabled:
        return jsonify({'error': 'Transcripts are disabled for this video'}), 403
    except VideoUnavailable:
        return jsonify({'error': 'Video is unavailable'}), 404
    except TooManyRequests:
        return jsonify({'error': 'Too many requests. Please slow down.'}), 429
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
