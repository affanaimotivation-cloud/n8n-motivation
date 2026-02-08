import os
import requests
import io
import random
import json
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Configuration
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
# Temperature 0.9 taaki content repeat na ho aur creative aaye
model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.9})

def get_content():
    # Diversified Categories: Ab sirf 'mehnat' nahi aayega
    categories = [
        "Financial Freedom & Luxury", 
        "Stoic Silence & Power", 
        "Betrayal & Rising Alone", 
        "King Mindset & Respect",
        "Time Management & Focus",
        "Winning against Odds"
    ]
    chosen = random.choice(categories)
    
    try:
        # Prompt ko strict kiya taaki JSON hi mile
        prompt = (
            f"Write a savage and unique Hindi quote about {chosen}. "
            "Do not use the word 'Mehnat' or 'Hard work' if possible. Use deep words. "
            "Return ONLY a JSON object: {\"quote\": \"...\", \"caption\": \"...\", \"tags\": \"#...\"} "
            "Make sure you provide exactly 15 viral hashtags."
        )
        response = model.generate_content(prompt)
        data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return data['quote'], data['caption'], data['tags']
    except:
        return "शेर खामोश रहे तो इसका मतलब ये नहीं कि वो शिकार करना भूल गया।", "Rise like a king.", "#mindset #power #success #luxury #motivation"

def get_premium_image():
    # Har baar unique seed taaki image badalti rahe
    url = f"https://picsum.photos/1080/1080?random={random.randint(1,9999)}"
    res = requests.get(url, timeout=30)
    return Image.open(io.BytesIO(res.content))

def create_image(quote):
    img = get_premium_image()
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 175)) 
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        # Bada Watermark (Size 100)
        font = ImageFont.truetype("hindifont.ttf", 115)
        watermark_font = ImageFont.truetype("hindifont.ttf", 80) 
    except:
        font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    # Text wrapping logic
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 14: current_line += word + " "
        else:
            lines.append(current_line); current_line = word + " "
    lines.append(current_line)

    y_text = 540 - (len(lines) * 95)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), (0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), (255, 215, 0), font=font, anchor="mm")
        y_text += 190
    
    # Large Watermark
    draw.text((540, 1010), "@affan.ai.motivation", (255, 255, 255, 220), font=watermark_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c, t = get_content()
    # Adding follow handle in caption
    full_caption = f"{c}\n\n👉 Follow for more: @affan.ai.motivation\n\n.\n.\n{t}"
    
    img = create_image(q)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=95)
    
    # Posting logic
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': full_caption, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    requests.post(url, data=payload, files=files)
    print("Unique Content Posted!")
