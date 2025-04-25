# from youtube_transcript_api.proxies import GenericProxyConfig
# from youtube_transcript_api.formatters import TextFormatter
# import os
# import re
# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable
# from flask import Flask, request, jsonify
import re
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Helper: Extract video ID from YouTube URL


def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None

# Endpoint to get transcript via SearchAPI


@app.route('/transcript', methods=['POST'])
def get_transcript():
    data = request.json
    url = data.get('url')
    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    api_url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "youtube_transcripts",
        "video_id": video_id,
        # Make sure to set this in your environment
        "api_key": "zwxLP7UhbXLsMC2XAfUS9xD3"
    }

    response = requests.get(api_url, params=params)

    if response.status_code != 200:
        return jsonify({'error': f"API request failed: {response.text}"}), response.status_code

    return jsonify(response.json())


# Run app safely
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(debug=True, host='0.0.0.0', port=port)


#     url = request.json.get('url')
#     video_id = extract_video_id(url)

#     if not video_id:
#         return jsonify({'error': 'Invalid YouTube URL'}), 400

#     ytt_api = YouTubeTranscriptApi(
#         proxy_config=GenericProxyConfig(
#             http_url="http://50.223.246.237:80",
#             https_url="https://170.106.136.15:13001",
#         )
#     )
#     try:
#         transcript = ytt_api.get_transcript(video_id)
#         return jsonify({'transcript': transcript})
#     except TranscriptsDisabled:
#         return jsonify({'error': 'Transcripts are disabled for this video'}), 403
#     except VideoUnavailable:
#         return jsonify({'error': 'Video unavailable'}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if
# == == == =

# app = Flask(__name__)

# # Helper: Extract video ID from URL


# def extract_video_id(url):
#     match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
#     return match.group(1) if match else None


# # Custom headers (User-Agent spoofing)
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                   'AppleWebKit/537.36 (KHTML, like Gecko) '
#                   'Chrome/123.0.0.0 Safari/537.36'
# }

# # Proxy config (optional, set via environment variable or leave as None)
# # proxy = os.environ.get("HTTP_PROXY")  # Format: http://username:password@ip:port
# # proxy_config = GenericProxyConfig(proxy_url=proxy) if proxy else None


# @app.route('/transcript', methods=['POST'])
# def get_transcript():
#     url = request.json.get('url')
#     video_id = extract_video_id(url)

#     if not video_id:
#         return jsonify({'error': 'Invalid YouTube URL'}), 400

#     try:
#         transcript = YouTubeTranscriptApi.get_transcript(
#             video_id,
#             # proxies=proxy_config,
#             cookies=None
#         )

#         # Format transcript to plain text
#         formatter = TextFormatter()
#         text_transcript = formatter.format_transcript(transcript)

#         return jsonify({'transcript': text_transcript})

#     except TranscriptsDisabled:
#         return jsonify({'error': 'Transcripts are disabled for this video'}), 403
#     except VideoUnavailable:
#         return jsonify({'error': 'Video is unavailable'}), 404
#     except Exception as e:
#         return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(debug=True, host='0.0.0.0', port=port)
# >>>>>> > main
