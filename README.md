BAKI is an old-school ascii editor for windows powershell and other platforms made in python.

INSTALLATION:

* Install python 3.11+ and run "python baki.py".

HOW TO RUN:

* Run "python baki.py -h" for help and keyboard commands.
If you got errors on dependencies, install all the libraries ("import" at the top of the file), like this: "pip install shutil"

HOW TO USE:

* Run "python baki.py YOUR_FILENAME.txt" to open existing files.
* Save files when exiting: press ESC and then Y. Or press N to make a copy of the file. Press ESC 2 times to exit without saving.

FEATURES:

* Selection (Ctrl + Q)
* Horizontal / vertical flipping the selection
* Cut / copy / cropping the selection
* Bulk replace characters (Ctrl + R)
* Resizing file (Ctrl + S)
* Adding picture from .txt file (Ctrl + W)
* Saving to JPG (Ctrl + D)
* GIF animation!
* Erase whole string
* Move columns up/down
* Move whole image AT CURSOR POSITION left/right
* Move whole image AT CURSOR POSITION top/down
* Shift mode 1: move characters in a row with space/backspace from current position
* Shift mode 2: move characters in a row with space/backspace from current position till the first space
* Eyedropper (Space / Ctrl + X)
* ... and more editing tools

ANIMATION HOW-TO:

* Run "python baki.py -a list.txt", where list.txt is a list of txt files (frames). Wait till each frame is rendered.
* TEXT PRINT ANIMATION run "python baki.py -at text.txt -c 5", where 'text.txt' is a file with your short text. Wait.
* MARQUEE ANIMATION: run "python baki.py -atm 'your phrase for a running string'". Wait.

* !!!IMPORTANT!!! : to make it work properly - change symbol sizes depending on your terminal font size: CHANGE cw/ch variables at the top of the file. Default is 6/12.

result.gif is an output file.

--------

More bug fixes and features are coming.

--------

TELL ME HOW IT WORKS! ESPECIALLY KEYBOARD)

Thank you.
