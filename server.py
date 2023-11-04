from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from src.url import encode, decode
from src.linter import lint

app = Flask(__name__)
CORS(app)

# Global default values
CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-'

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)

@app.route('/check', methods=['POST'])
def process_data():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'no JSON data sent'}), 400

    errors = lint(code=data['code'],
                  linter=data['linter'],
                  disable=data['disable'])

    return jsonify(errors), 200

@app.route('/encode', methods=['POST'])
def construct():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'no JSON data sent'}), 400

    errors = {"link": encode(linter=data['linter'],
                             disabled=data['disabled'],
                             chars=CHARS), }
    return jsonify(errors), 200

@app.route('/decode', methods=['POST'])
def deconstruct():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'no JSON data sent'}), 400

    errors = decode(code=data['settings'],
                    chars=CHARS,
                    linter=data['linter'])

    return jsonify(errors), 200

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
