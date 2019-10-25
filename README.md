# serial-visualisation
For simple visualisation of serial input (e.g. from an Arduino or similar device).

## You need to know:
Allows the reading of serial input to a computer, and display of it in a grid as an image. 

Each set of serial values should be separated by a newline character ('\n'), and values within a set should be tab-separated ('\t').

### To run:
1. download and install Python 3 if not already installed
0. download serial_grid.py, or clone the repository to your local machine
1. open command prompt (e.g. press windows key, type cmd, press enter)
2. type 'pip install opencv-python pyserial' (only have to do this once at the start of your session, and probably only once per computer)
3. navigate to where serial_grid.py is located (e.g. type 'cd ' and then paste in your filepath from the top of a file window, then press enter)
4. make sure your arduino software on the computer isn't using the serial port (only one program can access it at once, so program the arduino normally, and then just don't open the serial plotter or monitor, and run this instead)
5. run using 'python serial_grid.py'
6. answer the questions, and optionally save your settings
7. wait for it to start displaying (takes a few seconds it seems)
8. click the Data window and press 'q' or 'Q' or Escape to quit, or press 'p' (play/pause), 'c' (continue), or 's' (start/stop) to pause and/or resume the display (they're all the same, just pick your preferred key).

It seems like it freezes sometimes, and I'm not entirely sure why, but hopefully this'll come in handy as an alternative to viewing your data.
