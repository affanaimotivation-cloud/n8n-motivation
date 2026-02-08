import os
import requests
import io
import random
import json
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    topics = ["Empire Building", "Hard Work", "Success Mindset", "Consistency", "Winning Habits"]
    chosen = random.choice(topics)
    try:
        # JSON format instruction taaki data mix na ho
        prompt = (
            f"Write a deep Hindi motivational quote about {chosen}. "
            "Return only a JSON object with keys: 'quote', 'caption' (10 lines), and 'tags' (15 trending hashtags). "
            "Example: {\"quote\": \"...\", \"caption\": \"...\", \"tags\": \"#... #...\"}"
        )
        response = model.generate_content(prompt)
        # Safely cleaning the response text
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_text)
        return data['quote'], data['caption'], data['tags']
    except Exception as e:
        print(f"Content error: {e}")
        return "मेहनत का कोई विकल्प नहीं है।", "Utho aur badho!", "#motivation #success #viral #goals"

def get_premium_image():
    try:
        # Direct Picsum URL is most reliable
        url = f"https://picsum.photos/1080/1080?random={random.randint(1,5000)}"
        res = requests.get(url, timeout=30)
        return Image.open(io.BytesIO(res.content))
    except:
        return Image.new('RGB', (1080, 1080), color=(15, 20, 30))

def create_image(quote):
    img = get_premium_image()
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 175)) 
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        # Font settings
        font = ImageFont.truetype("hindifont.ttf", 110)
        # Bada Watermark (Size 95)
        watermark_font = ImageFont.truetype("hindifont.ttf", 95) 
    except:
        font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    # Text Wrapping
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
    
    # Large Watermark
    draw.text((540, 1010), "@affan.ai.motivation", fill=(255, 255, 255, 215), font=watermark_font, anchor="mm")
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
    # Handle and full hashtags fixed
    full_caption = f"{c}\n\n👉 Follow for more: @affan.ai.motivation\n\n.\n.\n{t}"
    img = create_image(q)
    post_to_fb(img, full_caption)
    print("Task Completed Successfully!")
