import requests
import json

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
        
        # Attempt to parse JSON directly
        # The provided sample output is a list of dictionaries, not a single dictionary.
        # The problem description asks for "the JSON dictionary", which might imply
        # the user expects a single object or the raw list.
        # For now, returning the raw parsed JSON (which is a list)
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
        # It's helpful to see what the response was if it's not valid JSON
        return f"Error decoding JSON. Response text: {response.text}"

if __name__ == "__main__":
    data_or_error = get_shuttle_data()
    
    if isinstance(data_or_error, str):  # It's an error message
        print(f"Error: {data_or_error}")
    elif data_or_error is None: # Should not happen with current logic but good for robustness
        print("Received no data and no specific error message.")
    else: # It's the JSON data
        print("Successfully fetched shuttle data:")
        # The data is a list of dictionaries, print it as such
        # If you want to pretty-print, you can use json.dumps
        # print(json.dumps(data_or_error, indent=2, ensure_ascii=False))
        for item in data_or_error:
            print(item)
