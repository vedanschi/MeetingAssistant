# webhook_listener.py
from fastapi import FastAPI, Request
from my_package.scheduler import schedule_meeting_recording
import uvicorn

app = FastAPI()

@app.post("/calendly-webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    print(payload)

    event_type = payload.get('event')
    if event_type == "invitee.created":
        meeting_time = payload['payload']['event']['start_time']  # ISO 8601
        print("Meeting Scheduled at:", meeting_time)
        schedule_meeting_recording(meeting_time)

    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("webhook_listener:app", host="0.0.0.0", port=8000)
