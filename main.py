import os, requests, io, random, json, time
from google import genai  # Nayi library
from PIL import Image, ImageDraw, ImageFont

# 1. API Client Setup (FORCE VERSION V1)
# Yahi wo badlav hai jo 404 error ko khatam karega
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={'api_version': 'v1'} # Forcefully using stable version
)

FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

FIXED_TAGS = "#motivation #success #viral #trending #reels #mindset #affan_ai_motivation #foryou #explore #attitude #power #alpha #money"

def get_unique_content():
    try:
        prompt = (f"ID:{time.time()}. Write a brand new 2-line savage Hindi attitude quote. "
                  "STRICT: No 'Duniya', 'Pehchaan', 'Mehnat'. Focus on 'Royal' and 'Killer' attitude. "
                  "Return JSON ONLY: {\"quote\": \"...\", \"caption\": \"...\"}")
        
        # 'models/' prefix lagane se compatibility badh jati hai
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            config={'temperature': 1.0}, 
            contents=prompt
        )
        
        raw_text = response.text.strip()
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0]
        
        data = json.loads(raw_text)
        return data['quote'], data['caption']
    except Exception as e:
        print(f"Final Attempt Error: {e}")
        return None, None

def create_image(quote):
    try:
        # Unsplash random HD image
        img_url = f"[https://api.unsplash.com/photos/random?query=dark,luxury,lifestyle&client_id=](https://api.unsplash.com/photos/random?query=dark,luxury,lifestyle&client_id=){UNSPLASH_KEY}"
        img_res = requests.get(img_url).json()
        download_url = img_res['urls']['regular']
        img = Image.open(io.BytesIO(requests.get(download_url).content)).resize((1080, 1080))
    except:
        # Backup if Unsplash fails
        img = Image.open(io.BytesIO(requests.get(f"[https://picsum.photos/1080/1080?random=](https://picsum.photos/1080/1080?random=){random.random()}").content))

    overlay = Image.new('RGBA', img.size, (0, 0, 0, 195)) # Darker overlay
    img.paste(overlay, (0,0), overlay)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("hindifont.ttf", 85) # Thoda bada font
        w_font = ImageFont.truetype("hindifont.ttf", 90) 
    except:
        font = w_font = ImageFont.load_default()

    # Wrap Text Logic
    words = quote.split()
    lines, current = [], ""
    for w in words:
        if len(current + w) < 18: current += w + " "
        else: lines.append(current.strip()); current = w + " "
    lines.append(current.strip())

    y = (1080 - (len(lines) * 120)) // 2 
    for line in lines:
        draw.text((543, y + 3), line, fill=(0, 0, 0), font=font, anchor="mm") # Shadow
        draw.text((540, y), line, fill=(255, 215, 0), font=font, anchor="mm") # Gold Text
        y += 120
    
    draw.text((540, 1020), "@affan.ai.motivation", fill=(255, 255, 255, 150), font=w_font, anchor="mm")
    return img

if __name__ == "__main__":
    q, c = get_unique_content()
    if q and c:
        full_cap = f"{c}\n\n👉 Follow: @affan.ai.motivation\n\n.\n.\n{FIXED_TAGS}"
        img = create_image(q)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=95)
        
        # Facebook API Upload
        res = requests.post(f"[https://graph.facebook.com/](https://graph.facebook.com/){FB_PAGE_ID}/photos", 
                            data={'message': full_cap, 'access_token': FB_ACCESS_TOKEN}, 
                            files={'source': buf.getvalue()})
        print("Success!" if res.status_code == 200 else f"Failed: {res.text}")
    else:
        print("Model still not responding. Check API key permissions.")
