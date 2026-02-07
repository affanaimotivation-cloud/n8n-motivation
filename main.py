import os
import requests
import io
import random
from google import genai
from PIL import Image, ImageDraw, ImageFont

# API Configs
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Hum explicitly 'v1' version specify kar rahe hain 404 error hatane ke liye
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options={'api_version': 'v1'}
)

def get_content():
    prompt = "Write a 1-line powerful motivational quote. Also, give a 1-sentence image background prompt. Format: Quote | ImagePrompt"
    try:
        # Model name check karein
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        parts = response.text.split('|')
        return (parts[0].strip(), parts[1].strip()) if len(parts) > 1 else (response.text.strip(), "nature success motivation background")
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return ("Success is not final, failure is not fatal.", "golden sunrise over mountains")

def create_image(quote, img_prompt):
    seed = random.randint(1, 100000)
    # Pollinations image generation
    url = f"https://image.pollinations.ai/prompt/{img_prompt.replace(' ', '%20')}?width=1080&height=1080&nologo=true&seed={seed}"
    img_data = requests.get(url).content
    img = Image.open(io.BytesIO(img_data))
    
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Simple font logic
    font = ImageFont.load_default()
    
    # Text shadow (black) and main text (white)
    text_pos = (width // 2, height // 2)
    draw.text((text_pos[0]+2, text_pos[1]+2), quote, fill="black", anchor="mm", font=font)
    draw.text(text_pos, quote, fill="white", anchor="mm", font=font)
    
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG')
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    data = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    r = requests.post(url, files=files, data=data)
    print(f"FB Response: {r.json()}")

# Start
try:
    quote, p_prompt = get_content()
    print(f"Quote: {quote}")
    final_image = create_image(quote, p_prompt)
    post_to_fb(final_image, quote)
    print("Process Finished Successfully!")
except Exception as e:
    print(f"Critical Error: {e}")
