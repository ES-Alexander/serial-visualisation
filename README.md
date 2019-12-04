# serial-visualisation
For simple visualisation of serial input (e.g. from an Arduino or similar device).
_________________________________
 Version: 1.0.3                  
 Author: ES Alexander            
 Release Date: 05/Dec/2019       
_________________________________

## You need to know:
Allows the reading of serial input to a computer, and display of it in a grid as an image. 

Each set of serial values should be separated by a newline character ('\n'), and values within a set should be tab-separated ('\t').

### To run:
1. download and install Python 3 if not already installed (select add to PATH)
2. windows users: open command prompt (e.g. press windows key, type cmd, press enter), Mac users: open terminal
3. type `pip install serial-visualisation` (only have to do this once at the start of your session, and probably only once per computer) - this step may cause issues if python and/or pip are not in your PATH. Google 'add pip to path' for a solution. Users with multiple Python installs may need to use pip3 instead of pip.
4. make sure your Arduino software on the computer isn't using the serial port (only one program can access it at once, so program the Arduino normally, and then just don't open the serial plotter or monitor, and run this instead)
5. run using `python -m serial_grid.serial_grid` (or `python3` on a Mac)
6. answer the questions, and optionally save your settings
7. wait for it to start displaying (takes a few seconds it seems)
8. click the Data window and press 'q' or 'Q' or Escape to quit, or press 'p' (play/pause), 'c' (continue), or 's' (start/stop) to pause and/or resume the display (they're all the same, just pick your preferred key).

I hope this works well for your project! If there are any problems, or suggestions for improvement, please submit an Issue on the github page (<https://github.com/ES-Alexander/serial-visualisation/issues>).
