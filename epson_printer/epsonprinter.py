import math
import io
import base64
import numpy as np
import usb.core
from functools import wraps
from PIL import Image

ESC = 27
GS = 29
FULL_PAPER_CUT = [GS, 86, 0]
UNDERLINE_OFF = [ESC, 45, 0]
BOLD_ON = [ESC, 69, 1]
BOLD_OFF = [ESC, 69, 0]
DEFAULT_LINE_SPACING = [ESC, 50]
CENTER = [ESC, 97, 1]
LEFT_JUSTIFIED = [ESC, 97, 0]
RIGHT_JUSTIFIED = [ESC, 97, 2]

def linefeed(lines=1):
    return [ESC, 100, lines]

def underline_on(weight):
    return [ESC, 45, weight]

def set_line_spacing(dots):
    return [ESC, 51, dots]

def set_text_size(width_magnification, height_magnification):
    if width_magnification < 0 or width_magnification > 7:
        raise Exception("Width magnification should be between 0(x1) and 7(x8)")
    if height_magnification < 0 or height_magnification > 7:
        raise Exception("Height magnification should be between 0(x1) and 7(x8)")
    n = 16 * width_magnification + height_magnification
    return [GS, 33, n]

def set_print_speed(speed):
    return [GS, 40, 75, 2, 0, 50, speed]

class PrintableImage:
    MAX_WIDTH = 440  # Define the maximum width as a class attribute
    OFFSET = -200       # Define the offset as a class attribute

    def __init__(self, data, height):
        self.data = data
        self.height = height

    @classmethod
    def from_image(cls, image):
        # Get the original dimensions of the image
        (w, h) = image.size
        print(f"Original image size: width={w}, height={h}")

        # Resize the image if its width is greater than the maximum width
        if w > cls.MAX_WIDTH:
            ratio = cls.MAX_WIDTH / w  # Calculate the scaling ratio to resize the width to MAX_WIDTH
            h = int(h * ratio)  # Adjust the height to maintain the aspect ratio
            image = image.resize((cls.MAX_WIDTH, h), Image.ANTIALIAS)
            print(f"Resized image size: width={cls.MAX_WIDTH}, height={h}")
            w = cls.MAX_WIDTH  # Update the width after resizing

        # Convert the image to black and white mode if it is not already
        if image.mode != '1':
            image = image.convert('1')
            print("Converted image to mode '1' (black and white)")

        # Convert the image data to a numpy array
        pixels = np.array(list(image.getdata()))
        print(f"Total number of pixels: {pixels.size}")

        try:
            pixels = pixels.reshape(h, w)
            print(f"Reshaped pixels to: height={h}, width={w}")
        except ValueError as e:
            print(f"Error reshaping pixels: {e}")
            raise

        # Calculate the padding needed to center the image
        total_width = cls.MAX_WIDTH  # Total width of the printable area
        if w < total_width:
            padding_left = max((total_width - w) // 2 + cls.OFFSET, 0)
            padding_right = total_width - w - padding_left
            # Add padding to the left and right
            print(f"Padding: left={padding_left}, right={padding_right}")
            padded_pixels = np.pad(pixels, ((0, 0), (padding_left, padding_right)), 'constant', constant_values=1)
            pixels = padded_pixels
            w = total_width  # Update the width to the total width
            print(f"New width after padding: {w}")

        # Calculate the number of extra rows needed to make the height a multiple of 24
        extra_rows = int(math.ceil(h / 24)) * 24 - h
        print(f"Extra rows needed to make height a multiple of 24: {extra_rows}")

        # Create extra rows filled with white pixels (represented by True)
        extra_pixels = np.ones((extra_rows, w), dtype=bool)

        # Add the extra rows to the pixel array
        pixels = np.vstack((pixels, extra_pixels))
        h += extra_rows  # Update the height to include the extra rows
        print(f"Adjusted image size with extra rows: height={h}")

        # Calculate the number of stripes (each stripe is 24 pixels high)
        nb_stripes = h // 24
        print(f"Number of stripes (24 pixels each): {nb_stripes}")

        # Reshape the pixel array into stripes, then invert and pack the bits
        pixels = pixels.reshape(nb_stripes, 24, w).swapaxes(1, 2).reshape(-1, 8)
        pixels = np.invert(np.packbits(pixels))

        data = []
        # Split the pixel array into individual stripes
        stripes = np.split(pixels, nb_stripes)
        for stripe in stripes:
            # Add the ESC/POS command to print a stripe
            data.extend([ESC, 42, 33, w % 256, w // 256])
            # Add the stripe data
            data.extend(stripe)
            # Add the ESC/POS command to feed paper
            data.extend([27, 74, 48])

        height = h * 2  # Calculate the total height in printer units
        return cls(data, height)  # Create and return a PrintableImage object

    def append(self, other):
        # Append another PrintableImage's data to this one
        self.data.extend(other.data)
        self.height += other.height
        return self

class EpsonPrinter:
    def __init__(self, id_vendor, id_product, out_ep=0x01):
        self.out_ep = out_ep
        self.printer = usb.core.find(idVendor=id_vendor, idProduct=id_product)
        if self.printer is None:
            raise ValueError("Printer not found. Make sure the cable is plugged in.")
        if self.printer.is_kernel_driver_active(0):
            try:
                self.printer.detach_kernel_driver(0)
            except usb.core.USBError as e:
                print("Could not detach kernel driver: %s" % str(e))
        try:
            self.printer.set_configuration()
            self.printer.reset()
        except usb.core.USBError as e:
            print("Could not set configuration: %s" % str(e))

    def write_this(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            byte_array = func(self, *args, **kwargs)
            self.write_bytes(byte_array)
        return wrapper

    def write_bytes(self, byte_array):
        self.printer.write(self.out_ep, byte_array, timeout=20000)

    def write(self, msg):
        self.printer.write(self.out_ep, msg.encode('utf-8'), timeout=20000)

    def print_text(self, msg):
        self.write(msg)

    @write_this
    def linefeed(self, lines=1):
        return linefeed(lines)

    @write_this
    def cut(self):
        return FULL_PAPER_CUT

    @write_this
    def print_image(self, printable_image):
        dyl = printable_image.height % 256
        dyh = int(printable_image.height / 256)
        byte_array = [ESC, 87, 46, 0, 0, 0, 0, 2, dyl, dyh]
        byte_array.extend([27, 76])
        byte_array.extend(printable_image.data)
        byte_array.append(12)
        return byte_array

    def print_images(self, *printable_images):
        from functools import reduce
        printable_image = reduce(lambda x, y: x.append(y), list(printable_images))
        self.print_image(printable_image)

    def print_image_from_file(self, image_file, rotate=False):
        image = Image.open(image_file)
        if rotate:
            image = image.rotate(180)
        printable_image = PrintableImage.from_image(image)
        self.print_image(printable_image)

    def print_image_from_buffer(self, data, rotate=False):
        image = Image.open(io.BytesIO(base64.b64decode(data)))
        if rotate:
            image = image.rotate(180)
        printable_image = PrintableImage.from_image(image)
        self.print_image(printable_image)

    @write_this
    def underline_on(self, weight=1):
        return underline_on(weight)

    @write_this
    def underline_off(self):
        return UNDERLINE_OFF

    @write_this
    def bold_on(self):
        return BOLD_ON

    @write_this
    def bold_off(self):
        return BOLD_OFF

    @write_this
    def set_line_spacing(self, dots):
        return set_line_spacing(dots)

    @write_this
    def set_default_line_spacing(self):
        return DEFAULT_LINE_SPACING

    @write_this
    def set_text_size(self, width_magnification, height_magnification):
        return set_text_size(width_magnification, height_magnification)

    @write_this
    def center(self):
        return CENTER

    @write_this
    def left_justified(self):
        return LEFT_JUSTIFIED

    @write_this
    def right_justified(self):
        return RIGHT_JUSTIFIED

    @write_this
    def set_print_speed(self, speed):
        return set_print_speed(speed)
