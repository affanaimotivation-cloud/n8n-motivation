import requests
import os

def upload_video(video_path, caption=""):
    PAGE_ID = os.getenv("FB_PAGE_ID")
    PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

    if not PAGE_ID or not PAGE_TOKEN:
        raise ValueError("FB_PAGE_ID ya FB_PAGE_TOKEN missing hai")

    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/video_reels"

    data = {
        "access_token": PAGE_TOKEN,
        "description": caption
    }

    with open(video_path, "rb") as video:
        files = {
            "file": video
        }

        response = requests.post(url, data=data, files=files)

    # ✅ DEBUG OUTPUT (ab error nahi aayega)
    print("FB STATUS:", response.status_code)
    print("FB RESPONSE:", response.text)

    if response.status_code != 200:
        raise Exception("Facebook upload failed")

    return response.json()
