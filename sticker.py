from PIL import Image

def create_sticker(path):
    img = Image.open(path)
    img = img.convert("RGBA")
    img = img.resize((512, 512))

    out = "sticker.webp"
    img.save(out, "WEBP")
    return out
