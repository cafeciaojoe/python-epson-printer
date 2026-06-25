# Run the following (you can't run this script directly, mac does not give you USB access)
# sudo python -m epson_printer.print_png -v 0x04b8 -p 0x0202


import os
from .epsonprinter import EpsonPrinter
from optparse import OptionParser
from PIL import Image

def list_supported_image_files(directory):
    """List all image files in the given directory supported by Pillow."""
    from PIL import Image
    supported_exts = set(ext.lower() for ext in Image.registered_extensions().keys())
    return [f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in supported_exts]

def main():
    parser = OptionParser()
    parser.add_option("-v", "--idvendor", action="store", type="int", dest="id_vendor", help="The printer vendor id")
    parser.add_option("-p", "--idProduct", action="store", type="int", dest="id_product", help="The printer product id")
    options, args = parser.parse_args()

    if not options.id_vendor or not options.id_product:
        parser.print_help()
        return

    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # List all supported image files in the directory
    image_files = list_supported_image_files(current_dir)
    if not image_files:
        print("No supported image files found in the current directory.")
        return

    # Display the list of image files
    print("Available image files:")
    for idx, file in enumerate(image_files):
        print(f"{idx + 1}. {file}")

    # Prompt the user to select a file
    try:
        choice = int(input("Enter the number of the image you want to print: ")) - 1
        if choice < 0 or choice >= len(image_files):
            print("Invalid choice.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    selected_file = image_files[choice]
    print(f"Selected file: {selected_file}")

    # Initialize the printer
    printer = EpsonPrinter(options.id_vendor, options.id_product)

    # Print the selected image
    image_path = os.path.join(current_dir, selected_file)
    printer.print_image_from_file(image_path)
    printer.linefeed(10)
    printer.cut()
    print("Image printed successfully.")

if __name__ == '__main__':
    main()