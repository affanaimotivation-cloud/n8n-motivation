import os
import requests
import io
import random
import google.generativeai as genai  # Yeh sahi tareeka hai import karne ka
from PIL import Image, ImageDraw, ImageFont

# 1. Config
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    try:
        # Gemini ko clear instruction: Bada caption aur 15 tags
        prompt = "Write 1 powerful motivational quote in HINDI. Then write a 5-line inspirational caption and 15 trending hashtags. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "ख्वाब वो नहीं जो नींद में आएं, ख्वाब वो हैं जो नींद उड़ दें।", "Keep Pushing!", "#motivation #success #hindi #tags"

def create_image(quote):
    seed = random.randint(1, 1000000)
    # Wahi stable URL jo pehle kaam kar raha tha
    url = f"https://image.pollinations.ai/prompt/dark-minimalist-background?width=1080&height=1080&nologo=true&seed={seed}"
    img = Image.open(io.BytesIO(requests.get(url).content))
    draw = ImageDraw.Draw(img)

    # 2. Hindi Font Setup (Extra Large Size: 120)
    try:
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"
        font_res = requests.get(font_url).content
        font = ImageFont.truetype(io.BytesIO(font_res), 120)
    except:
        font = ImageFont.load_default()

    # Text wrapping taaki bada font screen se bahar na jaye
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 12:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # 3. Drawing Text (Gold Color + Dark Shadow)
    y_text = 540 - (len(lines) * 75)
    for line in lines:
        # Shadow
        draw.text((544, y_text + 4), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        # Main Gold Text
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 160
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
    q, c, t = get_content()
    # Caption, Gap aur Hashtags ko jodan
    full_text = f"{c}\n\n.\n.\n{t}"
    print(f"Generating for: {q}")
    img = create_image(q)
    post_to_fb(img, full_text)
