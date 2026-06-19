def generate_image_url(prompt: str):
    prompt = prompt.replace(" ", "%20")
    return f"https://image.pollinations.ai/prompt/{prompt}"
