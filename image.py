from PIL import Image, ImageDraw

CREATOR = "فرعی22:امیر علی فروزان اصل"

def make_image(text):
    img = Image.new("RGB", (800, 500), (25, 25, 25))
    draw = ImageDraw.Draw(img)

    draw.text((100, 200), text, fill="white")
    draw.text((250, 450), CREATOR, fill="gray")

    path = "img.jpg"
    img.save(path)
    return path


def make_sticker(path):
    img = Image.open(path)
    img = img.convert("RGBA")
    img = img.resize((512, 512))

    out = "sticker.webp"
    img.save(out, "WEBP")
    return out
