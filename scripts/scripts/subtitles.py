import srt
from datetime import timedelta

def create_subtitles(text, output_file="subtitles.srt"):
    """
    Simple Hindi subtitles create karta hai
    """
    if not text:
        raise ValueError("Subtitle ke liye text empty hai")

    lines = text.split("।")
    subtitles = []

    start = timedelta(seconds=0)
    duration = timedelta(seconds=3)

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        end = start + duration

        subtitles.append(
            srt.Subtitle(
                index=i + 1,
                start=start,
                end=end,
                content=line
            )
        )

        start = end

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(srt.compose(subtitles))

    return output_file

