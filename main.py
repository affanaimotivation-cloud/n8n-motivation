import os, requests, io, random, time
from google import genai
from PIL import Image, ImageDraw, ImageFont

# 1. Config (GitHub Secrets)
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# 2. Setup New Gemini Client
client = genai.Client(api_key=GEMINI_KEY)

def get_content():
    try:
        prompt = "Write 1 powerful motivational quote in HINDI. Then a long inspirational caption and 15 trending hashtags. Format: Quote | Caption | Tags"
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        parts = response.text.strip().split('|')
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return "कोशिश करने वालों की कभी हार नहीं होती।", "Never give up!", "#motivation #success #hindi #trending #goals"

def get_image():
    # Pollinations fail hone par Picsum use karega (Zyada stable)
    for i in range(3):
        try:
            seed = random.randint(1, 1000)
            # Stable Source: Picsum (Nature/Dark images)
            url = f"https://picsum.photos/seed/{seed}/1080/1080"
            res = requests.get(url, timeout=20)
            img = Image.open(io.BytesIO(res.content))
            return img
        except:
            time.sleep(2)
    raise Exception("Image sources are down")

def create_image(quote):
    img = get_image()
    # Image ko thoda dark karna taaki text dikhe
    overlay = Image.new('RGBA', img.size, (0,0,0,100))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    draw = ImageDraw.Draw(img)
    
    # 3. Hindi Font Setup (Extra Large Size 120)
    try:
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"
        font_data = requests.get(font_url).content
        font = ImageFont.truetype(io.BytesIO(font_data), 120)
    except:
        font = ImageFont.load_default()

    # Text wrapping logic
    words = quote.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line + word) < 15:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # Drawing Text (Gold color with Shadow)
    y_text = 540 - (len(lines) * 70)
    for line in lines:
        draw.text((545, y_text + 5), line.strip(), fill=(0, 0, 0), font=font, anchor="mm") # Shadow
        draw.text((540, y_text), line.strip(), fill=(255, 215, 0), font=font, anchor="mm") # Gold Text
        y_text += 150
    return img

def post_to_fb(image_obj, message):
    img_byte_arr = io.BytesIO()
    image_obj.save(img_byte_arr, format='JPEG', quality=95)
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    payload = {'message': message, 'access_token': FB_ACCESS_TOKEN}
    files = {'source': ('post.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
    r = requests.post(url, data=payload, files=files)
    print("Post Response:", r.json())

if __name__ == "__main__":
    try:
        q, c, t = get_content()
        img = create_image(q)
        # Bada caption aur 15 tags
        post_to_fb(img, f"{c}\n\n.\n.\n{t}")
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
