import os
import requests

GRAPH_VERSION = "v18.0"

def upload_video(video_path, caption=""):
    PAGE_ID = os.getenv("FB_PAGE_ID")
    PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

    if not PAGE_ID or not PAGE_TOKEN:
        raise ValueError("FB_PAGE_ID ya FB_PAGE_TOKEN missing hai")

    # फाइल को बाइट्स में पढ़ना (इससे Content-Length की समस्या खत्म हो जाती है)
    with open(video_path, "rb") as f:
        video_data = f.read()
    
    file_size = len(video_data)

    # STEP 1: START
    start_url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PAGE_ID}/video_reels"
    start_payload = {
        "access_token": PAGE_TOKEN,
        "upload_phase": "start",
        "file_size": file_size
    }
    
    start_res = requests.post(start_url, data=start_payload).json()
    print("START RESPONSE:", start_res)

    if "video_id" not in start_res:
        raise Exception(f"Start failed: {start_res}")

    video_id = start_res["video_id"]
    upload_url = start_res["upload_url"]

    # STEP 2: TRANSFER (यहाँ "Content-Length" हाथ से सेट किया गया है)
    headers = {
        "Authorization": f"OAuth {PAGE_TOKEN}",
        "Content-Type": "application/octet-stream",
        "Offset": "0",
        "Content-Length": str(file_size) # फेसबुक को साइज बताना अनिवार्य है
    }

    transfer_res = requests.post(upload_url, headers=headers, data=video_data)
    print("TRANSFER STATUS:", transfer_res.status_code)

    if transfer_res.status_code not in (200, 201):
        print("TRANSFER RESPONSE:", transfer_res.text)
        raise Exception("Video transfer failed")

    # STEP 3: FINISH
    finish_payload = {
        "access_token": PAGE_TOKEN,
        "upload_phase": "finish",
        "video_id": video_id,
        "description": caption
    }
    
    finish_res = requests.post(start_url, data=finish_payload).json()
    print("FINISH RESPONSE:", finish_res)
    return finish_res
