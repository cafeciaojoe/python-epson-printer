# Run the following (you cant run this script direct, mac does not give you usb access)
# sudo python -m epson_printer.print_checklist -v 0x04b8 -p 0x0202

from .epsonprinter import EpsonPrinter
from optparse import OptionParser
import sys
import os

import textwrap
import re

preprint_space = 4
postprint_space = 4 #minimum of 4

def format_and_print_checklist(printer, checklist_file):
    import textwrap

    with open(checklist_file, 'r') as file:
        lines = file.readlines()

    max_line_width = 40  # Adjust this width based on your printer's capabilities

    for line in lines:
        stripped_line = line.strip()
        
        # Skip empty lines
        if not stripped_line:
            continue
        
        # Calculate the indentation level based on leading spaces
        leading_spaces = len(line) - len(line.lstrip())
        indentation_level = leading_spaces // 4  # Each level is 4 spaces
        indent = "  " * indentation_level  # Indentation for sub-items

        # Apply formatting based on content
        if stripped_line.startswith("#"):  # Title
            printer.center()
            printer.bold_on()
            printer.print_text(stripped_line.lstrip("#").strip())
            printer.bold_off()
            printer.left_justified()
            printer.linefeed()
        else:  # Main points and sub-items
            # Wrap text to the maximum line width, considering indentation
            wrapped_lines = textwrap.wrap(stripped_line, width=max_line_width - len(indent))
            for wrapped_line in wrapped_lines:
                printer.left_justified()
                printer.print_text(indent + wrapped_line)
                printer.linefeed()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-v", "--idvendor", action="store", type="int", dest="id_vendor", help="The printer vendor id")
    parser.add_option("-p", "--idProduct", action="store", type="int", dest="id_product", help="The printer product id")
    options, args = parser.parse_args()

    if not options.id_vendor or not options.id_product:
        parser.print_help()
        sys.exit(1)

    # Dynamically determine the absolute path of the checklist file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    checklist_file = os.path.join(script_dir, "checklist.txt")

    printer = EpsonPrinter(options.id_vendor, options.id_product)

    printer.linefeed(preprint_space)
    format_and_print_checklist(printer, checklist_file)

    printer.linefeed(postprint_space)
    printer.cut()
