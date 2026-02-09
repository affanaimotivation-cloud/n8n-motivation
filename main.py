import os, requests, io, random, json, time
from google import genai  # Nayi library import
from PIL import Image, ImageDraw, ImageFont

# 1. API Client Setup
# GitHub Secrets se keys uthayega
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

# Fixed Trending Hashtags
FIXED_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_unique_content():
    """Gemini se naya aur unique content lane ke liye"""
    try:
        # Timestamp ensures AI triggers fresh response every time
        prompt = (f"Time:{time.time()}. Task: Write a brand new 2-line savage Hindi attitude quote. "
                  "STRICT: Do NOT use 'Mehnat', 'Pehchaan', 'Duniya', 'Andaz'. "
                  "Focus on: Royal, Power, Empire. "
                  "Return JSON ONLY: {\"quote\": \"...\", \"caption\": \"...\"}")
        
        # Sahi model name jo 404 nahi dega
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            config={'temperature': 1.0}, 
            contents=prompt
        )
        
        # JSON Clean-up logic
        raw_text = response.text.strip()
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0]
        
        data = json.loads(raw_text)
        return data['quote'], data['caption']
    except Exception as e:
        print(f"Content Generation Error: {e}")
        return None, None # Force skip to avoid repeats

def create_image(quote):
    """Image par text likhne aur alignment fix karne ke liye"""
    # Random background image
    img_res = requests.get(f"[https://picsum.photos/1080/1080?random=](https://picsum.photos/1080/1080?random=){random.random()}")
    img = Image.open(io.BytesIO(img_res.content))
    
    # Dark Overlay for better text visibility
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 190))
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        # Fixed Font sizes for better fitting
        font = ImageFont.truetype("hindifont.ttf", 80)
        w_font = ImageFont.truetype("hindifont.ttf", 100) 
    except:
        font = w_font = ImageFont.load_default()

    # Smart Text Wrapping: 18 chars per line max
    words = quote.split()
    lines, current = [], ""
    for w in words:
        if len(current + w) < 18: current += w + " "
        else:
            lines.append(current.strip())
            current = w + " "
    lines.append(current.strip())

    # Vertical Centering logic
    y = (1080 - (len(lines) * 115)) // 2 
    for line in lines:
        # Shadow Effect
        draw.text((543, y + 3), line, fill=(0, 0, 0), font=font, anchor="mm")
        # Main Golden Text
        draw.text((540, y), line, fill=(255, 215, 0), font=font, anchor="mm")
        y += 115
    
    # Large Watermark
    draw.text((540, 1010), "@affan.ai.motivation", fill=(255, 255, 255, 180), font=w_font, anchor="mm")
    return img

if __name__ == "__main__":
    quote, caption = get_unique_content()
    
    if quote and caption:
        full_caption = f"{caption}\n\n👉 Follow: @affan.ai.motivation\n\n.\n.\n{FIXED_TAGS}"
        final_img = create_image(quote)
        
        # Save to buffer for upload
        buf = io.BytesIO()
        final_img.save(buf, format='JPEG', quality=95)
        
        # Facebook Graph API Call
        res = requests.post(f"[https://graph.facebook.com/](https://graph.facebook.com/){FB_PAGE_ID}/photos", 
                            data={'message': full_caption, 'access_token': FB_ACCESS_TOKEN}, 
                            files={'source': buf.getvalue()})
        
        if res.status_code == 200:
            print("Successfully Posted Unique Content!")
        else:
            print(f"FB Post Failed: {res.text}")
    else:
        print("Skipped: Repetition or API issue avoided.")
