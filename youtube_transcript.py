from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable
from youtube_transcript_api.proxies import GenericProxyConfig
import re
import os

app = Flask(__name__)


def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None


@app.route('/transcript', methods=['POST'])
def get_transcript():
    url = request.json.get('url')
    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    ytt_api = YouTubeTranscriptApi(
        proxy_config=GenericProxyConfig(
            http_url="http://50.223.246.237:80",
            https_url="https://170.106.136.15:13001",
        )
    )
    try:
        transcript_list = ytt_api.list('video_id')
        for transcript in transcript_list:
        print(transcript.fetch())
        transcript = ytt_api.get_transcript(video_id)
        return jsonify({'transcript': transcript})
    except TranscriptsDisabled:
        return jsonify({'error': 'Transcripts are disabled for this video'}), 403
    except VideoUnavailable:
        return jsonify({'error': 'Video unavailable'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Default to 5000 locally
    app.run(host='0.0.0.0', port=port)
