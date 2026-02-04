import argparse
from inky.auto import auto
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne

# Set file Arguments
parser = argparse.ArgumentParser(description="Show image on the Inky Impression screen")
parser.add_argument(
        "filename",
        help="Path to image file to display",
)
parser.add_argument(
        "--battery",
        help="Show battery warning (default: False)",
        action='store_true'
)
args = parser.parse_args()

# Inky Setup
inky_display = auto()

# Battery warning text
font = ImageFont.truetype(FredokaOne, 28)
battery_warning = "LOW BATTERY"
_, _, w, h = font.getbbox(battery_warning)
x = (inky_display.width) - w
y = (inky_display.height) - h

# Get the image
try:
    img = Image.open(args.filename)
except:
    img = Image.open(Path(__file__).resolve().parent / "default.jpg")
im_resized = img.resize((inky_display.width, inky_display.height))

if (args.battery):
        draw = ImageDraw.Draw(im_resized)
        draw.text((x, y), battery_warning, inky_display.BLACK, font)

# Render on display
inky_display.set_image(im_resized)
inky_display.show()
