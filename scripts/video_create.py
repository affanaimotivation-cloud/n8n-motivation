import requests

def create_video():
    url = "https://videos.pexels.com/video-files/856018/856018-hd_720_1280_25fps.mp4"
    r = requests.get(url)

    with open("output.mp4", "wb") as f:
        f.write(r.content)

    return "output.mp4"
