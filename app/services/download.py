import requests
import time
import os

# Створи папку якщо немає
os.makedirs("downloads", exist_ok=True)

def download_file_safely(url, filepath):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Downloading {url}...")
        with requests.get(url, stream=True, headers=headers, timeout=30) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Success: {filepath}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False