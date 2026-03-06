from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from lyrics import search_lyrics
from pronunciation import lyrics_to_korean

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/lyrics', methods=['POST'])
def get_lyrics():
    data = request.get_json() or {}
    artist = data.get('artist', '').strip()
    title = data.get('title', '').strip()

    if not artist or not title:
        return jsonify({'error': 'artist and title are required'}), 400

    lyrics, source = search_lyrics(artist, title)

    if not lyrics:
        return jsonify({'error': 'Lyrics not found'}), 404

    return jsonify({'lyrics': lyrics, 'source': source})


@app.route('/api/pronunciation', methods=['POST'])
def get_pronunciation():
    data = request.get_json() or {}
    lyrics = data.get('lyrics', '').strip()

    if not lyrics:
        return jsonify({'error': 'lyrics is required'}), 400

    lines = lyrics_to_korean(lyrics)
    return jsonify({'lines': lines})


if __name__ == '__main__':
    app.run(port=5001, debug=True)
