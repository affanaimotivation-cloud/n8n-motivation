import os, requests, io, random, json, time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config - Stable Model Connection
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

# Trending Tags Fix
FIXED_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_content():
    # Model name updated to 'gemini-1.5-flash-latest' for 404 fix
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    # Unique seed for every request to stop repetition
    unique_seed = f"User-{random.randint(1000, 9999)}-Time-{time.time()}"
    
    try:
        # Negative prompting to block old quotes
        prompt = (f"Seed: {unique_seed}. Task: Write a unique 2-line savage Hindi attitude quote. "
                  "STRICT: No 'Mehnat', 'Pehchaan', 'Andaz', 'Barabari', 'Duniya'. "
                  "Use deep words like 'Sultanat', 'Riyasat', 'Takht', 'Junoon'. "
                  "Return ONLY JSON: {\"quote\": \"...\", \"caption\": \"...\"}")
        
        response = model.generate_content(prompt, generation_config={"temperature": 1.0})
        # Clean JSON parsing
        data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return data['quote'], data['caption']
    except Exception as e:
        print(f"Model Error: {e}")
        return None, None

def create_image(quote):
    # Random High-Quality Image
    img = Image.open(io.BytesIO(requests.get(f"https://picsum.photos/1080/1080?random={random.random()}").content))
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 185)) 
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        # Balanced font size for all screens
        font = ImageFont.truetype("hindifont.ttf", 78)
        w_font = ImageFont.truetype("hindifont.ttf", 95) 
    except:
        font = w_font = ImageFont.load_default()

    # Smart line wrapping (Max 18 chars)
    words = quote.split()
    lines, current = [], ""
    for w in words:
        if len(current + w) < 19: current += w + " "
        else:
            lines.append(current.strip())
            current = w + " "
    lines.append(current.strip())

    # Vertical Centering logic
    y = (1080 - (len(lines) * 115)) // 2 
    for line in lines:
        draw.text((543, y + 3), line, fill=(0, 0, 0), font=font, anchor="mm") # Shadow
        draw.text((540, y), line, fill=(255, 215, 0), font=font, anchor="mm") # Gold Text
        y += 115
    
    # Large Watermark
    draw.text((540, 1010), "@affan.ai.motivation", fill=(255, 255, 255, 180), font=w_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c = get_content()
    
    if q and c:
        full_cap = f"{c}\n\n👉 Follow: @affan.ai.motivation\n\n.\n.\n{FIXED_TAGS}"
        img = create_image(q)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=95)
        
        # Facebook API Upload
        requests.post(f"https://graph.facebook.com/{FB_PAGE_ID}/photos", 
                      data={'message': full_cap, 'access_token': FB_ACCESS_TOKEN}, 
                      files={'source': buf.getvalue()})
        print("Success: Post Uploaded with New Model!")
    else:
        print("Error: Model 404 or Content Failed. Check API Key/Model Name.")
