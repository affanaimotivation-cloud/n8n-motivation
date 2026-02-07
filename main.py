import os
import requests
import io
import random
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config (Using your Secret names)
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# 2. Setup Gemini (Fixed 404 Model Error)
genai.configure(api_key=GEMINI_KEY)
# 'gemini-1.5-flash' ki jagah 'gemini-1.5-flash-latest' ya 'gemini-pro' use karein
model = genai.GenerativeModel('gemini-1.5-flash-latest') 

def get_content():
    try:
        prompt = "Write 1 powerful motivational quote in HINDI. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        q = parts[0].strip() if len(parts) > 0 else "संघर्ष ही सफलता की कुंजी है।"
        c = parts[1].strip() if len(parts) > 1 else "Keep Pushing!"
        t = parts[2].strip() if len(parts) > 2 else "#motivation #hindi #success"
        return q, c, t
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "ख्वाब बड़े देखो, मेहनत भी बड़ी करो।", "Stay Focused!", "#hindi #motivation"

def create_image(quote):
    # Retry logic for image tool
    for i in range(3):
        try:
            seed = random.randint(1, 1000000)
            url = f"https://image.pollinations.ai/prompt/dark-minimalist-nature-background?width=1080&height=1080&nologo=true&seed={seed}"
            img_data = requests.get(url, timeout=20).content
            img = Image.open(io.BytesIO(img_data))
            break
        except:
            time.sleep(2)
            if i == 2: raise Exception("Image Generator Down")

    draw = ImageDraw.Draw(img)

    # 3. Hindi Font (Bada aur saaf)
    try:
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"
        font_res = requests.get(font_url).content
        font = ImageFont.truetype(io.BytesIO(font_res), 110) # Bada Size
    except:
        font = ImageFont.load_default()

    # Text wrapping logic
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 18:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # Drawing Text with Shadow (Premium Look)
    y_text = 540 - (len(lines) * 60)
    for line in lines:
        # Shadow
        draw.text((543, y_text + 3), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        # Gold/Yellow Color
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 130
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
        post_to_fb(img, f"{c}\n\n{t}")
        print("Workflow Completed Successfully!")
    except Exception as e:
        print(f"Final Error: {e}")
