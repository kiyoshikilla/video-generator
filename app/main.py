from fastapi import FastAPI, Body
from app.models import VideoProcessingRequest
from celery.result import AsyncResult
from app.tasks import process_video

app = FastAPI()

@app.post("/process_media", status_code=202)
async def process_media(payload: VideoProcessingRequest):  
    
    task_payload = payload.model_dump(mode='json')

    task = process_video.delay(task_payload)
   
    return {
        "task_id": task.id,
        "status": "in queue",
        "message": "Successfully submitted",
    }

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    
    task_result = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": None,
    }

    if task_result.ready():
        response["status"] = task_result.result
    
    return response 