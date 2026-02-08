import os
import requests
import io
import random
import json
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)

def get_content():
    # Diversified topics to prevent repetition
    topics = ["Elite Athlete Discipline", "Deep Focus", "Financial Freedom", "Stoic Wisdom", "Success through Failure"]
    chosen = random.choice(topics)
    # Adding timestamp for total uniqueness
    timestamp = time.time()
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        # Strict instruction for JSON format and 15 tags
        prompt = (
            f"Current Timestamp: {timestamp}. Topic: {chosen}. "
            "Task: Write a brand new Hindi motivational quote. "
            "Write a fresh 10-line caption. Provide 15 viral hashtags. "
            "Return ONLY as JSON: {\"quote\": \"...\", \"caption\": \"...\", \"tags\": \"#...\"}"
        )
        response = model.generate_content(prompt)
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_text)
        return data['quote'], data['caption'], data['tags']
    except:
        return "ख्वाबों के लिए मेहनत करो।", "Utho aur jeeto!", "#motivation #viral #success"

def get_premium_image():
    try:
        # Using a very high seed to ensure different images
        seed = random.randint(1, 99999)
        url = f"https://picsum.photos/1080/1080?random={seed}"
        res = requests.get(url, timeout=30)
        return Image.open(io.BytesIO(res.content))
    except:
        return Image.new('RGB', (1080, 1080), color=(10, 15, 25))

def create_image(quote):
    img = get_premium_image()
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 175)) 
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        # Font settings
        font = ImageFont.truetype("hindifont.ttf", 110)
        # Bada Watermark Size 100 for better visibility
        watermark_font = ImageFont.truetype("hindifont.ttf", 100) 
    except:
        font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    # Wrap logic
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
    
    # Large Clear Watermark
    draw.text((540, 1000), "@affan.ai.motivation", fill=(255, 255, 255, 220), font=watermark_font, anchor="mm")
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
    # Fixed Follow-handle and Tags logic
    full_caption = f"{c}\n\n👉 Follow for more: @affan.ai.motivation\n\n.\n.\n{t}"
    img = create_image(q)
    post_to_fb(img, full_caption)
    print("Unique Post Success!")
