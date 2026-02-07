import os, requests, io, random
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# API Configs from your GitHub Secrets
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_content():
    prompt = "Write a 1-line powerful motivational quote. Also, give a 1-sentence image background prompt. Format: Quote | ImagePrompt"
    response = model.generate_content(prompt)
    parts = response.text.split('|')
    return (parts[0].strip(), parts[1].strip()) if len(parts) > 1 else (response.text, "success motivation background")

def create_image(quote, img_prompt):
    seed = random.randint(1, 100000)
    url = f"https://image.pollinations.ai/prompt/{img_prompt.replace(' ', '%20')}?width=1080&height=1080&nologo=true&seed={seed}"
    img = Image.open(io.BytesIO(requests.get(url).content))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default() 
    draw.text((540, 540), quote, fill=(255, 215, 0), anchor="mm")
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG')
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    data = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    r = requests.post(url, files=files, data=data)
    print(r.json())

try:
    q, p = get_content()
    img = create_image(q, p)
    post_to_fb(img, q)
    print("Post Successful!")
except Exception as e:
    print(f"Error: {e}")
