from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from lyrics import search_lyrics
from pronunciation import lyrics_to_korean
from search import search_candidates
from charts import get_chart, SUPPORTED_COUNTRIES

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/lyrics", methods=["POST"])
def get_lyrics():
    data = request.get_json() or {}
    artist = data.get("artist", "").strip()
    title = data.get("title", "").strip()

    if not artist and not title:
        return jsonify({"error": "artist or title is required"}), 400

    lyrics, source = search_lyrics(artist, title)

    if not lyrics:
        return jsonify({"error": "Lyrics not found"}), 404

    return jsonify({"lyrics": lyrics, "source": source})


@app.route("/api/pronunciation", methods=["POST"])
def get_pronunciation():
    data = request.get_json() or {}
    lyrics = data.get("lyrics", "").strip()

    if not lyrics:
        return jsonify({"error": "lyrics is required"}), 400

    lines = lyrics_to_korean(lyrics)
    return jsonify({"lines": lines})


@app.route('/api/search', methods=['POST'])
def get_search_candidates():
    data = request.get_json() or {}
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'error': 'query is required'}), 400

    results = search_candidates(query)
    return jsonify({'results': results})


@app.route('/api/charts', methods=['GET'])
def get_charts():
    country = request.args.get('country', 'kr').lower()
    if country not in SUPPORTED_COUNTRIES:
        return jsonify({'error': f'Unsupported country: {country}'}), 400
    tracks = get_chart(country)
    return jsonify({'country': country, 'tracks': tracks})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
