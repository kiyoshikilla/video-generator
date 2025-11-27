import requests 
from pathlib import Path


def download_video(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)

    print(f"Downloading: from {url} to {destination}")

    try:
        with requests.get(url, stream= True, timeout= 30) as r:
            r.raise_for_status()

            with open(destination, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)        
        return destination
    
    except Exception as e:
        print(f"Error downloading video from {url}: {e}")
        raise e