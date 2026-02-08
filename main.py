import os
import requests
import io
import random
import time
from google import genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config (Secrets)
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_KEY)

def get_content():
    topics = ["High Performance", "Aggressive Success", "Stoic Mindset", "Consistency", "Wealth Creation"]
    chosen = random.choice(topics)
    try:
        # Sakht instruction 50 trending hashtags ke liye taaki #tag kam na hon
        prompt = f"Write a powerful Hindi motivational quote about {chosen}. Then write a 12-line deep inspirational caption. Finally, provide exactly 50 trending and viral hashtags. Format: Quote | Caption | Tags"
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "मेहनत का कोई विकल्प नहीं है।", "Keep pushing forward!", "#motivation #success #viral #trending"

def get_premium_image():
    queries = ["fitness-motivation", "entrepreneur-lifestyle", "luxury-homes", "mountains", "space-exploration"]
    q = random.choice(queries)
    try:
        seed = random.randint(1, 10000)
        # Direct stable source taaki black background na aaye
        url = f"https://source.unsplash.com/featured/1080x1080?{q}&sig={seed}"
        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content))
    except:
        # Backup stable source
        res = requests.get(f"https://picsum.photos/1080/1080?random={random.randint(1,500)}")
        return Image.open(io.BytesIO(res.content))

def create_image(quote):
    img = get_premium_image()
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 150)) 
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        # Sahi font file path
        font = ImageFont.truetype("hindifont.ttf", 110)
        # Watermark ke liye bada font size
        watermark_font = ImageFont.truetype("hindifont.ttf", 60) 
    except:
        font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 14: current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    y_text = 540 - (len(lines) * 95)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 190
    
    # 1. Image Watermark Bara Kiya (Size 60)
    draw.text((540, 1010), "@affan.ai.motivation", fill=(255, 255, 255), font=watermark_font, anchor="mm")
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
    # 2. Caption mein "Follow for more" add kiya har post ke liye
    full_caption = f"{c}\n\nFollow for more: @affan.ai.motivation\n\n.\n.\n{t}"
    img = create_image(q)
    post_to_fb(img, full_caption)
    print("Post with 50 tags, larger watermark and follow-handle completed!")
