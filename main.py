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
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY") #

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    # Content repeat na ho isliye random topics
    topics = ["Discipline", "Focus", "Hard Work", "Rich Mindset", "Overcoming Failure", "Patience"]
    chosen = random.choice(topics)
    try:
        prompt = f"Write a deep, unique Hindi motivational quote about {chosen}. Then write a 10-line inspirational caption and 35 trending hashtags. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "ख्वाब बड़े देखो, मेहनत उससे भी बड़ी करो।", "Apne sapno ko pura karne ka waqt aa gaya hai!", "#motivation #success #hindi #viral"

def get_premium_image():
    # Human, Space, aur Nature ka random mix
    queries = ["entrepreneur", "space", "galaxy", "man-success", "fitness", "dark-nature", "mountain-climb"]
    q = random.choice(queries)
    try:
        # Direct URL method with random seed to prevent repeats
        seed = random.randint(1, 1000)
        url = f"https://source.unsplash.com/featured/1080x1080?{q}&sig={seed}"
        res = requests.get(url, timeout=30)
        return Image.open(io.BytesIO(res.content))
    except:
        # 2nd Option agar source down ho
        url = f"https://picsum.photos/1080/1080?random={random.randint(1,500)}"
        res = requests.get(url)
        return Image.open(io.BytesIO(res.content))

def create_image(quote):
    img = get_premium_image()
    # Dark Tint for clarity
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 140))
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        # Sahi font loading
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

    # Drawing Text (Gold + Black Shadow)
    y_text = 540 - (len(lines) * 90)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 180
        
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
    full_cap = f"{c}\n\n.\n.\n{t}"
    img = create_image(q)
    post_to_fb(img, full_cap)
    print("Task Done!")
