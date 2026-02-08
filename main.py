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
    # Topics list taaki variety bani rahe
    moods = ["Aggressive King Attitude", "Alpha Male Power", "Luxury Empire Wisdom", "Stoic Success", "Savage Comeback Quotes"]
    chosen_mood = random.choice(moods)
    
    # Model name fix: 'gemini-1.5-flash' ka upyog
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        # Instruction for unique content without repeating common words
        prompt = (
            f"Current Timestamp: {time.time()}. Topic: {chosen_mood}. "
            "Write a completely NEW 2-line aggressive Hindi attitude quote. "
            "STRICT RULE: Do NOT use the words: 'Mehnat', 'Hardwork', 'Pehchaan', 'Duniya', 'Sher', 'Khamoshi'. "
            "Use heavy words like: 'Sultanat', 'Dahshat', 'Kismat', 'Junoon', 'Tabahi', 'Aukaat'. "
            "Return ONLY a clean JSON object: {\"quote\": \"...\", \"caption\": \"...\"}"
        )
        
        # Generation config ko simple rakha taaki 404 na aaye
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.9,
                top_p=1.0,
                max_output_tokens=500,
            )
        )
        
        # JSON parsing logic
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_text)
        return data['quote'], data['caption']
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None, None

def create_image(quote):
    # Stable image background
    url = f"https://picsum.photos/1080/1080?random={random.randint(1,100000)}"
    res = requests.get(url, timeout=30)
    img = Image.open(io.BytesIO(res.content))
    
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 185)) 
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("hindifont.ttf", 112)
        # Bada watermark
        watermark_font = ImageFont.truetype("hindifont.ttf", 80) 
    except:
        font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    # Wrap quote text
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
    
    # Large watermark placement
    draw.text((540, 1010), "@affan.ai.motivation", (255, 255, 255, 215), font=watermark_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c = get_content()
    
    if q and c:
        # Caption with follow link and fixed tags
        full_caption = f"{c}\n\n👉 Follow for more: @affan.ai.motivation\n\n.\n.\n{DEFAULT_TAGS}"
        
        img = create_image(q)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=95)
        
        # Facebook Post
        url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
        payload = {'message': full_caption, 'access_token': FB_ACCESS_TOKEN}
        files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
        requests.post(url, data=payload, files=files)
        print("Success: Post with Unique Content Live!")
    else:
        print("Skipping post: Model generation failed.")
