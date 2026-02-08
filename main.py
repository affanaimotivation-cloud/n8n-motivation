import os
import requests
import io
import random
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# Secrets Setup
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    # Randomness badhane ke liye seed ka use
    random_topics = ["Hard work", "Never give up", "Success mindset", "Time management", "Confidence", "Discipline"]
    topic = random.choice(random_topics)
    
    try:
        # Gemini ko har baar alag topic dene ke liye prompt badla hai
        prompt = f"Write a unique, deep motivational quote in HINDI about '{topic}'. Then write an 8-line emotional caption and 30 trending hashtags. Format: Quote | Caption | Tags. Do not repeat previous quotes."
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "नया सवेरा, नयी उम्मीद।", "Aaj ka din aapka hai!", "#motivation #newday"

def get_premium_image():
    try:
        # Humans, Space aur Nature ka mix search
        queries = ["hardworking person", "office success", "space galaxy", "mountain climber", "gym motivation", "urban lifestyle"]
        q = random.choice(queries)
        
        # Sigle random photo ke liye 'sig' parameter add kiya hai taaki image repeat na ho
        url = f"https://api.unsplash.com/photos/random?query={q}&orientation=squarish&client_id={UNSPLASH_KEY}&sig={random.randint(1, 999)}"
        
        response = requests.get(url, timeout=30).json()
        image_url = response['urls']['regular']
        img_data = requests.get(image_url).content
        return Image.open(io.BytesIO(img_data)).resize((1080, 1080))
    except:
        # Fallback agar API limit hit ho jaye
        return Image.new('RGB', (1080, 1080), color=(20, 20, 40))

def create_image(quote):
    img = get_premium_image()
    
    # Text ke piche halka black tint taaki saaf dikhe
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 130))
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    
    try:
        font_path = "hindifont.ttf"
        font = ImageFont.truetype(font_path, 110)
    except:
        font = ImageFont.load_default()

    # Text wrapping
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 13:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # Drawing text
    y_text = 540 - (len(lines) * 90)
    for line in lines:
        draw.text((545, y_text + 5), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
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
    full_caption = f"{c}\n\n.\n.\n{t}"
    img = create_image(q)
    post_to_fb(img, full_caption)
    print("Unique Post Done!")
