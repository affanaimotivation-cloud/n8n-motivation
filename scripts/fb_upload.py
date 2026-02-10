import os
import requests

GRAPH_VERSION = "v18.0"

def upload_video(video_path, caption=""):
    PAGE_ID = os.getenv("FB_PAGE_ID")
    PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

    if not PAGE_ID or not PAGE_TOKEN:
        raise ValueError("FB_PAGE_ID ya FB_PAGE_TOKEN missing hai")

    file_size = os.path.getsize(video_path)

    # ---------- STEP 1: START ----------
    start_url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PAGE_ID}/video_reels"
    start_payload = {
        "access_token": PAGE_TOKEN,
        "upload_phase": "start",
        "file_size": file_size
    }

    start_res = requests.post(start_url, data=start_payload).json()
    print("START RESPONSE:", start_res)

    if "video_id" not in start_res or "upload_url" not in start_res:
        raise Exception("Upload start failed")

    video_id = start_res["video_id"]
    upload_url = start_res["upload_url"]

    # bracket / markdown fix
    upload_url = upload_url.strip("[]")

    # ---------- STEP 2: TRANSFER ----------
    with
