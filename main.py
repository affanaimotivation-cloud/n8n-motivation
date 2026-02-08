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

# 2. Permanent Trending Hashtags
DEFAULT_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_content():
    # टॉपिक्स को बिल्कुल बदल दिया ताकि 'मेहनत' शब्द न आए
    moods = ["Aggressive King", "Alpha Male Motivation", "Stoic Power", "Rich Lifestyle Wisdom", "Savage Comeback"]
    chosen_mood = random.choice(moods)
    
    # Random temperature taaki har baar output alag ho
    temp = random.uniform(0.8, 1.0)
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": temp})
    
    try:
        # Gemini ko super-strict instructions
        prompt = (
            f"Current Time: {time.time()}. Mood: {chosen_mood}. "
            "Write a completely NEW 2-line aggressive Hindi attitude quote. "
            "NEVER use the words: 'Mehnat', 'Hardwork', 'Pehchaan', 'Duniya'. "
            "Use heavy words like: 'Hukumat', 'Dahshat', 'Kismat', 'Junoon', 'Aag'. "
            "Return ONLY JSON: {\"quote\": \"...\", \"caption\": \"...\"}"
        )
        response = model.generate_content(prompt)
        # JSON parsing logic
        data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return data['quote'], data['caption']
    except Exception as e:
        # Agar fail ho toh error dikhaye, purana content nahi
        print(f"Gemini Error: {e}")
        return None, None

def create_image(quote):
    # Background image logic
    url = f"https://picsum.photos/1080/1080?random={random.randint(1,100000)}"
    res = requests.get(url, timeout=30)
    img = Image.open(io.BytesIO(res.content))
    
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 180)) 
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("hindifont.ttf", 110)
        # Watermark size set to 110 for visibility
        watermark_font = ImageFont.truetype("hindifont.ttf", 70) 
    except:
        font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    # Quote wrapping
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 13: current_line += word + " "
        else: lines.append(current_line); current_line = word + " "
    lines.append(current_line)

    y_text = 540 - (len(lines) * 95)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), (0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), (255, 215, 0), font=font, anchor="mm")
        y_text += 190
    
    # Large watermark
    draw.text((540, 1010), "@affan.ai.motivation", (255, 255, 255, 215), font=watermark_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c = get_content()
    
    if q and c:
        # Permanent tags add logic
        full_caption = f"{c}\n\n👉 Follow for more: @affan.ai.motivation\n\n.\n.\n{DEFAULT_TAGS}"
        
        img = create_image(q)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=95)
        
        # Post to Facebook
        url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
        payload = {'message': full_caption, 'access_token': FB_ACCESS_TOKEN}
        files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
        requests.post(url, data=payload, files=files)
        print("Fresh Post Success!")
    else:
        print("Skipping post due to Gemini Error.")
