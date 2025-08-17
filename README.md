<a name="readme-top"></a>
<div align="center">
  <a href="https://github.com/Leynia/PainGenerator">
    <img src="https://github.com/Leynia/PainGenerator/blob/main/resources/PAIN.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">PainGenerator</h3>

  <p align="center">
    A small Python program to generate textures based on the video game Cruelty Squad.
    <br />
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#gui-usage">GUI Usage</a></li>
    <li><a href="#web-ui-usage">Web UI Usage</a></li>
    <li><a href="#plans-for-the-future">Plans For The Future</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

![product-screenshot]

Created by Leia.

Original textures and concept from Cruelty Squad by Ville Kallio, Consummer Softproducts.

Pain Generator is a small python program which allows you to generate random images in the style of the 'PUNISHMENT' texture from the Cruelty Squad level MALL MADNESS, there is also the option for the texture to be generated based on user input.

This page is just an easy way to get the source code in case you'd like to tinker with the program and run it in your own python environment, for a fully functional .exe with no requirements needed, head to [https://crus.cc/mod/pain_generator/](https://crus.cc/mod/pain_generator/).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

- Python 3.x
- pip

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/Leynia/PainGenerator.git
    cd PainGenerator
    ```
2.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```
3.  **Download NLTK data:**
    The `nltk` package requires the `punkt` tokenizer. Run the following command in your terminal to start a Python interpreter and download the data:
    ```sh
    python -c "import nltk; nltk.download('punkt')"
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## GUI Usage

To run the desktop application, execute the `PainGenerator.py` script:

```sh
python PainGenerator.py
```

### Options

-   **Random/User Generated Checkbox**: Switch between random or user input-based generation.
-   **[User input-based mode] Word**: Word you'd like to have on the texture.
-   **[User input-based mode] Hex Value 1, 2, Reset Hex**: The color you would like to have as a gradient on the texture, must be in HEX value (Example : White = #FFFFFF), Reset Hex button resets to the basic program values (Red and Blue).
-   **[Random mode] How many images would you like to generate**: The number of image you would like to be randomly generated. 1 -> 100.
-   **[Random mode] Wordlist**: This program has three built in wordlists, "Cyberpunk AF" is a wordlist based upon William Gibson's "SPRAWL" trilogy of books. "TempleOS" is based upon the OS and writings of Terry A. Davis. "1894" is based upon the classic book "1984" by George Orwell.
-   **Output Folder**: Where you would like the images to be saved. Default folder is the "Results" folder.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Web UI Usage

This tool now includes a lightweight web interface to generate images from your browser.

1.  **Start the server:**
    ```sh
    python PainGenerator_WebUI/webui.py
    ```
2.  **Open your browser:**
    Navigate to `http://127.0.0.1:5000` to access the Web UI.

The options in the Web UI are the same as the GUI version. Generated images will be displayed on the page and saved to the `results` folder.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Discord Bot Usage

This tool also includes a Discord bot that generate such images.

### Bot Setup

1.  **Install bot requirements:**
    ```sh
    pip install -r requirements.txt
    ```
2.  **Set your Bot Token:**
    Create an environment variable named `DISCORD_BOT_TOKEN` with your bot's token. Alternatively, you can paste the token directly into `PainGenerator_Discord/bot.py` (Line 16).
3.  **Invite the Bot:**
    - Go to the "OAuth2 -> URL Generator" tab in the Discord Developer Portal.
    - Select the `bot` and `application.commands` scopes.
    - Grant `Send Messages` and `Attach Files` permissions.
    - Use the generated URL to invite the bot to your server.
4.  **Run the bot:**
    ```sh
    python PainGenerator_Discord/bot.py
    ```

### Bot Commands

-   **/setup (Admin only):** Run this command in your server to configure the bot. You can set the channel for automatic posts, the frequency, default wordlist, and default colors (or set to random).
-   **/generate:** Generates an image. You can specify the `word`, `hex` colors, and `size` as options. If you don't provide a word, a random one will be generated.
-   **/randomgen:** Generates up to 10 random images from a specified wordlist.
-   **/colorpalette:** Displays an image of the built-in Cruelty Squad color palette with hex codes.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Plans for the future

- [x] Create a Discord Bot which automatically generates images every `x` amount of time and posts it on the server.
- [x] Create a lite WebUI version of PainGenerator which can run in a website.

<!-- LICENSE -->
## License

Distributed under The Unlicense license. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Twitter - [@LeiaIsOnline](https://twitter.com/LeiaIsOnline)
</br>
Discord - Leia#4939

Project Link: [https://github.com/Leynia/PainGenerator](https://github.com/Leynia/PainGenerator)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[product-screenshot]: https://crus.cc/mod/pain_generator/image.jpg