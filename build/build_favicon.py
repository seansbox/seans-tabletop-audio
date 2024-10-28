import os
import re
from invoke import task
from PIL import Image, ImageDraw, ImageFont, ImageFilter

@task
def build_favicon(c, symbol_name, fgcolor="#FFFFFF", bgcolor="#F44336", pubpath="../public"):
    """
    Builds all required icons (favicon, touch icons, Windows tile icon) using a symbol found in a CSS file.

    Parameters:
        c (invoke.Context): The invoke context instance.
        symbol_name (str): The symbol name to look up in the CSS file.
        fgcolor (str): Foreground color for the symbol (default is white).
        bgcolor (str): Background color for the icons (default is red).
        pubpath (str): Path to the public directory where icons will be stored (default is "../public").
    """
    # Set paths based on pubpath
    icon_dir = os.path.join(pubpath, "ico")
    font_path = os.path.join(pubpath, "ttf/nerd-font/SymbolsNerdFont-Regular.ttf")
    css_path = os.path.join(pubpath, "ttf/nerd-font/nerd-font.css")
    os.makedirs(icon_dir, exist_ok=True)

    # Function to extract Unicode character from CSS file based on symbol name
    def get_unicode_character(symbol_name):
        with open(css_path, "r") as css_file:
            css_content = css_file.read()
        
        # Regex pattern to find the symbol name and its associated Unicode value
        pattern = rf"\.{symbol_name}:before\s*{{\s*content:\s*\"\\(.*?)\";"
        match = re.search(pattern, css_content)
        if not match:
            raise ValueError(f"Symbol '{symbol_name}' not found in {css_path}")
        
        # Convert the Unicode hex value to a character
        unicode_hex = match.group(1)
        return chr(int(unicode_hex, 16))

    # Get the actual character to use for the icon
    try:
        symbol = get_unicode_character(symbol_name)
    except ValueError as e:
        print(e)
        return

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
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"Font file not found: {font_path}")
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
        img.save(os.path.join(icon_dir, filename))

    # Create favicon images with circular background
    create_icon(symbol, fgcolor, bgcolor, 16, "favicon-16x16.png")
    create_icon(symbol, fgcolor, bgcolor, 32, "favicon-32x32.png")
    create_icon(symbol, fgcolor, bgcolor, 48, "favicon-48x48.png")
    create_icon(symbol, fgcolor, bgcolor, 64, "favicon-64x64.png")

    # Generate multi-size ICO file
    def png_to_ico(filenames, output_ico):
        icon_images = [Image.open(os.path.join(icon_dir, fn)) for fn in filenames]
        icon_images[0].save(
            os.path.join(icon_dir, output_ico),
            format="ICO",
            sizes=[(16, 16), (32, 32), (48, 48), (64, 64)]
        )

    # Create a favicon.ico from various sizes
    png_to_ico(["favicon-16x16.png", "favicon-32x32.png", "favicon-48x48.png", "favicon-64x64.png"], "favicon.ico")

    # Create Apple touch icons in multiple sizes with circular background
    for size in [57, 72, 114, 120, 144, 152, 180]:
        create_icon(symbol, fgcolor, bgcolor, size, f"apple-touch-icon-{size}x{size}.png")

    # Create the Windows tile icon with a square background
    create_icon(symbol, fgcolor, bgcolor, 144, "mstile-144x144.png", circle_background=False)

    # Generate HTML file for icons
    with open(os.path.join(icon_dir, "favicon.html"), "w") as f:
        f.write(f"""
<link rel="shortcut icon" href="{icon_dir}/favicon.ico">
<link rel="icon" sizes="32x32" href="{icon_dir}/favicon-32x32.png" />
<link rel="icon" sizes="16x16" href="{icon_dir}/favicon-16x16.png" />
<link rel="apple-touch-icon-precomposed" sizes="57x57" href="{icon_dir}/apple-touch-icon-57x57.png" />
<link rel="apple-touch-icon-precomposed" sizes="72x72" href="{icon_dir}/apple-touch-icon-72x72.png" />
<link rel="apple-touch-icon-precomposed" sizes="114x114" href="{icon_dir}/apple-touch-icon-114x114.png" />
<link rel="apple-touch-icon-precomposed" sizes="120x120" href="{icon_dir}/apple-touch-icon-120x120.png" />
<link rel="apple-touch-icon-precomposed" sizes="144x144" href="{icon_dir}/apple-touch-icon-144x144.png" />
<link rel="apple-touch-icon-precomposed" sizes="152x152" href="{icon_dir}/apple-touch-icon-152x152.png" />
<link rel="apple-touch-icon-precomposed" sizes="180x180" href="{icon_dir}/apple-touch-icon-180x180.png" />
<meta name="msapplication-TileColor" content="{bgcolor}" />
<meta name="msapplication-TileImage" content="{icon_dir}/mstile-144x144.png" />
        """)

    #print(f"Favicons and HTML for '{symbol_name}' created successfully in '{icon_dir}'.")
