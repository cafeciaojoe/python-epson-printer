# Run the following (you can't run this script directly, mac does not give you USB access)
# sudo python -m epson_printer.print_ascii_art -v 0x04b8 -p 0x0202


from PIL import Image

# Function to convert image to ASCII
def image_to_ascii(image_path, width=100):
    chars = "@%#*+=-:. "  # ASCII characters from dark to light
    img = Image.open(image_path)
    aspect_ratio = img.height / img.width
    new_height = int(aspect_ratio * width * 0.55)
    img = img.resize((width, new_height))
    img = img.convert("L")  # Convert to grayscale

    ascii_art = ""
    for pixel_value in img.getdata():
        # Ensure the index is within bounds
        ascii_art += chars[min(pixel_value // 25, len(chars) - 1)]
    ascii_art = "\n".join(
        [ascii_art[i:i + width] for i in range(0, len(ascii_art), width)]
    )
    return ascii_art

# Usage
ascii_art = image_to_ascii("logo.png", width=80)
print(ascii_art)