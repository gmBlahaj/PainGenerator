from PIL import Image, ImageDraw, ImageFont
from nltk.tokenize import word_tokenize
import colorsys
import numpy as np
import os
import random
import re
from typing import Tuple, List, Dict, Any

# Set program path to the parent directory to access resources
c_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Centralized Cruelty Squad Color Palette ---
CRUELTY_SQUAD_PALETTE = [
    # SLURPO12
    '#000000', '#1b4418', '#5e5441', '#416e38', '#8a755d', '#659d4a',
    '#c0ad8b', '#81c75f', '#f2e4b9', '#b1e783', '#ffffff', '#d6f89f',
    # Grimy/Industrial
    '#333333', '#4F4F4F', '#828282', '#BDBDBD', '#E0E0E0', '#F2F2F2',
    '#564D4D', '#6A5F5F', '#7F7272', '#948585', '#A99898', '#BEACAC',
    # Flesh and Gore
    '#58181F', '#8C1C27', '#B82735', '#E5394A', '#FF576B', '#FF8A9A',
    '#4A251D', '#7B4032', '#A55A48', '#D27C65', '#FFAD8F', '#FFE4D6',
    # Sickly Greens & Yellows
    '#A1B43B', '#CADB50', '#EFFF6B', '#FFFF9E', '#FFFFD1', '#F0F5BE',
    '#5E6E25', '#7D9033', '#A0B842', '#C7E351', '#EFFF6B', '#F8FFB0',
    # Corporate Blues
    '#0D1B2A', '#1B263B', '#415A77', '#778DA9', '#A9BCD0', '#E0E1DD',
    '#003049', '#00507A', '#0077B6', '#0096C7', '#48CAE4', '#90E0EF',
    # Vibrant & Gaudy ("Knallige")
    '#FF00FF', '#FF00BF', '#FF0080', '#FF0040', '#FF4000', '#FF8000',
    '#FFBF00', '#FFFF00', '#BFFF00', '#80FF00', '#40FF00', '#00FF00',
    '#00FF40', '#00FF80', '#00FFBF', '#00FFFF', '#00BFFF', '#0080FF',
    '#0040FF', '#0000FF', '#4000FF', '#8000FF', '#BF00FF', '#FF00FF',
]

# Load wordlists at startup
wordlists: Dict[str, List[str]] = {}
for list_name in ['SPRAWL', 'TempleOS', '1894']:
    try:
        with open(os.path.join(c_path, 'resources', f'{list_name}.txt'), 'r', encoding='utf8') as f:
            wordlists[list_name] = word_tokenize(f.read())
    except FileNotFoundError:
        wordlists[list_name] = []

def is_valid_hex_code(s: str) -> bool:
    """Checks if a string is a valid hex code."""
    return bool(re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", s))

def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Converts a hex code to an RGB tuple."""
    hex_code = hex_code.lstrip('#')
    if len(hex_code) == 3:
        hex_code = hex_code[0]*2 + hex_code[1]*2 + hex_code[2]*2
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def calculate_text_dimensions(word_length: int, output_width: int) -> Tuple[Tuple[int, int], Tuple[int, int, int, int]]:
    """Calculates the resize and crop dimensions for the text image, scaled to the output size."""
    scale_factor = output_width / 128.0
    resize_y = int(np.interp(word_length, [2, 10], [160, 960]) * scale_factor)
    crop_y1 = int(np.interp(word_length, [2, 10], [24, 40]) * scale_factor)
    crop_y2 = int(np.interp(word_length, [2, 10], [152, 168]) * scale_factor)
    return (output_width, resize_y), (0, crop_y1, output_width, crop_y2)

def generate_image(values: Dict[str, Any]) -> str:
    """Generates a single image based on the provided values and returns the save path."""
    is_user_generated = values.get('-CHECKBOX-', False)

    # --- Input Validation ---
    try:
        width, height = map(int, values['-SIZE-'].split('x'))
    except (ValueError, AttributeError):
        raise ValueError("Invalid image size selected.")

    # --- Word Setup ---
    if is_user_generated:
        word = values.get('-WORD-', 'PAIN')
        if not 2 <= len(word) <= 10:
            raise ValueError("Word must be between 2 and 10 letters.")
    else:
        wordlist_map = {'Cyberpunk AF': 'SPRAWL', 'TempleOS': 'TempleOS', '1894': '1894'}
        chosen_wordlist = values.get('-WORDLIST-', 'Cyberpunk AF')
        wordlist_key = wordlist_map.get(chosen_wordlist)
        if wordlist_key and wordlists.get(wordlist_key):
            word = random.choice(wordlists[wordlist_key])
        else:
            word = "DEFAULT"

    # --- Color Setup ---
    hex1 = values.get('-HEX1-')
    hex2 = values.get('-HEX2-')

    # If hex codes are provided and valid, use them.
    if hex1 and hex2 and is_valid_hex_code(hex1) and is_valid_hex_code(hex2):
        color1, color2 = hex_to_rgb(hex1), hex_to_rgb(hex2)
    else:
        # Otherwise, pick two random colors from the main palette.
        hex1, hex2 = random.sample(CRUELTY_SQUAD_PALETTE, 2)
        color1, color2 = hex_to_rgb(hex1), hex_to_rgb(hex2)

    # --- Image Generation ---
    text_canvas_size = (width * 8, height * 8)
    txtimg = Image.new('RGBA', text_canvas_size, (255, 255, 255, 0))

    gradient = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(3):
        gradient[:, :, i] = np.tile(np.linspace(color1[i], color2[i], height, dtype=np.uint8), (width, 1)).T
    img = Image.fromarray(gradient)

    font_path = os.path.join(c_path, "resources", "Envy Code R.ttf")
    fontsize = 1
    font = ImageFont.truetype(font_path, fontsize)
    while font.getlength(word.upper()) < text_canvas_size[0]:
        fontsize += 1
        font = ImageFont.truetype(font_path, fontsize)

    txtdraw = ImageDraw.Draw(txtimg)
    _, _, total_word_width, _ = txtdraw.textbbox((0, 0), word.upper(), font=font)
    gap_width = (text_canvas_size[0] - total_word_width) / (len(word) + 1)
    xpos = gap_width
    for letter in word.upper():
        txtdraw.text((xpos, 0), letter, (0, 0, 0), font=font)
        _, _, letter_width, _ = txtdraw.textbbox((0, 0), letter, font=font)
        xpos += letter_width + gap_width

    resize_dim, crop_box = calculate_text_dimensions(len(word), width)
    resized_text = txtimg.resize(resize_dim, Image.LANCZOS)
    cropped_text = resized_text.crop(crop_box)

    composite = Image.alpha_composite(img.convert('RGBA'), cropped_text)

    # --- Saving ---
    savepath = values.get('-FOLDER-', os.path.join(c_path, 'results'))
    os.makedirs(savepath, exist_ok=True)

    random_file_number = f'{random.randint(1, 999):03}'
    save_filename = f'{word.upper()}_{random_file_number}.png'
    save_full_path = os.path.join(savepath, save_filename)
    composite.save(save_full_path, quality=95)

    return save_full_path