from PIL import Image, ImageDraw

CREATOR = "امیر علی فروزان اصل"

def edit_image(path):
    img = Image.open(path)
    d = ImageDraw.Draw(img)

    d.rectangle([(0,0),(800,100)], fill="black")
    d.text((20,30), "EDITED ✨", fill="white")

    d.rectangle([(0,450),(800,500)], fill="black")
    d.text((20,460), CREATOR, fill="white")

    out = "edit.jpg"
    img.save(out)
    return out


def make_sticker(path):
    img = Image.open(path)
    img = img.convert("RGBA")
    img = img.resize((512,512))

    out = "sticker.webp"
    img.save(out, "WEBP")
    return out
