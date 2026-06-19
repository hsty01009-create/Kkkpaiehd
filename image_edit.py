from PIL import Image, ImageFilter, ImageEnhance

def enhance(path):
    img = Image.open(path)
    img = ImageEnhance.Sharpness(img).enhance(2)
    out = "enh.jpg"
    img.save(out)
    return out


def blur(path):
    img = Image.open(path).filter(ImageFilter.BLUR)
    out = "blur.jpg"
    img.save(out)
    return out


def gray(path):
    img = Image.open(path).convert("L")
    out = "gray.jpg"
    img.save(out)
    return out
