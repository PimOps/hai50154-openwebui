"""
title: Shuttle Bus Information
author: AI Assistant
description: Provides the latest shuttle bus location data.
requirements: requests
version: 0.1.0
licence: MIT
"""
import json
from typing import Union, List, Dict, Any
import requests
from datetime import datetime
import re
import asyncio
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    ZoneInfo = None

# Try to import Open WebUI event helpers
try:
    from openwebui.helpers import __event_emitter__
except ImportError:
    __event_emitter__ = None

def get_shuttle_data(cut_off_seconds=240):
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

class Tools:
    def __init__(self):
        """Initialize the Tool."""
        pass

    async def get_latest_shuttle_info(self, cut_off_seconds: int = 60) -> str:
        """
        Fetches the latest shuttle bus location data, filtered by cut_off_seconds.

        Args:
            cut_off_seconds (int): Maximum allowed seconds since last update. Defaults to 60.

        Returns:
            str: A JSON string representing the list of shuttle bus data if successful,
                 or an error message string if the request fails or data is invalid.
        """
        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {
                    "description": "Fetching shuttle bus data...",
                    "done": False,
                    "hidden": False,
                },
            })
        data_or_error = get_shuttle_data(cut_off_seconds)
        if isinstance(data_or_error, str):
            if __event_emitter__:
                await __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": f"Error: {data_or_error}",
                        "done": True,
                        "hidden": False,
                    },
                })
                await __event_emitter__({
                    "type": "notification",
                    "data": {
                        "type": "error",
                        "content": data_or_error,
                    },
                })
            return data_or_error
        elif isinstance(data_or_error, list):
            try:
                result = json.dumps(data_or_error, ensure_ascii=False)
                if __event_emitter__:
                    await __event_emitter__({
                        "type": "status",
                        "data": {
                            "description": "Shuttle bus data fetched successfully.",
                            "done": True,
                            "hidden": False,
                        },
                    })
                    await __event_emitter__({
                        "type": "notification",
                        "data": {
                            "type": "success",
                            "content": "Shuttle bus data fetched successfully!",
                        },
                    })
                return result
            except TypeError as e:
                error_msg = f"Error serializing shuttle data to JSON: {str(e)}"
                if __event_emitter__:
                    await __event_emitter__({
                        "type": "status",
                        "data": {
                            "description": error_msg,
                            "done": True,
                            "hidden": False,
                        },
                    })
                    await __event_emitter__({
                        "type": "notification",
                        "data": {
                            "type": "error",
                            "content": error_msg,
                        },
                    })
                return error_msg
        else:
            error_msg = "Received unexpected data type from shuttle service."
            if __event_emitter__:
                await __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": error_msg,
                        "done": True,
                        "hidden": False,
                    },
                })
                await __event_emitter__({
                    "type": "notification",
                    "data": {
                        "type": "error",
                        "content": error_msg,
                    },
                })
            return error_msg

# For backward compatibility, provide a sync wrapper
    def get_latest_shuttle_info_sync(self, cut_off_seconds: int = 60) -> str:
        return asyncio.run(self.get_latest_shuttle_info(cut_off_seconds))

if __name__ == "__main__":
    import sys
    cut_off = 60
    if len(sys.argv) > 1:
        try:
            cut_off = int(sys.argv[1])
        except ValueError:
            print("Invalid cut_off_seconds argument, using default 60.")
    tool_instance = Tools()
    shuttle_info = tool_instance.get_latest_shuttle_info_sync(cut_off)
    print("Shuttle Information:")
    # Try to pretty-print if it's JSON
    try:
        parsed_json = json.loads(shuttle_info)
        print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(shuttle_info)

"""
Test with:
python -m tools.shuttlebus_tool
"""
