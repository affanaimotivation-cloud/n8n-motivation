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

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    topics = ["Empire Building", "Hard Work", "Success Habits", "Never Give Up"]
    chosen = random.choice(topics)
    try:
        # 10-15 hashtags only
        prompt = f"Write a deep Hindi motivational quote about {chosen}. Then write a 10-line Hindi caption and 12 trending hashtags. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "मेहनat इतनी खामोशी से करो कि सफलता शोर मचा दे।", "Keep working hard!", "#motivation #success"

def get_premium_image():
    # Naya stable URL format
    queries = ["fitness", "success", "luxury", "mountain", "galaxy", "office"]
    q = random.choice(queries)
    try:
        # Picsum sabse zyada stable hai aur kabhi None nahi deta
        url = f"https://picsum.photos/1080/1080?random={random.randint(1,1000)}"
        res = requests.get(url, timeout=30)
        return Image.open(io.BytesIO(res.content))
    except:
        # Agar net slow ho toh solid color background taaki crash na ho
        return Image.new('RGB', (1080, 1080), color=(15, 20, 35))

def create_image(quote):
    img = get_premium_image()
    # Image size check taaki crash na ho
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 165)) 
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("hindifont.ttf", 110)
        # Watermark size 85 (Bada aur saaf)
        watermark_font = ImageFont.truetype("hindifont.ttf", 85) 
    except:
        font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 14: current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    y_text = 540 - (len(lines) * 95)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 190
    
    # Bada Watermark
    draw.text((540, 1000), "@affan.ai.motivation", fill=(255, 255, 255, 200), font=watermark_font, anchor="mm")
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG', quality=95)
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    requests.post(url, data=payload, files=files)

if __name__ == "__main__":
    q, c, t = get_content()
    # Caption handle add kiya
    full_caption = f"{c}\n\n👉 Follow for more: @affan.ai.motivation\n\n.\n.\n{t}"
    img = create_image(q)
    post_to_fb(img, full_caption)
    print("Post Success!")
