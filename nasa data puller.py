import requests
from datetime import datetime, timedelta, timezone

DONKI_FLR_URL = "https://api.nasa.gov/DONKI/FLR"
DONKI_CME_URL = "https://api.nasa.gov/DONKI/CME"
DONKI_GST_URL = "https://api.nasa.gov/DONKI/GST"
DONKI_IPS_URL = "https://api.nasa.gov/DONKI/IPS"

API_KEY = "dahNGdR4VeXrHHIC6d4b4s595lOFCADoWNIZUL16"


def get_last_day_range():
    """Return start and end date (UTC, YYYY-MM-DD) for the last 24 hours."""
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=3)
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


#this function just serves to get around the "start time" members having different names
def parse_time(event):
    time_str = event.get("beginTime") or event.get("startTime") or event.get("eventTime")
    if not time_str:
        return datetime.min
    try:
        return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min



def main():
    start_date, end_date = get_last_day_range()
    print(f"Fetching DONKI data from {start_date} to {end_date}...\n")

    try:
        
        flares = fetch_donki_data(DONKI_FLR_URL, start_date, end_date)
        cmes = fetch_donki_data(DONKI_CME_URL, start_date, end_date)
        gsts = fetch_donki_data(DONKI_GST_URL, start_date, end_date)
        shocks = fetch_donki_data(DONKI_IPS_URL, start_date, end_date)
        for flare in flares:
            flare["eventType"] = "FLR"
        for cme in cmes:
            cme["eventType"] = "CME"
        for gst in gsts:
            gst["eventType"] = "GST"
        for shock in shocks:
            shock["eventType"] = "IPS"        



        events = flares + cmes + gsts + shocks
        events.sort(key=parse_time, reverse=True)
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


        # Print both sets
        #print_solar_flares(flares)
        #print_cmes(cmes)

    except requests.RequestException as e:
        print(f"Error fetching data from NASA DONKI API: {e}")
    input("Type anything to exit.")

if __name__ == "__main__":
    main()