import requests
from datetime import datetime, timedelta, timezone

DONKI_FLR_URL = "https://api.nasa.gov/DONKI/FLR"
DONKI_CME_URL = "https://api.nasa.gov/DONKI/CME"


API_KEY = "DEMO_KEY"


def get_last_day_range():
    """Return start and end date (UTC, YYYY-MM-DD) for the last 24 hours."""
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=5)
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


def print_solar_flares(flares):
    """Print formatted solar flare events."""
    if not flares:
        print("No solar flare events found in the past 24 hours.\n")
        return

    print(f"🔆 Found {len(flares)} Solar Flare Events:\n")
    for flare in flares:
        print(f"ID: {flare.get('flrID', 'N/A')}")
        print(f"Class: {flare.get('classType', 'Unknown')}")
        print(f"Begin Time: {flare.get('beginTime', 'N/A')}")
        print(f"Peak Time: {flare.get('peakTime', 'N/A')}")
        print(f"Source Location: {flare.get('sourceLocation', 'N/A')}")
        print(f"Active Region: {flare.get('activeRegionNum', 'N/A')}")
        print(f"Link: {flare.get('link', 'N/A')}")
        print("-" * 60)
    print()


def print_cmes(cmes):
    """Print formatted CME events."""
    if not cmes:
        print("No coronal mass ejection events found in the past 24 hours.\n")
        return

    print(f"🌪️ Found {len(cmes)} Coronal Mass Ejection Events:\n")
    for cme in cmes:
        print(f"ID: {cme.get('activityID', 'N/A')}")
        print(f"Start Time: {cme.get('startTime', 'N/A')}")
        print(f"Source Location: {cme.get('sourceLocation', 'N/A')}")
        print(f"Note: {cme.get('note', 'N/A')}")
        print(f"Link: {cme.get('link', 'N/A')}")
        print("-" * 60)
    print()


def main():
    start_date, end_date = get_last_day_range()
    print(f"Fetching DONKI data from {start_date} to {end_date}...\n")

    try:
        # Fetch solar flares
        flares = fetch_donki_data(DONKI_FLR_URL, start_date, end_date)
        # Fetch CMEs
        cmes = fetch_donki_data(DONKI_CME_URL, start_date, end_date)
        
        # Print both sets
        print_solar_flares(flares)
        print_cmes(cmes)

    except requests.RequestException as e:
        print(f"Error fetching data from NASA DONKI API: {e}")
    input("Type anything to exit.")

if __name__ == "__main__":
    main()