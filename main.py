import os
import requests
import io
import random
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Configuration
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    try:
        # Long caption aur 10+ hashtags ke liye instruction
        prompt = "Write 1 powerful motivational quote in HINDI. Then a long inspirational caption and 15 trending hashtags. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "ख्वाब वो नहीं जो नींद में आएं, ख्वाब वो हैं जो नींद उड़ दें।", "Keep Grinding!", "#motivation #success #hindi #tags #trending"

def get_image_with_retry():
    # 3 baar koshish karega agar image load nahi hui
    for i in range(3):
        try:
            seed = random.randint(1, 1000000)
            url = f"https://image.pollinations.ai/prompt/dark-mountain-professional-background?width=1080&height=1080&nologo=true&seed={seed}"
            res = requests.get(url, timeout=30)
            img = Image.open(io.BytesIO(res.content))
            return img
        except:
            print(f"Image retry {i+1}...")
            time.sleep(3)
    raise Exception("Pollinations AI not responding properly")

def create_image(quote):
    img = get_image_with_retry()
    draw = ImageDraw.Draw(img)

    # 2. Hindi Font Setup (Size 120 - Kafi Bada)
    try:
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"
        font_data = requests.get(font_url).content
        font = ImageFont.truetype(io.BytesIO(font_data), 120)
    except:
        font = ImageFont.load_default()

    # Text wrapping logic
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 15:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # Text Drawing with Shadow and Gold Color
    y_text = 540 - (len(lines) * 65)
    for line in lines:
        draw.text((545, y_text + 5), line.strip(), fill=(0, 0, 0), font=font, anchor="mm") # Shadow
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm") # Gold Text
        y_text += 140
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG', quality=95)
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    r = requests.post(url, data=payload, files=files)
    print("FB Response:", r.json())

if __name__ == "__main__":
    try:
        q, c, t = get_content()
        img = create_image(q)
        # Bada caption aur 10+ tags
        post_to_fb(img, f"{c}\n\n.\n.\n{t}")
        print("Successfully Posted!")
    except Exception as e:
        print(f"Error: {e}")
