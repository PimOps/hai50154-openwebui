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

# Remove the import of get_shuttle_data, and define the function directly here

def get_shuttle_data():
    """
    Fetches shuttle bus data from the specified URL.

    Returns:
        dict: The JSON data as a dictionary if successful.
        str: An error message if the request fails or the response is not valid JSON.
    """
    url = "http://route.hellobus.co.kr:8787/pub/routeView/skku/getSkkuLoc.aspx"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
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

    def get_latest_shuttle_info(self) -> str:
        """
        Fetches the latest shuttle bus location data.

        Returns:
            str: A JSON string representing the list of shuttle bus data if successful,
                 or an error message string if the request fails or data is invalid.
        """
        data_or_error = get_shuttle_data()

        if isinstance(data_or_error, str):
            # It's already an error message string
            return data_or_error
        elif isinstance(data_or_error, list):
            # It's the shuttle data (list of dictionaries)
            try:
                return json.dumps(data_or_error, ensure_ascii=False)
            except TypeError as e:
                return f"Error serializing shuttle data to JSON: {str(e)}"
        else:
            # Should not happen based on get_shuttle_data's current implementation
            return "Received unexpected data type from shuttle service."

if __name__ == "__main__":
    # Example usage of the tool (for testing purposes)
    tool_instance = Tools()
    shuttle_info = tool_instance.get_latest_shuttle_info()
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
