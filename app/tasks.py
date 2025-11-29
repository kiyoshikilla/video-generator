import asyncio
import shutil
import tempfile
from pathlib import Path
from app.celery_app import app
from app.models import VideoProcessingRequest
from app.services.download import download_video
from app.services.elevenlabs import generate_tts
from app.services.video_constructor import create_video
from app.services.storage import get_storage
import traceback


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@app.task(bind=True)
def process_video(self, request_data: dict):
    
    try:
        request = VideoProcessingRequest(**request_data)
    except Exception as e:
        return {"status": "error", "message": f"Validation error: {e}"}

    
    task_id = self.request.id

    print(f"Staring task {task_id}: {request.task_name}")

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        videos_dir = temp_dir / "videos"
        audio_dir = temp_dir / "audios"
        tts_dir = temp_dir / "tts"
        output_dir = temp_dir / "output"


        videos_dir.mkdir(parents=True, exist_ok=True)
        audio_dir.mkdir(parents=True, exist_ok=True)
        tts_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        async def download_all_assets():
            download_tasks = []
            local_video_blocks = {}
            local_audio_blocks = {}

            for block_name, urls in request.video_blocks.items():
                local_video_blocks[block_name] = []
                for idx, url in enumerate(urls):
                    dest = videos_dir / block_name / f"video_{idx}.mp4"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    download_tasks.append(download_video(str(url), dest))
                    local_video_blocks[block_name].append(dest)

            for block_name, urls in request.audio_blocks.items():
                local_audio_blocks[block_name] = []
                for idx, url in enumerate(urls):
                    dest = audio_dir / block_name / f"audio_{idx}.mp3"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    download_tasks.append(download_video(str(url), dest))
                    local_audio_blocks[block_name].append(dest)
            
            await asyncio.gather(*download_tasks)
            return local_video_blocks, local_audio_blocks
        
        print("Downloading assets. Wait")
        try:
            video_paths, audio_path = run_async(download_all_assets())
        except Exception as e:
            return {"status": "error", "message": f"Download failed: {e}"}


        local_tts_files = []
        print("Generating text to speech")
        for item in request.text_to_speach:
            path = generate_tts(item.text, tts_dir, item.voice)
            if path:
                local_tts_files.append(path)

        
        print("Creating a video. Wait")
        try:
            results = create_video(
            video_blocks=video_paths,
            audio_blocks=audio_path,
            tts_files=local_tts_files,
            task_name=request.task_name,
            output_folder=output_dir,
        )
        except Exception as e:
            return {"status": "error", "message": f"Render failed: {e}"}
        

        storage_service = get_storage()
        final_path = []

        print(f"Saving to local + google drive")
        
        for temp_file in results:
            temp_path = Path(temp_file)
            if temp_path.exists():
                try:
                    public_link = storage_service.upload(temp_path, request.task_name)
                    final_path.append(public_link)
                except Exception as e:
                    print(f"[CRITICAL ERROR] GDrive upload failed for {temp_path.name}: {e}")
                    traceback.print_exc() 
                    final_path.append(str(temp_path.absolute()))
                    continue

        return {
            "status": "ok, completed",
            "task_id": task_id,
            "task_name": request.task_name,
            "generated_files": final_path,
            "count": len(results)
        }