import requests
import os

PAGE_ID = os.getenv("FB_PAGE_ID")
TOKEN = os.getenv("FB_PAGE_TOKEN")

def upload_video(video, audio, subtitle):
    url = f"https://graph.facebook.com/{PAGE_ID}/videos"

    files = {
        "file": open(video, "rb")
    }

    data = {
        "access_token": TOKEN,
        "description": "Follow for more @affan.ai.motivation"
    }

    requests.post(url, files=files, data=data)
