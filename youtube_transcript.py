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
    try:
        transcript_list = YouTubeTranscriptApi().list('video_id')
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
