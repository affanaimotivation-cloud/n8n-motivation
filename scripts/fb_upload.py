import os
import requests

GRAPH_VERSION = "v24.0"


def upload_video(video_path, caption=""):
    """
    Upload video as Facebook Reel
    """

    PAGE_ID = os.getenv("FB_PAGE_ID")
    PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

    if not PAGE_ID or not PAGE_TOKEN:
        raise ValueError("FB_PAGE_ID ya FB_PAGE_TOKEN missing hai")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size = os.path.getsize(video_path)

    if file_size < 1000:
        raise ValueError("Video file invalid ya bahut choti hai")

    print("Uploading File Size:", file_size)

    # =====================================
    # STEP 1️⃣ START PHASE
    # =====================================
    start_url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PAGE_ID}/video_reels"

    start_payload = {
        "access_token": PAGE_TOKEN,
        "upload_phase": "start",
        "file_size": file_size
    }

    start_res = requests.post(start_url, data=start_payload)
    start_json = start_res.json()

    print("START STATUS:", start_res.status_code)
    print("START RESPONSE:", start_json)

    if start_res.status_code != 200 or "video_id" not in start_json:
        raise Exception(f"Upload start failed: {start_json}")

    video_id = start_json["video_id"]
    upload_url = start_json["upload_url"]

    # =====================================
    # STEP 2️⃣ TRANSFER PHASE
    # =====================================
    headers = {
        "Authorization": f"OAuth {PAGE_TOKEN}",
        "Offset": "0",
        "Content-Type": "application/octet-stream"
    }

    with open(video_path, "rb") as video_file:
        transfer_res = requests.post(
            upload_url,
            headers=headers,
            data=video_file
        )

    print("TRANSFER STATUS:", transfer_res.status_code)
    print("TRANSFER RESPONSE:", transfer_res.text)

    if transfer_res.status_code not in (200, 201):
        raise Exception("Video transfer failed")

    # =====================================
    # STEP 3️⃣ FINISH PHASE
    # =====================================
    finish_payload = {
        "access_token": PAGE_TOKEN,
        "upload_phase": "finish",
        "video_id": video_id,
        "description": caption,
        "video_state": "PUBLISHED"
    }

    finish_res = requests.post(start_url, data=finish_payload)
    finish_json = finish_res.json()

    print("FINISH STATUS:", finish_res.status_code)
    print("FINISH RESPONSE:", finish_json)

    if finish_res.status_code != 200:
        raise Exception(f"Finish failed: {finish_json}")

    print("✅ Reel Successfully Uploaded!")
    return finish_json
