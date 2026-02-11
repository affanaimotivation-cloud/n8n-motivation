import os
import requests

# हमने एरर के हिसाब से वर्शन v24.0 सेट कर दिया है
GRAPH_VERSION = "v24.0" 

def upload_video(video_path, caption=""):
    PAGE_ID = os.getenv("FB_PAGE_ID")
    PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")

    if not PAGE_ID or not PAGE_TOKEN:
        raise ValueError("FB_PAGE_ID ya FB_PAGE_TOKEN missing hai")

    # फाइल का साइज निकालें
    file_size = os.path.getsize(video_path)

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
        raise Exception(f"Upload start failed: {start_res}")

    video_id = start_res["video_id"]
    upload_url = start_res["upload_url"]

    # STEP 2: TRANSFER (यहाँ असली जादू है)
    # हम फाइल को सीधा 'data=f' के बजाय 'f.read()' करके बाइट्स में भेजेंगे
    with open(video_path, "rb") as f:
        video_data = f.read()

    headers = {
        "Authorization": f"OAuth {PAGE_TOKEN}",
        "Offset": "0",
        "Content-Type": "application/octet-stream",
        "Content-Length": str(len(video_data)) # फेसबुक की डिमांड पूरी
    }

    # 'data=video_data' भेजने से पायथन Content-Length को डिलीट नहीं कर पाता
    transfer_res = requests.post(upload_url, headers=headers, data=video_data)
    
    print(f"TRANSFER STATUS: {transfer_res.status_code}")
    if transfer_res.status_code not in (200, 201):
        print("TRANSFER RESPONSE:", transfer_res.text)
        raise Exception("Video transfer failed")

    # STEP 3: FINISH
    finish_payload = {
        "access_token": PAGE_TOKEN,
        "upload_phase": "finish",
        "video_id": video_id,
        "description": caption,
        "video_state": "PUBLISHED"
    }
    
    finish_res = requests.post(start_url, data=finish_payload).json()
    print("FINISH RESPONSE:", finish_res)
    return finish_res
