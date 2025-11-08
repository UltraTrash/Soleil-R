# donki_worker.py
import os
import time
import requests
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient, errors

# Config from environment
API_KEY = os.environ.get("NASA_DONKI_API")  # must be set in Render secrets/env
MONGO_URI = os.environ.get("MONGO_URL")  # must be set in Render secrets/env
FETCH_INTERVAL_SECONDS = int(os.environ.get("DONKI_FETCH_INTERVAL", "600"))  # default 10 minutes

DONKI_FLR_URL = "https://api.nasa.gov/DONKI/FLR"
DONKI_CME_URL = "https://api.nasa.gov/DONKI/CME"
DONKI_GST_URL = "https://api.nasa.gov/DONKI/GST"
DONKI_IPS_URL = "https://api.nasa.gov/DONKI/IPS"


def get_last_day_range():
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")


def fetch_donki_data(url, start_date, end_date):
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "api_key": API_KEY,
    }
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def parse_time(event):
    time_str = event.get("beginTime") or event.get("startTime") or event.get("eventTime")
    if not time_str:
        return datetime.min
    try:
        return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.min


def get_unique_id_for_event(event):
    # Pick the best id field available
    for key in ("flrID", "activityID", "gstID", "eventID", "id"):
        val = event.get(key)
        if val:
            return str(val)
    # fallback to link or timestamp
    if event.get("link"):
        return str(event["link"])
    return f"unknown-{parse_time(event).isoformat()}"


def upsert_event(collection, event):
    event_id = get_unique_id_for_event(event)
    # Use a compound _id to avoid collisions between types
    doc_id = f"{event.get('eventType','UNKNOWN')}::{event_id}"
    # Add or update lastSeen time
    event["_lastSeen"] = datetime.utcnow().isoformat()
    # Upsert - keep the event JSON (replace fields) and set lastModified timestamp
    update_doc = {
        "$set": event,
        "$currentDate": {"lastModified": True},
    }
    collection.update_one({"_id": doc_id}, update_doc, upsert=True)


def make_db_client():
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI environment variable not set")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # test connection
    client.server_info()
    return client


def main_loop():
    client = make_db_client()
    # If MONGO_URI includes db name, get_default_database returns it; otherwise fallback to 'donki'
    try:
        db = client.get_default_database() or client["donki"]
    except Exception:
        db = client["donki"]
    coll = db["events"]
    # Ensure an index for easy queries (not strictly required since we use _id)
    try:
        coll.create_index([("eventType", 1)])
    except Exception:
        pass

    while True:
        start_date, end_date = get_last_day_range()
        try:
            flares = fetch_donki_data(DONKI_FLR_URL, start_date, end_date)
            cmes = fetch_donki_data(DONKI_CME_URL, start_date, end_date)
            gsts = fetch_donki_data(DONKI_GST_URL, start_date, end_date)
            shocks = fetch_donki_data(DONKI_IPS_URL, start_date, end_date)

            # annotate type
            for f in flares:
                f["eventType"] = "FLR"
            for c in cmes:
                c["eventType"] = "CME"
            for g in gsts:
                g["eventType"] = "GST"
            for s in shocks:
                s["eventType"] = "IPS"

            events = flares + cmes + gsts + shocks
            # sort newest first (optional)
            events.sort(key=parse_time, reverse=True)

            for ev in events:
                try:
                    upsert_event(coll, ev)
                except errors.PyMongoError as e:
                    print("Mongo upsert error:", e)

            print(f"[{datetime.utcnow().isoformat()}] Fetched {len(events)} events, sleeping {FETCH_INTERVAL_SECONDS}s")
        except requests.RequestException as e:
            print("Error fetching DONKI:", e)
        except errors.PyMongoError as e:
            print("MongoDB connection error:", e)
            # try to reconnect next loop
            try:
                client = make_db_client()
                db = client.get_default_database() or client["donki"]
                coll = db["events"]
            except Exception as recon_e:
                print("Reconnection failed:", recon_e)
        except Exception as e:
            print("Unexpected error:", e)

        time.sleep(FETCH_INTERVAL_SECONDS)


if __name__ == "__main__":
    main_loop()