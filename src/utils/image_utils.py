import os
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_placeholder(width, height, scene_id):
    """Creates a professional placeholder image if generation fails."""
    img = Image.new('RGB', (width, height), (40, 44, 52))
    draw = ImageDraw.Draw(img)
    text = f"Scene {scene_id}\nVisuals Pending"
    draw.text((width//2 - 100, height//2), text, fill="white", align="center")
    return np.array(img)

import urllib.parse
import io

def get_pollinations_image(prompt, width, height):
    """Unrestricted fallback for image generation using Pollinations.ai."""
    try:
        # CLEAN the prompt for the URL
        safe_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width={width}&height={height}&nologo=true"
        
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content)).convert("RGB")
    except Exception as e:
        print(f"      ❌ Pollinations critical failure: {e}")
        return None
    return None

def draw_subtitles(image_array, text, resolution):
    """Bakes stylized subtitles directly into image frames."""
    w, h = resolution
    img = Image.fromarray(image_array)
    draw = ImageDraw.Draw(img)
    
    # Font discovery
    font = None
    f_size = w // 28
    paths = ["arial.ttf", "LiberationSans-Bold.ttf", "C:\\Windows\\Fonts\\arial.ttf"]
    for p in paths:
        try:
            font = ImageFont.truetype(p, f_size)
            break
        except: continue
    if not font: font = ImageFont.load_default()
        
    lines = textwrap.wrap(text, width=45)
    line_bboxes = [draw.textbbox((0, 0), l, font=font) for l in lines]
    max_w = max([b[2] for b in line_bboxes])
    total_h = sum([b[3] - b[1] for b in line_bboxes]) + (len(lines) * 5)
    
    pad = 15
    y_pos = h * 0.85 - total_h
    draw.rectangle([w/2-max_w/2-pad, y_pos-pad, w/2+max_w/2+pad, y_pos+total_h+pad], fill=(0,0,0,160))
    
    curr_y = y_pos
    for line in lines:
        lw = draw.textbbox((0, 0), line, font=font)[2]
        draw.text((w/2 - lw/2, curr_y), line, font=font, fill="white")
        curr_y += (draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]) + 5
    return np.array(img)
