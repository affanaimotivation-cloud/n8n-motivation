import os
import requests

GRAPH_VERSION = "v18.0"

def upload_video(video_path, caption=""):
    PAGE_ID = os.getenv("FB_PAGE_ID")
    PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

    if not PAGE_ID or not PAGE_TOKEN:
        raise ValueError("FB_PAGE_ID ya FB_PAGE_TOKEN missing hai")

    file_size = os.path.getsize(video_path)

    # ---------------- STEP 1: START ----------------
    start_url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PAGE_ID}/video_reels"
    start_payload = {
        "access_token": PAGE_TOKEN,
        "upload_phase": "start",
        "file_size": file_size
    }

    start_res = requests.post(start_url, data=start_payload).json()
    print("START RESPONSE:", start_res)

    if "video_id" not in start_res:
        raise Exception("Upload start failed")

    video_id = start_res["video_id"]
    upload_url = start_res["upload_url"]

    # ---------------- STEP 2: TRANSFER ----------------
    with open(video_path, "rb") as f:
        transfer_headers = {
            "Authorization": f"OAuth {PAGE_TOKEN}",
            "file_offset": "0"
        }
        transfer_res = requests.post(upload_url, headers=transfer_headers, data=f)

    print("TRANSFER STATUS:", transfer_res.status_code)

    if transfer_res.status_code != 200:
        raise Exception("Video transfer failed")

    # ---------------- STEP 3: FINISH ----------------
    finish_payload = {
        "access_token": PAGE_TOKEN,
        "upload_phase": "finish",
        "video_id": video_id,
        "description": caption
    }

    finish_res = requests.post(start_url, data=finish_payload).json()
    print("FINISH RESPONSE:", finish_res)

    if "success" not in finish_res:
        raise Exception("Facebook upload failed")

    print("✅ REEL SUCCESSFULLY POSTED")
