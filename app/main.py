from fastapi import FastAPI, Body
from models import VideoProcessingRequest

app = FastAPI()

@app.post("/process_media", status_code=202)
async def process_media(payload: VideoProcessingRequest):  
    pass
   

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    pass