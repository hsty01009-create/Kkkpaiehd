from PIL import Image, ImageDraw

CREATOR = "امیر علی فروزان اصل"

def make_image(text):
    img = Image.new("RGB", (800, 500), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    draw.text((100, 200), text, fill="white")
    draw.text((200, 450), CREATOR, fill="gray")

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
