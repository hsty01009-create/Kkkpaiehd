from PIL import Image, ImageEnhance, ImageDraw

def edit_image(path, text="PRO AI"):
    img = Image.open(path)

    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = ImageEnhance.Brightness(img).enhance(1.2)

    draw = ImageDraw.Draw(img)
    draw.text((40, 40), text, fill="white")

    out = path.replace(".jpg", "_edit.jpg")
    img.save(out)
    return out
