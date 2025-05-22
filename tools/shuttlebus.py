import requests
import json
from datetime import datetime
import re
from zoneinfo import ZoneInfo  # Python 3.9+


def get_shuttle_data(cut_off_seconds=120):
    """
    Fetches shuttle bus data from the specified URL, adds 'last_update' field (seconds since get_date),
    and filters out records older than cut_off_seconds. Uses Asia/Seoul timezone for accurate calculation.

    Args:
        cut_off_seconds (int): Maximum allowed seconds since last update. Defaults to 60.

    Returns:
        list: Filtered list of shuttle data with 'last_update' field.
        str: An error message if the request fails or the response is not valid JSON.
    """
    url = "http://route.hellobus.co.kr:8787/pub/routeView/skku/getSkkuLoc.aspx"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if ZoneInfo:
            tz = ZoneInfo("Asia/Seoul")
            now = datetime.now(tz)
        else:
            now = datetime.now()
        filtered = []
        for item in data:
            get_date_str = item.get("get_date", "")
            # Example: '2025-05-22 오전 8:53:44' or '2025-02-14 오전 8:46:36'
            # Convert to 24-hour format
            match = re.match(r"(\d{4}-\d{2}-\d{2}) (오전|오후) (\d{1,2}):(\d{2}):(\d{2})", get_date_str)
            if not match:
                item["last_update"] = None
                continue
            date_part, ampm, hour, minute, second = match.groups()
            hour = int(hour)
            if ampm == "오후" and hour != 12:
                hour += 12
            if ampm == "오전" and hour == 12:
                hour = 0
            dt = datetime.strptime(f"{date_part} {hour:02}:{minute}:{second}", "%Y-%m-%d %H:%M:%S")
            if ZoneInfo:
                dt = dt.replace(tzinfo=tz)
            last_update = (now - dt).total_seconds()
            item["last_update"] = int(last_update)
            if last_update <= cut_off_seconds:
                filtered.append(item)
        return filtered
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err} - Status Code: {response.status_code}"
    except requests.exceptions.ConnectionError as conn_err:
        return f"Error connecting to the server: {conn_err}"
    except requests.exceptions.Timeout as timeout_err:
        return f"The request timed out: {timeout_err}"
    except requests.exceptions.RequestException as req_err:
        return f"An unexpected error occurred during the request: {req_err}"
    except json.JSONDecodeError:
        return f"Error decoding JSON. Response text: {response.text}"

if __name__ == "__main__":
    import sys
    cut_off = 60
    if len(sys.argv) > 1:
        try:
            cut_off = int(sys.argv[1])
        except ValueError:
            print("Invalid cut_off_seconds argument, using default 60.")
    data_or_error = get_shuttle_data(cut_off)
    if isinstance(data_or_error, str):
        print(f"Error: {data_or_error}")
    elif data_or_error is None:
        print("Received no data and no specific error message.")
    else:
        print("Successfully fetched shuttle data:")
        for item in data_or_error:
            print(item)
