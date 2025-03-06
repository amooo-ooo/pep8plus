__all__ = [
    "Api",
    "TOOLS"
]

from functools import partial
from typing import List, Tuple, Callable, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS

from lib.utils import encode, decode, lint, fix

TOOLS: List[Tuple[str, Callable]] = [
    ("/check", lint),
    ("/autofix", fix),
    ("/encode", encode),
    ("/decode", decode)
]

class Api(Flask):
    def __init__(self, tools: Optional[List[Tuple[str, Callable]]] = None):
        super().__init__(__name__, static_folder='client/dist', static_url_path="/")
        CORS(self)
        self.setup_routes(tools or TOOLS)

    def setup_routes(self, tools: List[Tuple[str, Callable]]):
        self.add_url_rule('/', defaults={'path': ''}, view_func=self.catch_all)
        self.add_url_rule('/<path:path>', view_func=self.catch_all)
        
        # TODO: must be a cleaner way
        for path, method in tools:
            view_func = partial(self.handle, method)
            view_func.__name__ = method.__name__ 
            self.add_url_rule(path, methods=['POST'], view_func=view_func)

    def catch_all(self, path: str = "index.html"):
        return self.send_static_file(path)

    def handle(self, func: Callable):
        data = request.get_json(force=True)
        if not data:
            return jsonify({'error': 'no JSON data sent'}), 400
        return jsonify(func(**data)), 200

def main():    
    app_instance = Api(TOOLS)
    app_instance.run()

if __name__ == '__main__':
    main()
