import requests
import time
import os
import certifi
import dotenv
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient, errors
from pymongo.errors import BulkWriteError

dotenv.load_dotenv()

API_KEY = os.environ.get("NASA_DONKI_API")  if os.environ.get("NASA_DONKI_API") else dotenv.get_key('.env', 'NASA_DONKI_API')
MONGO_URI = os.environ.get("MONGO_URI") if os.environ.get("MONGO_URI") else dotenv.get_key('.env', 'MONGO_URI')
FETCH_INTERVAL_SECONDS = int(os.environ.get("DONKI_FETCH_INTERVAL", "600")) 


DONKI_FLR_URL = "https://api.nasa.gov/DONKI/FLR"
DONKI_CME_URL = "https://api.nasa.gov/DONKI/CME"
DONKI_GST_URL = "https://api.nasa.gov/DONKI/GST"
DONKI_IPS_URL = "https://api.nasa.gov/DONKI/IPS"
DONKI_MPC_URL = "https://api.nasa.gov/DONKI/MPC"



def get_last_day_range():
    """Return start and end date (UTC, YYYY-MM-DD) for the last 24 hours."""
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=2)
    return yesterday.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")


def fetch_donki_data(url, start_date, end_date):
    """Fetch data from a DONKI endpoint for a given date range."""
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "api_key": API_KEY,
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def get_unique_id_for_event(event):
    for key in ("flrID", "activityID", "gstID", "eventID", "id", "mpcID"):
        val = event.get(key)
        if val:
            return str(val)
    

    # if it "somehow" fails to find a valid id it will fallback to using the link as the unique id
    # this should like, never happen tho
    if event.get("link"):
        return str(event["link"])
    return f"unknown-{parse_time(event).isoformat()}"


def print_flare(flare):
    print("SOLAR FLARE")
    print(f"ID: {flare.get('flrID', 'N/A')}")
    print(f"Class: {flare.get('classType', 'Unknown')}")
    print(f"Begin Time: {flare.get('beginTime', 'N/A')}")
    print(f"Peak Time: {flare.get('peakTime', 'N/A')}")
    print(f"Source Location: {flare.get('sourceLocation', 'N/A')}")
    print(f"Active Region: {flare.get('activeRegionNum', 'N/A')}")
    print(f"Link: {flare.get('link', 'N/A')}")
    print("-" * 60)
    print()


def print_cme(cme):
    print("CORONAL MASS EJECTION")
    print(f"ID: {cme.get('activityID', 'N/A')}")
    print(f"Start Time: {cme.get('startTime', 'N/A')}")
    print(f"Source Location: {cme.get('sourceLocation', 'N/A')}")
    print(f"Note: {cme.get('note', 'N/A')}")
    print(f"Link: {cme.get('link', 'N/A')}")
    print("-" * 60)
    print()

def print_gst(gst):
    print("GEOMAGNETIC STORM")
    print(f"ID: {gst.get('gstID', 'N/A')}")
    print(f"Start Time: {gst.get('startTime', 'N/A')}")
    print(f"Link: {gst.get('link', 'N/A')}")
    print("-" * 60)
    print()

def print_ips(ips):
    print("INTERPLANETARY SHOCK")
    print(f"ID: {ips.get('activityID', 'N/A')}")
    print(f"Start Time: {ips.get('eventTime', 'N/A')}")
    print(f"Location: {ips.get('location', 'N/A')}")
    print(f"Catalog: {ips.get('catalog', 'N/A')}")
    print(f"Link: {ips.get('link', 'N/A')}")
    print("-" * 60)
    print()

def print_mpc(mpc):
    print("MAGNETOPAUSE CROSSING")
    print(f"ID: {mpc.get('mpcID', 'N/A')}")
    print(f"Start Time: {mpc.get('eventTime', 'N/A')}")
    print(f"Link: {mpc.get('link', 'N/A')}")
    print("-" * 60)
    print()


def print_all_events(events):
    for event in events:
            match event["eventType"]:
                case 'FLR':
                    print_flare(event)
                case 'CME':
                    print_cme(event)
                case 'GST':
                    print_gst(event)
                case 'IPS':
                    print_ips(event)
                case 'MPC':
                    print_mpc(event)

def update_events(start_date, end_date):
    flares = fetch_donki_data(DONKI_FLR_URL, start_date, end_date)
    cmes = fetch_donki_data(DONKI_CME_URL, start_date, end_date)
    gsts = fetch_donki_data(DONKI_GST_URL, start_date, end_date)
    shocks = fetch_donki_data(DONKI_IPS_URL, start_date, end_date)
    mpcs = fetch_donki_data(DONKI_MPC_URL, start_date, end_date)
    for flare in flares:
        flare["eventType"] = "FLR"
    for cme in cmes:
        cme["eventType"] = "CME"
    for gst in gsts:
        gst["eventType"] = "GST"
    for shock in shocks:
        shock["eventType"] = "IPS"
    for mpc in mpcs:
        mpc["eventType"] = "MPC"   
    events = flares + cmes + gsts + shocks + mpcs
    events.sort(key=parse_time, reverse=True)
    return events


# this function just serves to get around the "start time" attributes having different names
def parse_time(event):
    time_str = event.get("beginTime") or event.get("startTime") or event.get("eventTime")
    if not time_str:
        return datetime.min
    try:
        return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min



def make_db_client():
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI environment variable not set")
    client = MongoClient(MONGO_URI, tlscafile=certifi.where(), serverSelectionTimeoutMS=5000)
    # test connection
    client.server_info()
    return client

def main():
    client = make_db_client()
    db = client["solarweather"]         
    collection = db["events"]

    collection.create_index("flrID", unique=True, sparse=True)
    collection.create_index("activityID", unique=True, sparse=True)
    collection.create_index("mpcID", unique=True, sparse=True)
    collection.create_index("gstID", unique=True, sparse=True)

    while True:
        start_date, end_date = get_last_day_range()
        print(f"Fetching DONKI data from {start_date} to {end_date}...\n")

        try:
            events = update_events(start_date, end_date)
            print_all_events(events)
            if events:
                try:
                    result = collection.insert_many(events, ordered=False)
                    print(f"Inserted {len(result.inserted_ids)} events.")
                except BulkWriteError as e:
                    inserted_count = e.details.get("nInserted", 0)
                    skipped_count = len(e.details.get("writeErrors", []))
                    print(f"Inserted {inserted_count} events, skipped {skipped_count} duplicates.")
            else:
                print("No events to insert.")
        except requests.RequestException as e:
            print(f"Error fetching data from NASA DONKI API: {e}")
        time.sleep(5*60)

if __name__ == "__main__":
    main()