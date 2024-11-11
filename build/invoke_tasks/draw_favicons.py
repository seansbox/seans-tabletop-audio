import os
import re
from invoke import task
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from .print_progress import print_progress


@task
def draw_favicons(
    c,
    symbol_name="nf-seti-audio",
    fgcolor="#FFFFFF",
    bgcolor="#F44336",
    favicon_dir="../public/ico",
    fontcss="../public/ttf/nerd-font/nerd-font.css",
    fontttf="../public/ttf/nerd-font/SymbolsNerdFont-Regular.ttf",
):
    """
    Builds all required icons (favicon, touch icons, Windows tile icon) using a symbol found in a CSS file.

    Parameters:
        c (invoke.Context): The invoke context instance.
        symbol_name (str): The symbol name to look up in the CSS file.
        fgcolor (str): Foreground color for the symbol (default is white).
        bgcolor (str): Background color for the icons (default is red).
        favicon_dir (str): Path to the directory where icons will be stored (default is "../public/ico").
        fontcss (str): Path to the CSS file defining the symbol (default is "../public/ttf/nerd-font/nerd-font.css").
        fontttf (str): Path to the TTF font file (default is "../public/ttf/nerd-font/SymbolsNerdFont-Regular.ttf").
    """
    # Set paths based on parameters
    os.makedirs(favicon_dir, exist_ok=True)

    # Function to extract Unicode character from CSS file based on symbol name
    def get_unicode_character(symbol_name):
        with open(fontcss, "r") as css_file:
            css_content = css_file.read()

        # Regex pattern to find the symbol name and its associated Unicode value
        pattern = rf"\.{symbol_name}:before\s*{{\s*content:\s*\"\\(.*?)\";"
        match = re.search(pattern, css_content)
        if not match:
            raise ValueError(f"Symbol '{symbol_name}' not found in {fontcss}")

        # Convert the Unicode hex value to a character
        unicode_hex = match.group(1)
        return chr(int(unicode_hex, 16))

    # Get the actual character to use for the icon
    try:
        symbol = get_unicode_character(symbol_name)
    except ValueError as e:
        print(e)
        return

    icon_sizes = [
        (16, "favicon-16x16.png"),
        (32, "favicon-32x32.png"),
        (48, "favicon-48x48.png"),
        (64, "favicon-64x64.png"),
        (57, "apple-touch-icon-57x57.png"),
        (72, "apple-touch-icon-72x72.png"),
        (114, "apple-touch-icon-114x114.png"),
        (120, "apple-touch-icon-120x120.png"),
        (144, "apple-touch-icon-144x144.png"),
        (152, "apple-touch-icon-152x152.png"),
        (180, "apple-touch-icon-180x180.png"),
        (144, "mstile-144x144.png", False),
    ]

    total_icons = len(icon_sizes) + 2  # 2 additional icons for favicon.ico and favicon.html

    # Function to create an anti-aliased circular background
    def create_anti_aliased_circle(size, bgcolor):
        upscale_factor = 4
        high_res_size = size * upscale_factor
        img = Image.new("RGBA", (high_res_size, high_res_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, high_res_size, high_res_size), fill=bgcolor)
        img = img.resize((size, size), Image.LANCZOS)
        return img

    # Function to create circular or square icon and save as PNG
    def create_icon(symbol, fgcolor, bgcolor, size, filename, circle_background=True):
        # Create a transparent square image
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Draw anti-aliased circle background if needed
        if circle_background:
            circle_img = create_anti_aliased_circle(size, bgcolor)
            img.paste(circle_img, (0, 0), circle_img)
        else:
            draw = ImageDraw.Draw(img)
            draw.rectangle((0, 0, size, size), fill=bgcolor)

        # Load the font and calculate text position
        try:
            font_size = int(size * 0.6)
            font = ImageFont.truetype(fontttf, font_size)
        except IOError:
            print(f"Font file not found: {fontttf}")
            return

        # Calculate text positioning to center it
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), symbol, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        text_x = (size - text_width) / 2 - 1
        text_y = (size - text_height) / 2 - 1
        text_y -= bbox[1]  # Adjust for baseline

        # Draw the symbol in the center
        draw.text((text_x, text_y), symbol, font=font, fill=fgcolor)

        # Save the image as a PNG
        img.save(os.path.join(favicon_dir, filename))

    # Create icons and show progress
    for index, (size, filename, *args) in enumerate(icon_sizes, start=1):
        print_progress(f"Creating icon {filename}...", processed=index, total=total_icons)
        circle_background = args[0] if args else True
        create_icon(symbol, fgcolor, bgcolor, size, filename, circle_background)

    # Generate multi-size ICO file
    def png_to_ico(filenames, output_ico):
        icon_images = [Image.open(os.path.join(favicon_dir, fn)) for fn in filenames]
        icon_images[0].save(
            os.path.join(favicon_dir, output_ico), format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)]
        )

    # Create a favicon.ico from various sizes
    print_progress("Creating favicon.ico...", processed=total_icons - 1, total=total_icons)
    png_to_ico(["favicon-16x16.png", "favicon-32x32.png", "favicon-48x48.png", "favicon-64x64.png"], "favicon.ico")

    print_progress("Creating favicon.html...", processed=total_icons, total=total_icons)
    # Generate HTML file for icons
    with open(os.path.join(favicon_dir, "favicon.html"), "w") as f:
        favicon_dir = favicon_dir.replace("../", "")
        f.write(
            f"""
<link rel="shortcut icon" href="{favicon_dir}/favicon.ico">
<link rel="icon" sizes="32x32" href="{favicon_dir}/favicon-32x32.png" />
<link rel="icon" sizes="16x16" href="{favicon_dir}/favicon-16x16.png" />
<link rel="apple-touch-icon-precomposed" sizes="57x57" href="{favicon_dir}/apple-touch-icon-57x57.png" />
<link rel="apple-touch-icon-precomposed" sizes="72x72" href="{favicon_dir}/apple-touch-icon-72x72.png" />
<link rel="apple-touch-icon-precomposed" sizes="114x114" href="{favicon_dir}/apple-touch-icon-114x114.png" />
<link rel="apple-touch-icon-precomposed" sizes="120x120" href="{favicon_dir}/apple-touch-icon-120x120.png" />
<link rel="apple-touch-icon-precomposed" sizes="144x144" href="{favicon_dir}/apple-touch-icon-144x144.png" />
<link rel="apple-touch-icon-precomposed" sizes="152x152" href="{favicon_dir}/apple-touch-icon-152x152.png" />
<link rel="apple-touch-icon-precomposed" sizes="180x180" href="{favicon_dir}/apple-touch-icon-180x180.png" />
<meta name="msapplication-TileColor" content="{bgcolor}" />
<meta name="msapplication-TileImage" content="{favicon_dir}/mstile-144x144.png" />
            """
        )
