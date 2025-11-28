import aiohttp
import aiofiles
from pathlib import Path


async def download_video(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)

    print(f"Downloading: from {url} to {destination}")

    try:

        timeout = aiohttp.ClientTimeout(total=90)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as r:
                r.raise_for_status()

                async with aiofiles.open(destination, 'wb') as f:
                    async for chunk in r.content.iter_chunked(8192):
                        if chunk:
                            await f.write(chunk)        
        return destination
    
    except Exception as e:
        print(f"Error downloading video from {url}: {e}")
        raise e