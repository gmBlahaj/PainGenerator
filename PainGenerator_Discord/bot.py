import discord
from discord import app_commands
from discord.ext import tasks
import os
import sys
import random
import json
import time
from typing import Literal, Optional
from PIL import Image, ImageDraw, ImageFont
import asyncio


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PainGenerator_WebUI import generator


DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
CONFIG_FILE = 'server_configs.json'


intents = discord.Intents.default()
intents.guilds = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


server_configs = {}

def load_configs():
    global server_configs
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            server_configs = {str(k): v for k, v in json.load(f).items()}
    else:
        server_configs = {}

def save_configs():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(server_configs, f, indent=4)

def get_guild_config(guild_id: int):
    guild_id_str = str(guild_id)
    if guild_id_str not in server_configs:
        server_configs[guild_id_str] = {
            "target_channel_id": None, "frequency_hours": 3,
            "default_wordlist": "Cyberpunk AF", "last_posted_timestamp": 0,
            "hex1": None, "hex2": None, "random_colors": True
        }
    server_configs[guild_id_str].setdefault("hex1", None)
    server_configs[guild_id_str].setdefault("hex2", None)
    server_configs[guild_id_str].setdefault("random_colors", True)
    return server_configs[guild_id_str]


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    load_configs()
    print(f'Loaded configs for {len(server_configs)} servers.')
    print('Syncing command tree...')
    await tree.sync()
    print('Command tree synced.')
    auto_post_task.start()


@tree.command(name='setup', description='Configure the bot for this server (Admins only).')
@app_commands.describe(
    channel='The channel where automatic images will be posted.',
    frequency='How often to post a random image (in hours).',
    wordlist='The default wordlist for random generation.',
    random_colors='Set to True for random colors, False to use specific hex values.',
    hex1='The first default hex color for automatic posts (e.g., #FF0000).',
    hex2='The second default hex color for automatic posts (e.g., #0000FF).'
)
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction, channel: discord.TextChannel, frequency: app_commands.Range[int, 1, 168],
                wordlist: Literal['Cyberpunk AF', 'TempleOS', '1894'], random_colors: bool = True,
                hex1: Optional[str] = None, hex2: Optional[str] = None):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    if not random_colors and (not hex1 or not hex2):
        await interaction.response.send_message("If `random_colors` is False, you must provide both `hex1` and `hex2`.", ephemeral=True)
        return
    if hex1 and not generator.is_valid_hex_code(hex1):
        await interaction.response.send_message(f"Invalid hex code for `hex1`: {hex1}", ephemeral=True)
        return
    if hex2 and not generator.is_valid_hex_code(hex2):
        await interaction.response.send_message(f"Invalid hex code for `hex2`: {hex2}", ephemeral=True)
        return

    config = get_guild_config(interaction.guild.id)
    config.update({
        'target_channel_id': channel.id, 'frequency_hours': frequency,
        'default_wordlist': wordlist, 'random_colors': random_colors,
        'hex1': hex1 if not random_colors else None,
        'hex2': hex2 if not random_colors else None
    })
    save_configs()
    color_status = "Random from Palette" if random_colors else f"{hex1} & {hex2}"
    await interaction.response.send_message(
        f"Configuration updated!\n"
        f"- Posts will be sent to **#{channel.name}** every **{frequency}** hour(s).\n"
        f"- Default wordlist: **{wordlist}**.\n"
        f"- Default colors: **{color_status}**.",
        ephemeral=True
    )

@tree.command(name='generate', description='Generates a PAIN image.')
@app_commands.describe(word='The word to display (2-10 letters). Omit for a random word.',
                       hex1='The first hex color (e.g., #FF0000). Omit for random.',
                       hex2='The second hex color (e.g., #0000FF). Omit for random.',
                       size='The size of the image.')
async def generate_cmd(interaction: discord.Interaction, size: Literal['128x128', '256x256', '512x512', '1024x1024'] = '256x256',
                       word: Optional[str] = None, hex1: Optional[str] = None, hex2: Optional[str] = None):
    await interaction.response.defer()
    try:
        config = get_guild_config(interaction.guild.id) if interaction.guild else get_guild_config(0)
        values = {
            '-CHECKBOX-': bool(word or hex1 or hex2), '-SIZE-': size,
            '-WORDLIST-': config['default_wordlist'], '-WORD-': word,
            '-HEX1-': hex1, '-HEX2-': hex2,
        }
        image_path = generator.generate_image(values)
        await interaction.followup.send(file=discord.File(image_path))
        os.remove(image_path)
    except ValueError as e:
        await interaction.followup.send(f"Error: {e}")
    except Exception as e:
        await interaction.followup.send(f"An unexpected error occurred: {e}")

@tree.command(name='randomgen',
              description='Generates multiple random images.')
@app_commands.describe(
    quantity='The number of images to generate (1-10).',
    wordlist='The wordlist to use for random words.',
    size='The size of the generated images.'
)
async def randomgen(
    interaction: discord.Interaction,
    quantity: app_commands.Range[int, 1, 10],
    wordlist: Literal['Cyberpunk AF', 'TempleOS', '1894'],
    size: Literal['128x128', '256x256', '512x512', '1024x1024'] = '256x256'
):
    await interaction.response.defer()
    await interaction.followup.send(f"Generating {quantity} random images from the `{wordlist}` wordlist at {size}...")
    for i in range(quantity):
        try:
            values = {'-CHECKBOX-': False, '-WORDLIST-': wordlist, '-SIZE-': size}
            image_path = generator.generate_image(values)
            await interaction.channel.send(f"Image {i+1}/{quantity}", file=discord.File(image_path))
            os.remove(image_path)
        except Exception as e:
            await interaction.channel.send(f"Failed to generate image {i+1}: {e}")
        await asyncio.sleep(1)

@tree.command(name='colorpalette', description='Displays the Cruelty Squad color palette.')
async def colorpalette(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        cols = 12
        swatch_size = 60
        text_h = 20
        padding = 5
        font_path = os.path.join(generator.c_path, "resources", "Envy Code R.ttf")
        font = ImageFont.truetype(font_path, 14)
        bg_color = '#2C001E'

        num_colors = len(generator.CRUELTY_SQUAD_PALETTE)
        rows = (num_colors + cols - 1) // cols
        img_w = cols * (swatch_size + padding) + padding
        img_h = rows * (swatch_size + text_h + padding) + padding
        
        img = Image.new('RGB', (img_w, img_h), bg_color)
        draw = ImageDraw.Draw(img)

        for i, color_hex in enumerate(generator.CRUELTY_SQUAD_PALETTE):
            row, col = divmod(i, cols)
            x = col * (swatch_size + padding) + padding
            y = row * (swatch_size + text_h + padding) + padding
            draw.rectangle([x, y, x + swatch_size, y + swatch_size], fill=color_hex)
            
            text_x = x + swatch_size / 2
            text_y = y + swatch_size + text_h / 2
            draw.text((text_x, text_y), color_hex, fill='#FFFFFF', font=font, anchor='mm')

        palette_path = os.path.join(generator.c_path, 'results', 'palette.png')
        os.makedirs(os.path.dirname(palette_path), exist_ok=True)
        img.save(palette_path)
        await interaction.followup.send(file=discord.File(palette_path), ephemeral=True)
        os.remove(palette_path)
    except Exception as e:
        await interaction.followup.send(f"An error occurred while generating the palette: {e}")


@tasks.loop(minutes=5)
async def auto_post_task():
    current_time = time.time()
    for guild_id_str, config in server_configs.items():
        if not all(k in config for k in ['target_channel_id', 'frequency_hours', 'last_posted_timestamp']):
            continue
        
        frequency_seconds = config['frequency_hours'] * 3600
        if (current_time - config['last_posted_timestamp']) > frequency_seconds:
            channel = bot.get_channel(config['target_channel_id'])
            if channel:
                try:
                    print(f"Posting automatic image to '{channel.guild.name}'...")
                    values = {
                        '-CHECKBOX-': not config.get('random_colors', True),
                        '-WORDLIST-': config['default_wordlist'], '-SIZE-': '256x256',
                        '-HEX1-': config.get('hex1'), '-HEX2-': config.get('hex2'),
                    }
                    image_path = generator.generate_image(values)
                    await channel.send(file=discord.File(image_path))
                    os.remove(image_path)
                    config['last_posted_timestamp'] = current_time
                except Exception as e:
                    print(f"Failed to post to '{channel.guild.name}': {e}")
    save_configs()

@auto_post_task.before_loop
async def before_auto_post_task():
    await bot.wait_until_ready()


if __name__ == "__main__":
    if DISCORD_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("ERROR: Please set your DISCORD_BOT_TOKEN.")
    else:
        bot.run(DISCORD_BOT_TOKEN)
