import os
import requests
import io
import random
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. Configuration
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    try:
        prompt = "Write 1 powerful motivational quote in HINDI. Then write a 6-line inspirational caption and 20 hashtags. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "सफलता का रास्ता मेहनत से होकर गुजरta है।", "Stay motivated!", "#motivation #success"

def get_image_pro():
    # Pollinations agar fail ho toh ye Picsum se high-quality nature image lega
    keywords = ["nature", "mountain", "space", "dark-forest", "ocean"]
    word = random.choice(keywords)
    
    # Method 1: Pollinations (AI Generated)
    try:
        seed = random.randint(1, 100000)
        url = f"https://image.pollinations.ai/prompt/dark-cinematic-{word}-motivation-background?width=1080&height=1080&nologo=true&seed={seed}"
        res = requests.get(url, timeout=20)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content))
    except:
        print("Pollinations failed, trying stable source...")

    # Method 2: Picsum (High Quality Real Photos - 100% Stable)
    try:
        url = f"https://picsum.photos/1080/1080?grayscale&blur=2" # Dark/Blur look for text clarity
        res = requests.get(url, timeout=20)
        return Image.open(io.BytesIO(res.content))
    except:
        # Last Resort: Dark Blue Gradient jaisa feel
        return Image.new('RGB', (1080, 1080), color=(10, 20, 30))

def create_image(quote):
    img = get_image_pro()
    draw = ImageDraw.Draw(img)

    # Text readability ke liye halka sa dark layer upar se
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 100)) # 100 is transparency
    img.paste(overlay, (0,0), overlay)

    try:
        font_path = "hindifont.ttf" 
        font = ImageFont.truetype(font_path, 110) 
    except:
        font = ImageFont.load_default()

    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 12: 
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    y_text = 540 - (len(lines) * 80)
    for line in lines:
        # Shadow
        draw.text((545, y_text + 5), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        # Main Text (Yellow/Gold)
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 160
    
    return img

# ... post_to_fb function wahi rahega ...

if __name__ == "__main__":
    q, c, t = get_content()
    full_text = f"{c}\n\n.\n.\n{t}"
    img = create_image(q)
    # Save image for posting
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=95)
    
    # Facebook post logic
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': full_text, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    requests.post(url, data=payload, files=files)
    print("Post Completed!")
