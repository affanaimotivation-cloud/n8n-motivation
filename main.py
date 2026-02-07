import os
import requests
import io
import random
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    prompt = "Write 1 powerful short motivational quote in HINDI. Format: Quote | Caption | Tags"
    response = model.generate_content(prompt)
    parts = response.text.strip().split('|')
    return parts[0].strip(), parts[1].strip(), parts[2].strip()

def create_image(quote):
    seed = random.randint(1, 1000000)
    # Wahi Pollinations URL jo pehle success hua tha
    url = f"https://image.pollinations.ai/prompt/nature-galaxy-dark-background?width=1080&height=1080&nologo=true&seed={seed}"
    
    img_data = requests.get(url).content
    img = Image.open(io.BytesIO(img_data))
    draw = ImageDraw.Draw(img)

    # Font Setup (Hindi ke liye Noto Sans download ho raha hai)
    font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"
    font_res = requests.get(font_url).content
    font = ImageFont.truetype(io.BytesIO(font_res), 100) # Size bada kar diya hai

    # Drawing Text (Gold color with Shadow)
    draw.text((543, 543), quote, fill=(0, 0, 0), font=font, anchor="mm") # Shadow
    draw.text((540, 540), quote, fill=(255, 215, 0), font=font, anchor="mm") # Gold Text
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG')
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    data = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    requests.post(url, files=files, data=data)

if __name__ == "__main__":
    q, c, t = get_content()
    img = create_image(q)
    post_to_fb(img, f"{c}\n\n{t}")
    print("Post Successfully Done!")
