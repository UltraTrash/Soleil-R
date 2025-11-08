# app.py
import os
import certifi
import dotenv
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI") if os.environ.get("MONGO_URI") else dotenv.get_key('.env', 'MONGO_URI')
def make_db_client():
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI environment variable not set")
    client = MongoClient(MONGO_URI, tlscafile=certifi.where(), serverSelectionTimeoutMS=5000)
    # test connection
    client.server_info()
    return client

client = make_db_client()
db = client["solarweather"]         
collection = db["events"]

@app.route("/")
def index():
    # call url_for('static', ...) within templates instead of here
    return render_template("index.html")

@app.get("/api/events")
def get_events():
    page = int(request.args.get("page", 0))
    limit = 5
    skip = page * limit

    events = list(collection.find().sort("eventTime", -1).skip(skip).limit(limit))
    return jsonify(events)

# Optional: also export 'application' (some platforms expect this)
application = app

# keep this so `python app.py` still works locally
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)