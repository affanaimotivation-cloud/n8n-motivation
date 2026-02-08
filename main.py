import os
import requests
import io
import random
import time
from google import genai # Nayi library
from PIL import Image, ImageDraw, ImageFont

# 1. Config
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

# Naya Gemini Client
client = genai.Client(api_key=GEMINI_KEY)

def get_content():
    topics = ["Discipline", "Focus", "Hard Work", "Success Mindset", "Sacrifice", "Leadership"]
    chosen = random.choice(topics)
    try:
        prompt = f"Write a powerful, unique Hindi motivational quote about {chosen}. Then write a 12-line deep inspirational caption in Hindi/Hinglish and 45 trending hashtags. Format: Quote | Caption | Tags"
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "मेहनत इतनी खामोशी से करो कि सफलता शोर मचा दे।", "Utho aur ladna shuru karo!", "#motivation #success #hindi #viral #40tags"

def get_premium_image():
    queries = ["entrepreneur-man", "fitness-success", "dark-mountain", "galaxy-stars", "urban-motivation"]
    q = random.choice(queries)
    try:
        # Sig parameter taaki har baar alag photo aaye
        url = f"https://images.unsplash.com/photo-1?auto=format&fit=crop&w=1080&h=1080&q=80&query={q}&sig={random.randint(1,5000)}"
        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content))
    except:
        print("Image download failed, using solid color fallback.")
    
    # Backup: Agar image download nahi hoti, toh black background dega crash hone ki jagah
    return Image.new('RGB', (1080, 1080), color=(15, 20, 35))

def create_image(quote):
    img = get_premium_image()
    # Overlay logic jo crash nahi hoga kyunki image hamesha 'img' mein hogi
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 160)) 
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        # Aapki font file
        font = ImageFont.truetype("hindifont.ttf", 115) 
    except:
        font = ImageFont.load_default()

    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 13: current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    y_text = 540 - (len(lines) * 90)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 180
    
    draw.text((540, 1030), "@affan.ai.motivation", fill=(255, 255, 255), anchor="mm")
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
    full_caption = f"{c}\n\n.\n.\n{t}"
    img = create_image(q)
    post_to_fb(img, full_caption)
    print("Success: Final Fixed Version Posted!")
