from PIL import Image, ImageEnhance, ImageFilter

def edit_image(path):
    img = Image.open(path)

    img = ImageEnhance.Brightness(img).enhance(1.4)
    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = ImageEnhance.Sharpness(img).enhance(1.6)

    img = img.filter(ImageFilter.DETAIL)

    out = "edited.jpg"
    img.save(out)
    return out
