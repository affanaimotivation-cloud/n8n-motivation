import os
from moviepy.editor import ImageClip, AudioFileClip
from scripts.fb_upload import upload_video

def create_reel():
    print("--- 🎬 वीडियो बनाना शुरू हो रहा है ---")
    
    # अपनी फाइलों के नाम यहाँ चेक करें
    image_path = "background.jpg"  # आपकी फोटो
    audio_path = "audio.mp3"        # आपका म्यूजिक/ऑडियो
    output_path = "final_reel.mp4"  # जो वीडियो बनेगा
    
    # चेक करें कि फाइलें मौजूद हैं या नहीं
    if not os.path.exists(image_path) or not os.path.exists(audio_path):
        print(f"Error: {image_path} या {audio_path} नहीं मिल रही!")
        return None

    try:
        # 1. ऑडियो लोड करें
        audio = AudioFileClip(audio_path)
        
        # 2. इमेज लोड करें और उसकी लंबाई ऑडियो जितनी रखें
        clip = ImageClip(image_path).set_duration(audio.duration)
        
        # 3. ऑडियो को इमेज के साथ जोड़ें
        clip = clip.set_audio(audio)
        
        # 4. वीडियो को सेव करें (Facebook Reels के लिए 30fps बेस्ट है)
        print("Rendering video... इसमें थोड़ा समय लग सकता है।")
        clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        # रेंडरिंग के बाद फाइल साइज चेक करें
        size = os.path.getsize(output_path)
        print(f"Video created successfully: {size} bytes")
        
        return output_path
    except Exception as e:
        print(f"Rendering Error: {e}")
        return None

def main():
    # स्टेप 1: वीडियो बनाएं
    video_file = create_reel()
    
    if video_file:
        # स्टेप 2: साइज चेक करें ताकि 111 bytes वाला एरर न आए
        if os.path.getsize(video_file) > 1000:
            caption = "Amazing AI Reel 🚀 #reels #automation #python"
            
            try:
                print("Facebook पर अपलोड किया जा रहा है...")
                response = upload_video(video_file, caption)
                print("🎉 मुबारक हो! रील पोस्ट हो गई:", response)
            except Exception as e:
                print(f"❌ अपलोड फेल हो गया: {e}")
        else:
            print("🛑 वीडियो फाइल बहुत छोटी (corrupt) है।")
    else:
        print("❌ वीडियो नहीं बन पाया।")

if __name__ == "__main__":
    main()
