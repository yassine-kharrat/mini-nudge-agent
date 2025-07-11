from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from typing import AsyncGenerator
from dotenv import load_dotenv
from nudger.ingestion import load_crm_data, load_email_threads
from nudger.reasoning import generate_nudges

load_dotenv()

app = FastAPI(title="Nudge Generator API", description="Streams sales nudges based on CRM data")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Nudge Generator API - Use /nudges to stream nudges or /test for the web interface"}

@app.get("/test")
async def test_page():
    """Serve the test HTML page"""
    return FileResponse("static/index.html")

@app.get("/nudges")
async def stream_nudges() -> StreamingResponse:
    """
    Stream JSON nudges as they are generated.
    Returns a streaming response with each nudge as a JSON object.
    """
    
    async def generate_nudges_stream() -> AsyncGenerator[str, None]:
        # Load data
        crm_data = load_crm_data("data/crm_events.csv")
        email_data = load_email_threads("data/emails.json")
        
        # Generate nudges
        nudges = generate_nudges(crm_data, email_data)
        
        # Stream each nudge as JSON
        for nudge in nudges:
            yield f"data: {json.dumps(nudge, default=str)}\n\n"
            await asyncio.sleep(0.1)  # Small delay for streaming effect
        
        # Send end signal
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_nudges_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 