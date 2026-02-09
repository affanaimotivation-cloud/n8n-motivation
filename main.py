import os, requests, io, random, json, time
from google import genai  # Nayi library
from PIL import Image, ImageDraw, ImageFont

# 1. Setup New Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

# Fixed Tags
FIXED_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_unique_content():
    try:
        # Unique timestamp taaki repetition na ho
        prompt = (f"ID:{time.time()}. Write a brand new 2-line savage Hindi attitude quote. "
                  "STRICT: Do NOT use 'Mehnat', 'Pehchaan', 'Duniya', 'Andaz'. "
                  "Use heavy words like 'Sultanat', 'Dahshat', 'Riyasat'. "
                  "Return JSON ONLY: {\"quote\": \"...\", \"caption\": \"...\"}")
        
        # Sahi model name jo 404 nahi dega
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            config={'temperature': 1.0}, 
            contents=prompt
        )
        data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return data['quote'], data['caption']
    except Exception as e:
        print(f"API Error: {e}")
        return None, None # Purana content post nahi hoga

def create_image(quote):
    # Fetch background
    img = Image.open(io.BytesIO(requests.get(f"https://picsum.photos/1080/1080?random={random.random()}").content))
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 190))
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        # Font size 80 taaki image se bahar na jaye
        font = ImageFont.truetype("hindifont.ttf", 80)
        w_font = ImageFont.truetype("hindifont.ttf", 100) # Bada Watermark
    except:
        font = w_font = ImageFont.load_default()

    # Smart Wrap: 18 chars max per line
    words = quote.split()
    lines, current = [], ""
    for w in words:
        if len(current + w) < 18: current += w + " "
        else: lines.append(current.strip()); current = w + " "
    lines.append(current.strip())

    # Vertical Centering
    y = (1080 - (len(lines) * 115)) // 2 
    for line in lines:
        draw.text((543, y + 3), line, fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y), line, fill=(255, 215, 0), font=font, anchor="mm")
        y += 115
    
    draw.text((540, 1010), "@affan.ai.motivation", fill=(255, 255, 255, 180), font=w_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c = get_unique_content()
    if q and c:
        full_cap = f"{c}\n\n👉 Follow: @affan.ai.motivation\n\n.\n.\n{FIXED_TAGS}"
        img = create_image(q)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=95)
        
        # Direct FB Post
        requests.post(f"https://graph.facebook.com/{FB_PAGE_ID}/photos", 
                      data={'message': full_cap, 'access_token': FB_ACCESS_TOKEN}, 
                      files={'source': buf.getvalue()})
        print("Success: Unique Content Posted!")
    else:
        print("Skipped to prevent repetition.")
