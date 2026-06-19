from PIL import Image

def make_sticker(path):
    img = Image.open(path).convert("RGBA")
    img.thumbnail((512, 512))
    out = path.replace(".jpg", ".webp")
    img.save(out, "WEBP")
    return out
