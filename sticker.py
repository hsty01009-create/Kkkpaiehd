from PIL import Image

def create_sticker(path):
    img = Image.open(path).convert("RGBA")
    out = "sticker.webp"
    img.save(out, "WEBP")
    return out
