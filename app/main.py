from fastapi import FastAPI, Body

app = FastAPI()

@app.post("/process_media")
async def process_media(
    video_blocks: str = Body(embed=True),
):
    
    return {'data': '1'}