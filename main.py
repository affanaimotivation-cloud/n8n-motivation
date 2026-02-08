import os
import requests
import io
import random
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config (Secrets)
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    # Randomness ke liye topics badalte rahenge
    topics = ["Unstoppable Discipline", "Wealth Mindset", "Pain is Power", "Consistency", "Leadership", "Sacrifice for Dreams"]
    chosen = random.choice(topics)
    try:
        # Sakht Prompt: Kam se kam 30 tags aur 10 lines ka caption
        prompt = f"Write a powerful Hindi motivational quote about {chosen}. Then write a 10-line deep inspirational caption in Hindi/Hinglish. Finally, provide 40 trending Instagram/Facebook hashtags. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "किस्मत का रोना रोने से कुछ नहीं होगा, मेहनत करो।", "Utho aur apne sapno ke liye ladna shuru karo.", "#motivation #success #quotes #hardwork #viral"

def get_premium_image():
    # Diversified Queries: Insaan, Space, Nature sab kuch
    queries = ["entrepreneur-man", "fitness-woman", "galaxy-stars", "dark-mountain", "urban-city-night", "deep-ocean"]
    q = random.choice(queries)
    try:
        # Direct Source URL taaki black screen na aaye
        seed = random.randint(1, 2000)
        url = f"https://source.unsplash.com/featured/1080x1080?{q}&sig={seed}"
        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content))
    except:
        # Backup stable source
        return Image.open(io.BytesIO(requests.get(f"https://picsum.photos/1080/1080?random={random.randint(1,100)}").content))

def create_image(quote):
    img = get_premium_image()
    # Dark Tint layer taaki text chamke
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 150))
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        # Aapki uploaded font file
        font = ImageFont.truetype("hindifont.ttf", 115) 
    except:
        font = ImageFont.load_default()

    # Text wrapping logic
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 13: current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # Drawing (Gold Text + Shadow)
    y_text = 540 - (len(lines) * 90)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 180
    
    # Handle bada aur niche
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
    # Formatting caption with extra hashtags
    full_caption = f"{c}\n\n.\n.\n{t}"
    img = create_image(q)
    post_to_fb(img, full_caption)
    print("Success: Post with 40+ Tags & Long Caption!")
