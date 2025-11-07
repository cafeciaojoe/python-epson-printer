# Run the following (you can't run this script directly, mac does not give you USB access)
# sudo python -m epson_printer.checklist -v 0x04b8 -p 0x0202

from .epsonprinter import EpsonPrinter
from optparse import OptionParser
import sys
import os
import textwrap

def print_user_input(printer):
    max_line_width = 40  # Adjust this width based on your printer's capabilities

    print("Type your text below. Press Enter to print the line. Type 'exit' to quit.")
    while True:
        user_input = input("> ").strip()
        
        if user_input.lower() == "exit":
            break
        
        if not user_input:
            continue  # Skip empty input
        
        # Apply formatting based on content
        if user_input.startswith("#"):  # Title
            printer.center()
            printer.bold_on()
            printer.print_text(user_input.lstrip("#").strip())
            printer.bold_off()
            printer.left_justified()
            printer.linefeed()
        else:  # Regular text
            # Wrap text to the maximum line width
            wrapped_lines = textwrap.wrap(user_input, width=max_line_width)
            for wrapped_line in wrapped_lines:
                printer.left_justified()
                printer.print_text(wrapped_line)
                printer.linefeed()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-v", "--idvendor", action="store", type="int", dest="id_vendor", help="The printer vendor id")
    parser.add_option("-p", "--idProduct", action="store", type="int", dest="id_product", help="The printer product id")
    options, args = parser.parse_args()

    if not options.id_vendor or not options.id_product:
        parser.print_help()
        sys.exit(1)

    printer = EpsonPrinter(options.id_vendor, options.id_product)
    print_user_input(printer)

    printer.linefeed(10)
    printer.cut()