import requests
import json

def upload_document_for_rag(api_url: str, token: str, text: str, source_url: str) -> dict:
    """
    Uploads a document for RAG (Retrieval-Augmented Generation) to the specified Open WebUI host.

    Args:
        api_url (str): The base URL of your Open WebUI host (e.g., 'http://localhost:8080').
        token (str): Your Bearer token for authentication.
        text (str): The document text to upload.
        source_url (str): The source URL for the document metadata.

    Returns:
        dict: The JSON response from the server.
    """
    url = f"{api_url.rstrip('/')}/api/rag/upload"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "documents": [
            {
                "text": text,
                "metadata": {
                    "source_url": source_url
                }
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    # Example usage
    api_url = "http://localhost:8080/"  # Replace with your Open WebUI host
    token = "<YOUR_TOKEN>"  # Replace with your Bearer token
    text = "## My Markdown Content\n\nThis is an article..."
    source_url = "https://original-article-url.com"

    try:
        result = upload_document_for_rag(api_url, token, text, source_url)
        print("Upload successful. Server response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Upload failed: {e}")