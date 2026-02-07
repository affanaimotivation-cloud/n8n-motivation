import os
import requests
import io
import random
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Configuration (Secrets)
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    try:
        # Long Caption aur 15+ Hashtags ke liye instruction
        prompt = "Write 1 powerful motivational quote in HINDI. Then write a 5-line inspirational caption and 15 trending hashtags. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "ख्वाब वो नहीं जो नींद में आएं, ख्वाब वो हैं जो नींद उड़ा दें।", "Stay Focused!", "#motivation #success #hindi"

def get_image_safe():
    # Retry mechanism taaki UnidentifiedImageError na aaye
    for i in range(3):
        try:
            seed = random.randint(1, 999999)
            url = f"https://pollinations.ai/p/dark-nature-mountain-motivation-background?width=1080&height=1080&seed={seed}"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
        except:
            print(f"Attempt {i+1} failed. Retrying...")
            time.sleep(5)
    
    # Fallback: Agar generator fail ho toh solid color background banaye
    print("Using fallback background...")
    return Image.new('RGB', (1080, 1080), color=(10, 10, 30))

def create_image(quote):
    img = get_image_safe()
    draw = ImageDraw.Draw(img)

    # 2. Hindi Font Fix (Boxes hatane ke liye Noto Sans download ho raha hai)
    try:
        # Noto Sans Hindi font download link
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"
        font_res = requests.get(font_url).content
        font = ImageFont.truetype(io.BytesIO(font_res), 120) # Bada Font Size
    except:
        print("Font download failed, using default...")
        font = ImageFont.load_default()

    # Text wrapping logic taaki font bada dikhe
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 12: 
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # 3. Drawing Text (Gold Color + Shadow)
    y_text = 540 - (len(lines) * 80)
    for line in lines:
        draw.text((545, y_text + 5), line.strip(), fill=(0, 0, 0), font=font, anchor="mm") # Shadow
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm") # Gold Text
        y_text += 160
    
    # Handle add karna niche
    draw.text((540, 1020), "@affan.ai.motivation", fill=(200, 200, 200), anchor="mm")
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
        quote, caption, tags = get_content()
        full_text = f"{caption}\n\n.\n.\n{tags}"
        img = create_image(quote)
        post_to_fb(img, full_text)
        print("Post Success!")
    except Exception as e:
        print(f"Error: {e}")
