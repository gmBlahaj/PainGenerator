from PIL import Image, ImageDraw, ImageFont, ImageTk
from nltk.tokenize import word_tokenize
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import colorsys
import numpy as np
import os
import random
import re
from typing import Tuple, List, Dict, Any
from PainGenerator_WebUI.generator import CRUELTY_SQUAD_PALETTE

# Set program path
c_path = os.path.dirname(__file__)

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
        hex_code = "".join([c*2 for c in hex_code])
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def calculate_text_dimensions(word_length: int, output_width: int) -> Tuple[Tuple[int, int], Tuple[int, int, int, int]]:
    """Calculates the resize and crop dimensions for the text image, scaled to the output size."""
    scale_factor = output_width / 128.0
    resize_y = int(np.interp(word_length, [2, 10], [160, 960]) * scale_factor)
    crop_y1 = int(np.interp(word_length, [2, 10], [24, 40]) * scale_factor)
    crop_y2 = int(np.interp(word_length, [2, 10], [152, 168]) * scale_factor)
    return (output_width, resize_y), (0, crop_y1, output_width, crop_y2)

class ColorPickerWindow(tk.Toplevel):
    def __init__(self, parent, hex_var: tk.StringVar):
        super().__init__(parent)
        self.hex_var = hex_var
        self.transient(parent)
        self.grab_set()
        self.title("Cruelty Squad Colors")
        self.configure(background='#2C001E')

        cols = 12
        btn_width_px = 25
        btn_height_px = 25
        pad = 4
        scrollbar_width = 20
        window_width = (cols * (btn_width_px + pad)) + pad + scrollbar_width
        window_height = 300
        self.geometry(f"{window_width}x{window_height}")

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame, bg='#2C001E', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, color_code in enumerate(CRUELTY_SQUAD_PALETTE):
            row, col = divmod(i, cols)
            btn_frame = tk.Frame(scrollable_frame, bg=color_code, width=btn_width_px, height=btn_height_px)
            btn_frame.grid(row=row, column=col, padx=2, pady=2)
            btn_frame.bind("<Button-1>", lambda e, c=color_code: self.select_color(c))

        canvas.pack(side="left", fill="both", expand=True, padx=(5,0), pady=5)
        scrollbar.pack(side="right", fill="y", padx=(0,5), pady=5)

    def select_color(self, color_code: str):
        self.hex_var.set(color_code)
        self.destroy()

class PainGeneratorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PAIN GENERATOR v1.00")
        self.iconphoto(True, tk.PhotoImage(file=os.path.join(c_path, 'resources', 'PAIN.png')))
        self.resizable(True, True) # Make window resizable
        self.minsize(600, 500) # Set a minimum size

        # Configure grid layout to expand
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_style()

        self.is_random_var = tk.BooleanVar()
        self.word_var = tk.StringVar()
        self.hex1_var = tk.StringVar()
        self.hex2_var = tk.StringVar()
        self.spin_var = tk.StringVar(value='1')
        self.folder_var = tk.StringVar(value=os.path.join(c_path, 'results'))
        self.wordlist_var = tk.StringVar(value='Cyberpunk AF')
        self.size_var = tk.StringVar(value='128x128')

        self.create_widgets()
        self.toggle_mode()

    def setup_style(self):
        BG_COLOR = '#2C001E'
        FG_COLOR = '#FFFFFF'
        INPUT_BG = '#5A003D'
        BUTTON_BG = '#5A003D'
        ACCENT_COLOR = '#01d28e'
        SELECT_BG = '#7A2A5F'

        self.configure(background=BG_COLOR)
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('.', background=BG_COLOR, foreground=FG_COLOR, fieldbackground=INPUT_BG, borderwidth=0, lightcolor=BG_COLOR, darkcolor=BG_COLOR)
        style.configure('TFrame', background=BG_COLOR)
        style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR)
        style.configure('TCheckbutton', background=BG_COLOR, foreground=FG_COLOR, indicatorbackground=INPUT_BG)
        style.map('TCheckbutton', background=[('active', BG_COLOR)], indicatorcolor=[('selected', FG_COLOR), ('!selected', INPUT_BG)])
        style.configure('TEntry', fieldbackground=INPUT_BG, foreground=FG_COLOR, insertcolor=FG_COLOR, borderwidth=0)
        style.configure('TSpinbox', fieldbackground=INPUT_BG, foreground=FG_COLOR, arrowcolor=FG_COLOR, borderwidth=0)
        style.map('TSpinbox', background=[('readonly', BG_COLOR)])
        style.configure('TCombobox', fieldbackground=INPUT_BG, foreground=FG_COLOR, borderwidth=0, arrowcolor=FG_COLOR, selectbackground=SELECT_BG, selectforeground=FG_COLOR)
        style.map('TCombobox', fieldbackground=[('readonly', INPUT_BG)], selectbackground=[('readonly', SELECT_BG)], selectforeground=[('readonly', FG_COLOR)])
        self.option_add('*TCombobox*Listbox.background', INPUT_BG)
        self.option_add('*TCombobox*Listbox.foreground', FG_COLOR)
        self.option_add('*TCombobox*Listbox.selectBackground', SELECT_BG)
        self.option_add('*TCombobox*Listbox.selectForeground', FG_COLOR)
        style.configure('TButton', background=BUTTON_BG, foreground=FG_COLOR, padding=5, borderwidth=0)
        style.map('TButton', background=[('active', SELECT_BG)])
        style.configure('Accent.TButton', foreground="black", background=ACCENT_COLOR, padding=5)
        style.map('Accent.TButton', background=[('active', '#01b87a')])
        style.configure("Vertical.TScrollbar", background=BUTTON_BG, troughcolor=BG_COLOR, bordercolor=BG_COLOR, arrowcolor=FG_COLOR)
        style.map("Vertical.TScrollbar", background=[('active', SELECT_BG)])

        # Styles for the new mode indicator label
        style.configure('Random.TLabel', background=INPUT_BG, foreground='#FF0000', anchor='center', font=('Courier', 12, 'bold'))
        style.configure('User.TLabel', background=INPUT_BG, foreground=ACCENT_COLOR, anchor='center', font=('Courier', 12, 'bold'))

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="25")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2) # Give image frame more space
        main_frame.grid_rowconfigure(0, weight=1)

        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        left_frame.grid_columnconfigure(0, weight=1) # Allow widgets to expand horizontally

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # --- Left Frame Widgets ---
        self.mode_indicator_label = ttk.Label(left_frame, text="")
        self.mode_indicator_label.grid(row=0, column=0, columnspan=5, sticky=tk.EW, pady=(0, 15))

        ttk.Checkbutton(left_frame, text="Random/User Generated", variable=self.is_random_var, command=self.toggle_mode).grid(row=1, column=0, columnspan=5, sticky=tk.W, pady=(0, 10))
        ttk.Label(left_frame, text="Word").grid(row=2, column=0, columnspan=5, sticky=tk.W)
        self.word_entry = ttk.Entry(left_frame, textvariable=self.word_var)
        self.word_entry.grid(row=3, column=0, columnspan=5, sticky=tk.EW, pady=(0,10))

        hex_frame = ttk.Frame(left_frame)
        hex_frame.grid(row=4, column=0, columnspan=5, sticky=tk.W)
        ttk.Label(hex_frame, text="Hex Value 1").grid(row=0, column=0, sticky=tk.W)
        self.hex1_entry = ttk.Entry(hex_frame, textvariable=self.hex1_var, width=10)
        self.hex1_entry.grid(row=1, column=0, sticky=tk.W)
        ttk.Button(hex_frame, text="Pick", width=4, command=lambda: self.pick_color(self.hex1_var)).grid(row=1, column=1, sticky=tk.W, padx=2)
        ttk.Label(hex_frame, text="Hex Value 2").grid(row=0, column=2, sticky=tk.W, padx=(10,0))
        self.hex2_entry = ttk.Entry(hex_frame, textvariable=self.hex2_var, width=10)
        self.hex2_entry.grid(row=1, column=2, sticky=tk.W, padx=(10,0))
        ttk.Button(hex_frame, text="Pick", width=4, command=lambda: self.pick_color(self.hex2_var)).grid(row=1, column=3, sticky=tk.W, padx=2)
        
        ttk.Button(left_frame, text="Reset Hex", command=self.reset_hex).grid(row=5, column=0, columnspan=5, sticky=tk.W, pady=(5,10))
        ttk.Label(left_frame, text="How many images?").grid(row=6, column=0, columnspan=5, sticky=tk.W)
        self.spinbox = ttk.Spinbox(left_frame, from_=1, to=100, textvariable=self.spin_var, width=5)
        self.spinbox.grid(row=7, column=0, columnspan=5, sticky=tk.W, pady=(0,10))
        ttk.Label(left_frame, text="Image Size").grid(row=8, column=0, columnspan=5, sticky=tk.W)
        self.size_combo = ttk.Combobox(left_frame, textvariable=self.size_var, values=['128x128', '256x256', '512x512', '1024x1024'], state='readonly', width=10)
        self.size_combo.grid(row=9, column=0, columnspan=5, sticky=tk.W, pady=(0,10))

        ttk.Label(left_frame, text="Output Folder").grid(row=10, column=0, columnspan=5, sticky=tk.W)
        folder_frame = ttk.Frame(left_frame)
        folder_frame.grid(row=11, column=0, columnspan=5, sticky=tk.EW)
        folder_frame.columnconfigure(0, weight=1)
        ttk.Entry(folder_frame, textvariable=self.folder_var).grid(row=0, column=0, sticky=tk.EW)
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1, sticky=tk.W, padx=(5,0))

        ttk.Button(left_frame, text="GENERATE", command=self.generate, style="Accent.TButton").grid(row=12, column=0, columnspan=5, pady=10, sticky=tk.EW)

        # --- Right Frame Widgets ---
        self.img = ImageTk.PhotoImage(Image.open(os.path.join(c_path, "resources", "PAIN.png")))
        self.image_label = ttk.Label(right_frame, image=self.img, anchor="center")
        self.image_label.grid(row=0, column=0, columnspan=2, sticky="nsew")

        wordlist_frame = ttk.Frame(right_frame)
        wordlist_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5,0))
        wordlist_frame.columnconfigure(0, weight=1) # Push combo to the right
        ttk.Label(wordlist_frame, text="WORDLIST:").grid(row=0, column=0, sticky=tk.E, padx=(0,5))
        self.wordlist_combo = ttk.Combobox(wordlist_frame, textvariable=self.wordlist_var, values=['Cyberpunk AF', 'TempleOS', '1894'], state='readonly', width=15)
        self.wordlist_combo.grid(row=0, column=1, sticky=tk.W)

        ttk.Button(right_frame, text="EXIT", command=self.destroy, style="Accent.TButton").grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.EW)

    def pick_color(self, hex_var: tk.StringVar):
        ColorPickerWindow(self, hex_var)

    def toggle_mode(self):
        is_user_generated = self.is_random_var.get()
        
        if is_user_generated:
            self.mode_indicator_label.config(text="-- USER GENERATED --", style='User.TLabel')
        else:
            self.mode_indicator_label.config(text="-- RANDOM --", style='Random.TLabel')

        self.word_entry.config(state="normal" if is_user_generated else "disabled")
        self.hex1_entry.config(state="normal" if is_user_generated else "disabled")
        self.hex2_entry.config(state="normal" if is_user_generated else "disabled")
        self.spinbox.config(state="disabled" if is_user_generated else "normal")
        self.wordlist_combo.config(state="disabled" if is_user_generated else "readonly")
        
        if is_user_generated:
            self.word_var.set("PAIN")
            self.reset_hex()
        else:
            self.word_var.set("")
            self.hex1_var.set("")
            self.hex2_var.set("")

    def reset_hex(self):
        self.hex1_var.set("#FF0000")
        self.hex2_var.set("#0000FF")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def generate(self):
        values = {
            '-CHECKBOX-': self.is_random_var.get(), '-WORD-': self.word_var.get(),
            '-HEX1-': self.hex1_var.get(), '-HEX2-': self.hex2_var.get(),
            '-SPIN-': self.spin_var.get(), '-FOLDER-': self.folder_var.get(),
            '-WORDLIST-': self.wordlist_var.get(), '-SIZE-': self.size_var.get()
        }
        self.generate_images(values)

    def generate_images(self, values: Dict[str, Any]):
        try:
            times_to_run = 1 if values['-CHECKBOX-'] else int(values['-SPIN-'])
        except ValueError:
            messagebox.showerror("ERROR", "Incorrect input for number of images.")
            self.spin_var.set('1')
            return

        if not 1 <= times_to_run <= 100:
            messagebox.showerror("ERROR", "Number is too small or too large. Range = 1 -> 100")
            self.spin_var.set('1')
            return
        
        try:
            width, height = map(int, values['-SIZE-'].split('x'))
        except ValueError:
            messagebox.showerror("ERROR", "Invalid image size selected.")
            return

        for _ in range(times_to_run):
            if values['-CHECKBOX-']:
                word = values['-WORD-']
                if not 2 <= len(word) <= 10:
                    messagebox.showerror("ERROR", "Word is too small or too large. Range = 2 -> 10 letters")
                    break
                hex1, hex2 = values['-HEX1-'], values['-HEX2-']
                if not (is_valid_hex_code(hex1) and is_valid_hex_code(hex2)):
                    messagebox.showerror("ERROR", "Hex value is incorrect")
                    break
                color1, color2 = hex_to_rgb(hex1), hex_to_rgb(hex2)
            else:
                wordlist_map = {'Cyberpunk AF': 'SPRAWL', 'TempleOS': 'TempleOS', '1894': '1894'}
                chosen_wordlist = values['-WORDLIST-']
                wordlist_key = wordlist_map.get(chosen_wordlist)
                word = random.choice(wordlists.get(wordlist_key, ["DEFAULT"]))
                hex1, hex2 = random.sample(CRUELTY_SQUAD_PALETTE, 2)
                color1, color2 = hex_to_rgb(hex1), hex_to_rgb(hex2)

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

            random_file_number = f'{random.randint(1, 999):03}'
            composite = Image.alpha_composite(img.convert('RGBA'), cropped_text)
            
            savepath = values['-FOLDER-']
            if not os.path.exists(savepath):
                os.makedirs(savepath, exist_ok=True)
                self.folder_var.set(savepath)

            save_filename = f'{word.upper()}_{random_file_number}.png'
            save_full_path = os.path.join(savepath, save_filename)
            composite.save(save_full_path, quality=95)
            
            display_img = Image.open(save_full_path)
            display_img.thumbnail((self.image_label.winfo_width(), self.image_label.winfo_height()))
            new_img = ImageTk.PhotoImage(display_img)
            self.image_label.config(image=new_img)
            self.image_label.image = new_img

if __name__ == "__main__":
    app = PainGeneratorGUI()
    app.mainloop()
