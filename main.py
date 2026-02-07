import os
import requests
import io
import random
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# 2. Setup Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    try:
        prompt = "Write 1 short powerful motivational quote. Just the text, no quotes or intro."
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '')
    except:
        return "Your limitation—it's only your imagination."

def create_image(quote):
    # Try multiple times if image fails
    for i in range(3):
        try:
            seed = random.randint(1, 999999)
            img_url = f"https://image.pollinations.ai/prompt/professional-dark-motivation-background?width=1080&height=1080&nologo=true&seed={seed}"
            
            response = requests.get(img_url, timeout=30)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                draw = ImageDraw.Draw(img)
                # Drawing text in center
                draw.text((540, 540), quote, fill=(255, 255, 255), anchor="mm")
                return img
        except Exception as e:
            print(f"Image attempt {i+1} failed: {e}")
            time.sleep(2) # Wait 2 seconds before retry
    return None

def post_to_fb(image_obj, message):
    if image_obj is None:
        print("Error: No image to post.")
        return
        
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG', quality=90)
    
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    
    r = requests.post(url, data=payload, files=files)
    print("FB Response:", r.json())

if __name__ == "__main__":
    try:
        q = get_content()
        print(f"Quote: {q}")
        img = create_image(q)
        if img:
            post_to_fb(img, q)
            print("Successfully executed!")
        else:
            print("Failed to generate image after retries.")
    except Exception as e:
        print(f"Critical Error: {e}")
