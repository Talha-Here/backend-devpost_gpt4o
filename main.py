from flask import Flask
from flask_cors import CORS

from flask_app import flask_app
from flask_app_google_search import flask_app_google_search

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://devpost-gpt4o-hackathon.vercel.app"])
# CORS(app, origins=["https://devpost-gpt4o-hackathon.vercel.app"])

# Register both Flask apps with different prefixes
app.register_blueprint(flask_app, url_prefix='/flask_app')
app.register_blueprint(flask_app_google_search, url_prefix='/flask_app_google_search')

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000)
    app.run(debug=True)
