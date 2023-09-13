from flask import Flask
from flask_cors import CORS
import json

app = Flask(__name__)

@app.route("/api/healthcheck")
def hello_world():
    return json.loads('{"status": "ok"}')

if __name__ == '__main__':
    CORS(app, resources={r"/api/*": {"origins": "http://localhost"}})
    app.run(host='127.0.0.1', port=8080, debug=True)