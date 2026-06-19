from PIL import Image, ImageEnhance

def edit_image(path):
    img = Image.open(path)
    img = ImageEnhance.Brightness(img).enhance(1.3)
    img = ImageEnhance.Contrast(img).enhance(1.4)
    out = "edit.jpg"
    img.save(out)
    return out


def make_sticker(path):
    img = Image.open(path).convert("RGBA")
    img.thumbnail((512,512))
    out = "sticker.webp"
    img.save(out, "WEBP")
    return out
