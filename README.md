Python library for EPSON thermal printers
====================

A python library to control thermal printers based on the ESC/POS language as defined by Epson.

### Installation
Clone the project
```
git clone https://github.com/cafeciaojoe/python-epson-printer
```
Install dependencies
```
cd python-epson-printer
sudo python setup.py install
```
Connect your EPSON thermal printer via a USB port and run
```
lsusb
Bus 001 Device 005: ID 04b8:0e03 Seiko Epson Corp.
```
Write down the vendor_id and the product_id and pass them as arguments to the test page
```
sudo python -m epson_printer.testpage -v 0x04b8 -p 0x0202
```
### note
numpy needed to be installed manually with pip in the conda environment
```
pip install numpy
```

pyusb needed to be installed manually with conda-forge in the conda environment
```
conda install -c conda-forge pyusb
```

If the backend is still not found, you may need to set the LIBUSB_PATH environment variable to point to the libusb library.
```
find / -name "libusb-1.0.so" 2>/dev/null
```

kagi coda assistant was guiding me thru this. 





### Devices
The library should work with all ESC/POS-based Epson printers but it has only been tested with a TM-T20. If you have tested
the library with a different model, please add it to the [list of supported printers](https://github.com/benoitguigal/python-epson-printer/wiki/List-of-supported-printers)

### ESC/POS commands

##### Print commands
* print text
* feed lines

##### Character commands
* Left, right or centered justified
* Bold ON/OFF
* Underline ON/OFF
* Font size

##### Bit image commands
* print arbitrary long bitmap pixels array

##### Hardware commands
* full paper cut



### Credits
* [python-escpos code on google](https://code.google.com/p/python-escpos/)
* [sending-a-bit-image-to-an-epson-tm-t88iii-receipt-printer-using-c-and-escpos blog post](http://nicholas.piasecki.name/blog/2009/12/sending-a-bit-image-to-an-epson-tm-t88iii-receipt-printer-using-c-and-escpos/)

