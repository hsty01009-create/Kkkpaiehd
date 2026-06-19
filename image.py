from PIL import Image, ImageDraw

CREATOR = "امیر علی فروزان اصل"

def make_image(text):
    img = Image.new("RGB", (800, 500), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    draw.text((100, 200), text, fill="white")
    draw.text((200, 450), CREATOR, fill="gray")

    out = "img.jpg"
    img.save(out)
    return out


def edit_image(path):
    img = Image.open(path)
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0,0),(800,80)], fill=(0,0,0))
    draw.text((20,20), "EDITED ✨", fill="white")

    draw.rectangle([(0,450),(800,500)], fill=(0,0,0))
    draw.text((20,460), CREATOR, fill="white")

    out = "edit.jpg"
    img.save(out)
    return out
