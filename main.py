import os, requests, io, random, json, time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

# Fixed Trending Tags
FIXED_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_content():
    # Adding a timestamp and a random number to the prompt forces AI to be unique
    unique_id = f"{time.time()}-{random.randint(100, 999)}"
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        # Strict negative prompting to avoid previous themes
        prompt = (f"RequestID: {unique_id}. Write a brand NEW 2-line savage Hindi attitude quote. "
                  "DO NOT use words: 'Mehnat', 'Pehchaan', 'Duniya', 'Andaz', 'Barabari'. "
                  "Topic: Choose randomly between (Royal, Silence, Fear, Revenge, Empire). "
                  "Return ONLY JSON: {\"quote\": \"...\", \"caption\": \"...\"}")
        
        response = model.generate_content(prompt, generation_config={"temperature": 1.0})
        data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return data['quote'], data['caption']
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def create_image(quote):
    # Dynamic image fetch
    img_res = requests.get(f"https://picsum.photos/1080/1080?random={random.random()}")
    img = Image.open(io.BytesIO(img_res.content))
    
    # Dark overlay for better readability
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 185))
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        # Optimized font size to stay within image boundaries
        font = ImageFont.truetype("hindifont.ttf", 75)
        w_font = ImageFont.truetype("hindifont.ttf", 95) 
    except:
        font = w_font = ImageFont.load_default()

    # Wrap logic
    words = quote.split()
    lines, current = [], ""
    for w in words:
        if len(current + w) < 20: current += w + " "
        else:
            lines.append(current.strip())
            current = w + " "
    lines.append(current.strip())

    # Dynamic line spacing and centering
    line_h = 110
    y = (1080 - (len(lines) * line_h)) // 2 
    
    for line in lines:
        draw.text((542, y + 2), line, fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y), line, fill=(255, 215, 0), font=font, anchor="mm")
        y += line_h
    
    # Large Watermark as per requirements
    draw.text((540, 1010), "@affan.ai.motivation", fill=(255, 255, 255, 180), font=w_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c = get_content()
    
    if q and c:
        full_cap = f"{c}\n\n👉 Follow for more: @affan.ai.motivation\n\n.\n.\n{FIXED_TAGS}"
        img = create_image(q)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=95)
        
        # Post to Facebook
        requests.post(f"https://graph.facebook.com/{FB_PAGE_ID}/photos", 
                      data={'message': full_cap, 'access_token': FB_ACCESS_TOKEN}, 
                      files={'source': buf.getvalue()})
        print("Success: Unique Post Uploaded!")
    else:
        print("Skipping to avoid duplicate post.")
