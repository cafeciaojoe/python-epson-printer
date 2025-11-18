import os
from .epsonprinter import EpsonPrinter
from optparse import OptionParser
from PIL import Image

def list_png_files(directory):
    """List all PNG files in the given directory."""
    return [f for f in os.listdir(directory) if f.lower().endswith('.png')]

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

    # List all PNG files in the directory
    png_files = list_png_files(current_dir)
    if not png_files:
        print("No PNG files found in the current directory.")
        return

    # Display the list of PNG files
    print("Available PNG files:")
    for idx, file in enumerate(png_files):
        print(f"{idx + 1}. {file}")

    # Prompt the user to select a file
    try:
        choice = int(input("Enter the number of the image you want to print: ")) - 1
        if choice < 0 or choice >= len(png_files):
            print("Invalid choice.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    selected_file = png_files[choice]
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