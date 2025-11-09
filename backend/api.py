# app.py
import os
import certifi
import dotenv
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI") if os.environ.get("MONGO_URI") else dotenv.get_key('../.env', 'MONGO_URI')
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

# @app.route("/")
# def index():
#     # call url_for('static', ...) within templates instead of here
#     return render_template("index.html")

def serialize_doc(doc):
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_doc(v) for v in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc

@app.get("/api/events/paginate5")
def get_events():
    page = int(request.args.get("page", 0))
    limit = 5
    skip = page * limit
    events_cursor = collection.find().sort("eventTime", -1).skip(skip).limit(limit)
    events = [serialize_doc(event) for event in events_cursor]
    return jsonify(events)

@app.get("/api/events/getcme")
def get_cme():
    cme = collection.find_one({"eventType": "CME"}, sort=[("eventTime", -1)])
    if not cme:
        return jsonify({"error": "No CME data found"}), 404
    return jsonify(serialize_doc(cme))

@app.get("/api/events/getflr")
def get_flare():
    flare = collection.find_one({"eventType": "FLR"}, sort=[("eventTime", -1)])
    if not flare:
        return jsonify({"error": "No FLR data found"}), 404
    return jsonify(serialize_doc(flare))

@app.get("/api/events/getgst")
def get_gst():
    gst = collection.find_one({"eventType": "GST"}, sort=[("eventTime", -1)])
    if not gst:
        return jsonify({"error": "No GST data found"}), 404
    return jsonify(serialize_doc(gst))

@app.get("/api/events/getips")
def get_ips():
    ips = collection.find_one({"eventType": "IPS"}, sort=[("eventTime", -1)])
    if not ips:
        return jsonify({"error": "No IPS data found"}), 404
    return jsonify(serialize_doc(ips))

# Optional: also export 'application' (some platforms expect this)
application = app

# keep this so `python app.py` still works locally
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)