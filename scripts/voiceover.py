def create_subtitles(text):
    srt = f"""1
00:00:01,000 --> 00:00:06,000
{text}
"""
    with open("subtitles.srt", "w", encoding="utf-8") as f:
        f.write(srt)

    return "subtitles.srt"
