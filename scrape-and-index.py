# %%
import stealth_requests as requests
import requests as r
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from dotenv import load_dotenv
import os
import json
from tqdm import tqdm
from time import sleep
import base64
load_dotenv()

# %%
lightrag_url = os.getenv('LIGHTRAG_URL', 'http://localhost:9621')

with open('data/urls.txt', 'r') as f:
    page_urls = [line.strip() for line in f if line.strip()]

with open('data/pdfs.txt', 'r') as f:
    pdf_urls = [line.strip() for line in f if line.strip()]

# %%
def scrape_content(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'html.parser')

    # Find the 'div' with class 'content-wrap'
    content_wrap_div = soup.find('div', class_='content-wrap')

    # Get the HTML content of this div
    if content_wrap_div:
        content_wrap_html = str(content_wrap_div)
        md_content = md(content_wrap_html)
        #print(md_content)
        return md_content
    else:
        print(f"Div with class 'content-wrap' not found in {url}")
        return None

def insert_page_to_rag(page):
    data = {
        "text": page["content"],
        "file_path": page["url"],
        "metadata": {
            "url": page["url"]
        },
        "source": "web"
    }
    resp = r.post(f"{lightrag_url}/documents/text", json=data)
    return resp.status_code

def insert_pdf_to_rag(pdf_url):
    resp = requests.get(pdf_url)
    if resp.status_code == 200:
        filename = pdf_url.split('/')[-1] or "file.pdf"
        files = {
            'file': (filename, resp.content, 'application/pdf')
        }
        headers = {
            'accept': 'application/json'
            # Do not set Content-Type, requests will set it for multipart/form-data
        }
        upload_resp = r.post(f"{lightrag_url}/documents/file", files=files, headers=headers)
        return upload_resp
    else:
        print(f"Failed to download PDF: {pdf_url}")
        return None


# %%
pdf_pbar = tqdm(pdf_urls)

for url in pdf_pbar:
    pdf_pbar.set_description(f"Processing PDF: {url}")
    status_code = insert_pdf_to_rag(url)
    if status_code.status_code == 200:
        pdf_pbar.set_description(f"Successfully inserted PDF: {url}")
    else:
        print(f"Failed to insert PDF: {url}, Status Code: {status_code.content}")
    sleep(0.5)  # Sleep to avoid overwhelming the server

# %%
url_pbar = tqdm(page_urls)

markdown_dicts = []
for url in url_pbar:
    url_pbar.set_description(f"Scraping {url}")
    content = scrape_content(url)
    if content:
        markdown_dicts.append({
            "url": url,
            "content": content
        })
    sleep(0.5)  # To avoid overwhelming the server



