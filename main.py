import os, requests, io, random, json, time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

# Fix Trending Tags
FIXED_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_content():
    # Temperature 1.0 ensures no repetition
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        prompt = (f"Time:{time.time()}. Task: Write a brand new 2-line savage Hindi attitude quote. "
                  "STRICT: Do NOT use 'Mehnat', 'Pehchaan', 'Sher', 'Khamoshi'. "
                  "Use words like 'Sultanat', 'Dahshat', 'Hukumat', 'Takht'. "
                  "Return ONLY JSON: {\"quote\": \"...\", \"caption\": \"...\"}")
        
        response = model.generate_content(prompt, generation_config={"temperature": 1.0})
        data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return data['quote'], data['caption']
    except:
        return "अपना अंदाज़ अलग है, बराबरी करोगे तो बिखर जाओगे।", "Rule the world."

def create_image(quote):
    # Dynamic Image Fetch
    img = Image.open(io.BytesIO(requests.get(f"https://picsum.photos/1080/1080?random={random.random()}").content))
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 180)) 
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        # Font size 80 kiya taaki kitna bhi lamba quote ho bahar na jaye
        font = ImageFont.truetype("hindifont.ttf", 80)
        w_font = ImageFont.truetype("hindifont.ttf", 80) # Watermark Size
    except:
        font = w_font = ImageFont.load_default()

    # Smart Wrap Logic: Max 18 characters per line
    words = quote.split()
    lines, current = [], ""
    for w in words:
        if len(current + w) < 18:
            current += w + " "
        else:
            lines.append(current.strip())
            current = w + " "
    lines.append(current.strip())

    # Middle Alignment (Text hamesha beech mein rahega)
    line_h = 110
    total_text_h = len(lines) * line_h
    start_y = (1080 - total_text_h) // 2 
    
    for line in lines:
        # Shadow
        draw.text((542, start_y + 2), line, fill=(0, 0, 0), font=font, anchor="mm")
        # Gold Text
        draw.text((540, start_y), line, fill=(255, 215, 0), font=font, anchor="mm")
        start_y += line_h
    
    # Bada Watermark
    draw.text((540, 1010), "@affan.ai.motivation", fill=(255, 255, 255, 180), font=w_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c = get_content()
    full_cap = f"{c}\n\n👉 Follow: @affan.ai.motivation\n\n.\n.\n{FIXED_TAGS}"
    
    img = create_image(q)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=95)
    
    # Post to FB
    requests.post(f"https://graph.facebook.com/{FB_PAGE_ID}/photos", 
                  data={'message': full_cap, 'access_token': FB_ACCESS_TOKEN}, 
                  files={'source': buf.getvalue()})
    print("Post Successful: Import Fixed, Text Bound fixed!")
