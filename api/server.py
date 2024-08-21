from flask import Flask, request, jsonify
from flask_cors import CORS

from lib.url import encode, decode
from lib.linter import lint, fix

app = Flask(__name__, static_folder='client/dist', static_url_path="/")
CORS(app)          
                    
# Global default values   
CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-+!"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file("index.html")

@app.route('/check', methods=['POST'])
def process_data():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'no JSON data sent'}), 400
    
    

    errors = lint(code=data.get('code', ''),
                  linter=data.get('linter', 'flake8'),
                  disable=data.get('disable', None))

    return jsonify(errors), 200

@app.route('/autofix', methods=['POST'])
def autofix():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'no JSON data sent'}), 400

    fixed = fix(code=data.get('code', ''))

    return jsonify(fixed), 200

@app.route('/encode', methods=['POST'])
def construct():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'no JSON data sent'}), 400

    errors = {"link": encode(linter=data.get('linter', 'flake8'),
                             disabled=data.get('disabled', None),
                             chars=CHARS), }
    return jsonify(errors), 200

@app.route('/decode', methods=['POST'])
def deconstruct():
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'no JSON data sent'}), 400

    errors = decode(code=data.get('settings', 'all'),
                    chars=CHARS,
                    linter=data.get('linter', 'flake8'))

    return jsonify(errors), 200

if __name__ == '__main__':
    app.run()
