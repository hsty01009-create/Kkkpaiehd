import requests
from urllib.parse import quote


def generate_image_url(prompt):
    """
    ساخت لینک عکس از متن
    """
    prompt = quote(prompt)
    return f"https://image.pollinations.ai/prompt/{prompt}"


def check_image(prompt):
    """
    تست وجود عکس
    """
    try:
        url = generate_image_url(prompt)
        r = requests.get(url, timeout=20)

        if r.status_code == 200:
            return url

        return None

    except Exception:
        return None
