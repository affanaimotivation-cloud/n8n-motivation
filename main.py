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

# Gemini Client Setup
client = genai.Client(api_key=GEMINI_KEY)

def get_content():
    # Topics list for unique content
    topics = ["Discipline", "Focus", "Hard Work", "Success Mindset", "Luxury Life", "Athlete Motivation"]
    chosen = random.choice(topics)
    try:
        # Prompt for 40+ hashtags and long caption
        prompt = f"Write a powerful, unique Hindi motivational quote about {chosen}. Then write a 12-line deep inspirational caption in Hindi/Hinglish and 45 trending hashtags. Format: Quote | Caption | Tags"
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "ख्वाब बड़े देखो, मेहनत उससे भी बड़ी करो।", "Utho aur ladna shuru karo!", "#motivation #success #hindi #viral"

def get_premium_image():
    # Specific keywords for humans, space, and nature
    queries = ["entrepreneur", "fitness", "luxury-car", "mountain-climbing", "galaxy", "office-work"]
    q = random.choice(queries)
    try:
        # Most stable Direct Unsplash URL
        seed = random.randint(1, 10000)
        url = f"https://source.unsplash.com/featured/1080x1080?{q}&sig={seed}"
        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content))
    except:
        print("Unsplash fetch failed, using Picsum backup.")
    
    # Backup: Picsum is extremely stable if Unsplash fails
    try:
        res = requests.get(f"https://picsum.photos/1080/1080?random={random.randint(1,500)}")
        return Image.open(io.BytesIO(res.content))
    except:
        return Image.new('RGB', (1080, 1080), color=(10, 20, 30))

def create_image(quote):
    img = get_premium_image()
    # Adding a darker overlay for text clarity
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 150)) 
    img.paste(overlay, (0,0), overlay)
    
    draw = ImageDraw.Draw(img)
    try:
        # Using the hindi font you uploaded
        font = ImageFont.truetype("hindifont.ttf", 110) 
    except:
        font = ImageFont.load_default()

    # Wrapping text
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 14: current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # Drawing (Gold Text + Black Shadow)
    y_text = 540 - (len(lines) * 90)
    for line in lines:
        draw.text((546, y_text + 6), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 180
    
    # Large handle at the bottom
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
    print("Unique Post Completed!")
