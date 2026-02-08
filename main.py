import os
import requests
import io
import random
import time
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 1. Configuration (Secrets from GitHub)
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY") # Unsplash key ab use hogi

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    try:
        # Prompt ko aur achha kiya hai takki lamba aur behtar caption + 25+ hashtags aayein
        prompt = "Write 1 powerful and deep motivational quote in HINDI. Then write a 8-line highly inspirational and engaging caption, followed by at least 25 trending and relevant hashtags. Format: Quote | Caption | Tags"
        response = model.generate_content(prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except Exception as e:
        print(f"Gemini content error: {e}")
        return "सफलता के लिए सबसे महत्वपूर्ण है निरंतर प्रयास।", "हर छोटा कदम एक दिन बड़ी मंज़िल तक पहुंचाता है।", "#motivation #success #hindi #inspiration #goals"

def get_premium_image():
    # Unsplash se humans, nature, space, urban motivation images search karna
    try:
        # Keywords mein "person", "man", "woman", "fitness" add kiye hain
        query = random.choice([
            "person working hard", "motivational success", "entrepreneur mindset", 
            "nature", "mountains", "galaxy", "ocean", "dark-forest", 
            "urban success", "fitness motivation", "woman empowerment", "man achievement"
        ])
        url = f"https://api.unsplash.com/photos/random?query={query}&orientation=squarish&client_id={UNSPLASH_KEY}"
        response = requests.get(url, timeout=25).json() # Timeout badha diya
        image_url = response['urls']['regular']
        img_data = requests.get(image_url, timeout=25).content
        return Image.open(io.BytesIO(img_data)).resize((1080, 1080))
    except Exception as e:
        print(f"Unsplash Image Error: {e}. Using solid fallback for safety.")
        # Agar Unsplash fail ho toh dark color background
        return Image.new('RGB', (1080, 1080), color=(15, 20, 35))

def create_image(quote):
    # Image lene ke baad use thoda dark aur blur karna taaki text saaf dikhe
    img = get_premium_image()
    
    # Readability ke liye Dark Overlay (Halka kaala parda)
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 150)) # Thoda aur dark kiya
    img.paste(overlay, (0,0), overlay)

    draw = ImageDraw.Draw(img)

    # 2. Hindi Font Fix (Using your uploaded hindifont.ttf)
    try:
        font_path = "hindifont.ttf" 
        font = ImageFont.truetype(font_path, 110) # Bada aur clear size
    except:
        print("Font file 'hindifont.ttf' nahi mili! Check your GitHub repo.")
        font = ImageFont.load_default()

    # Text wrapping logic
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 12: 
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # 3. Draw Text (Gold Color + Shadow)
    y_text = 540 - (len(lines) * 85)
    for line in lines:
        # Shadow (Black)
        draw.text((546, y_text + 6), line.strip(), fill=(0, 0, 0), font=font, anchor="mm")
        # Main Text (Gold)
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm")
        y_text += 175
    
    # Handle add karna niche
    draw.text((540, 1030), "@affan.ai.motivation", fill=(200, 200, 200), anchor="mm")
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG', quality=95)
    
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    r = requests.post(url, data=payload, files=files)
    print("Facebook Result:", r.json())

if __name__ == "__main__":
    try:
        quote, caption, tags = get_content()
        full_caption = f"{caption}\n\n.\n.\n{tags}"
        print(f"Generating post with quote: {quote}")
        img = create_image(quote)
        post_to_fb(img, full_caption)
        print("Successfully Posted to Facebook!")
    except Exception as e:
        print(f"Final Execution Error: {e}")
