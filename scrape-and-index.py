# %%
import stealth_requests as requests
import requests as r
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from dotenv import load_dotenv
import os
from tqdm import tqdm
from time import sleep

load_dotenv()
lightrag_url = os.getenv('LIGHTRAG_URL', 'http://localhost:9621')

with open('data/urls.txt') as f:
    page_urls = [line.strip() for line in f if line.strip()]
with open('data/pdfs.txt') as f:
    pdf_urls = [line.strip() for line in f if line.strip()]

def scrape_content(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')
        div = soup.find('div', class_='content-wrap')
        if div:
            return md(str(div))
        print(f"[WARN] 'content-wrap' not found: {url}")
    except Exception as e:
        print(f"[ERROR] Failed to scrape {url}: {e}")
    return None

def insert_page_to_rag(page):
    data = {
        "text": page["content"],
        "file_path": page["url"],
        "metadata": {"url": page["url"]},
        "source": "web"
    }
    try:
        resp = r.post(f"{lightrag_url}/documents/text", json=data, timeout=10)
        return resp.status_code
    except Exception as e:
        print(f"[ERROR] Failed to insert page: {page['url']}: {e}")
        return None

def insert_pdf_to_rag(pdf_url):
    try:
        resp = requests.get(pdf_url, timeout=20)
        resp.raise_for_status()
        filename = pdf_url.split('/')[-1] or "file.pdf"
        files = {'file': (filename, resp.content, 'application/pdf')}
        headers = {'accept': 'application/json'}
        upload_resp = r.post(f"{lightrag_url}/documents/file", files=files, headers=headers, timeout=30)
        return upload_resp.status_code, upload_resp.content
    except Exception as e:
        print(f"[ERROR] PDF {pdf_url}: {e}")
        return None, None


for url in tqdm(page_urls, desc="Pages"):
    content = scrape_content(url)
    if content:
        insert_page_to_rag({"url": url, "content": content})
    sleep(0.5)

for url in tqdm(pdf_urls, desc="PDFs"):
    status, content = insert_pdf_to_rag(url)
    if status == 200:
        print(f"[OK] PDF inserted: {url}")
    else:
        print(f"[FAIL] PDF: {url}, Status: {status}, Content: {content}")
    sleep(0.5)





