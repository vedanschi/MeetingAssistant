# webhook_listener.py
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/calendly-webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    print(payload)
    
    event_type = payload.get('event')
    if event_type == "invitee.created":
        # extract start time, save it, schedule recording
        print("Meeting Scheduled:", payload['payload']['event']['start_time'])
    
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("webhook_listener:app", host="0.0.0.0", port=8000)
