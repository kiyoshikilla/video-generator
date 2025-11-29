import requests
from pathlib import Path

def download_video(url: str, dest_path: Path) -> bool:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.google.com/'
    }

    try:
        print(f"Downloading: {url}")
        
        with requests.get(url, stream=True, headers=headers, timeout=60) as r:
            r.raise_for_status() 
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=64 * 1024):
                    if chunk:
                        f.write(chunk)
                        
        print(f"Success: {dest_path.name}")
        return True

    except Exception as e:
        print(f"Download failed for {url}: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return False