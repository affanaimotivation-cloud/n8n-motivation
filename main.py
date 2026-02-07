import os
import requests
import io
import random
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config (Secrets using your names)
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# 2. Setup Gemini (Free Version)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    try:
        # Strict prompt taaki koi faltu text na aaye
        prompt = "Write 1 powerful short motivational quote. Just the quote, no intro."
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '')
    except:
        return "Success is not final, failure is not fatal."

def create_image(quote):
    # Free Image Generator
    seed = random.randint(1, 999999)
    img_url = f"https://image.pollinations.ai/prompt/professional-nature-background?width=1080&height=1080&nologo=true&seed={seed}"
    img = Image.open(io.BytesIO(requests.get(img_url).content))
    draw = ImageDraw.Draw(img)
    # Default font size is small, but it works on every system
    draw.text((540, 540), quote, fill=(255, 255, 255), anchor="mm")
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG')
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    r = requests.post(url, data=payload, files=files)
    print("FB Response:", r.json())

if __name__ == "__main__":
    q = get_content()
    img = create_image(q)
    post_to_fb(img, q)
