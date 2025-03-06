__all__ = [
    "TOOLS"
]

from typing import List, Tuple, Callable
from flask import Flask, request, jsonify
from flask_cors import CORS
from lib.utils import encode, decode, lint, fix

TOOLS: List[Tuple[str, Callable]] = [
    ("/check", lint),
    ("/autofix", fix),
    ("/encode", encode),
    ("/decode", decode)
]

app = Flask(__name__, static_folder='client/dist', static_url_path="/")
CORS(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path: str = "index.html"):
    return app.send_static_file(path)

@app.route('/check', methods=['POST'])
def check():
    return handle(lint)

@app.route('/autofix', methods=['POST'])
def autofix():
    return handle(fix)

@app.route('/encode', methods=['POST'])
def encode_route():
    return handle(encode)

@app.route('/decode', methods=['POST'])
def decode_route():
    return handle(decode)

def handle(func: Callable):
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'no JSON data sent'}), 400
    return jsonify(func(**data)), 200

def main():
    app.run()

if __name__ == '__main__':
    main()
