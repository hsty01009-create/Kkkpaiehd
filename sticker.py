from PIL import Image
import os


def create_sticker(input_file, output_file="sticker.webp"):
    """
    تبدیل عکس به استیکر تلگرام
    """

    img = Image.open(input_file).convert("RGBA")

    width, height = img.size

    max_size = 512

    if width > height:
        new_width = max_size
        new_height = int(height * max_size / width)
    else:
        new_height = max_size
        new_width = int(width * max_size / height)

    img = img.resize((new_width, new_height))

    background = Image.new("RGBA", (512, 512), (0, 0, 0, 0))

    x = (512 - new_width) // 2
    y = (512 - new_height) // 2

    background.paste(img, (x, y), img)

    background.save(output_file, "WEBP")

    return output_file
