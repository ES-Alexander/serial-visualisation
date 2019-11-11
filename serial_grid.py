#!/usr/bin/env python3

###############################################################################
#                                                                             #
# Serial Grid: A module for displaying serial data in a grid image.           #
#                                                                             #
# Similar to Serial Monitor/Serial Plotter for arduino, but with a grid       #
#   output displayed as a greyscale image. Serial data-points should be tab-  #
#   separated, with each set of datapoints separated by a newline.            #
#                                                                             #
# Author: ES-Alexander                                                        #
# Date: 25/Oct/2019                                                           #
#                                                                             #
###############################################################################
#                                                                             #
# License: Free to use (e.g. for personal/research/commercial) under MIT      #
#   license. Usage at risk and expense of user - no liability accepted for    #
#   damages, and no guarantee provided of validity.                           #
#                                                                             #
#   If referencing, refer to as:                                              #
#   'Serial grid visualisation code provided by ES-Alexander                  #
#    (github.com/ES-Alexander)'                                               #
#                                                                             #
###############################################################################
#                                                                             #
# Modified: 11/Nov/2019 (ES-Alexander)                                        #
#   Added colour selection for min/max.                                       #
#                                                                             #
###############################################################################

import io           # input/output, allows for reading lines
import serial       # pyserial library (serial interfacing)
import numpy as np  # numerical python, fast array-based processing
import cv2          # opencv-python library
import sys          # system library, for error printing
from serial.tools.list_ports import main as list_ports

class Grid(object):
    ''' A class for displaying serial data as a gridded image.

    Close an active grid by clicking on the Data (display) window and pressing
        'q' or Escape.
    Pause an active grid by clicking on the Data (display) window and pressing
        'p' (play/pause), 'c' (continue), or 's' (start/stop).

    '''
    EXIT_KEYS = [ord('q'), ord('Q'), 27] # q or escape
    PAUSE_KEYS = [ord('c'), ord('p'), ord('s')] # c, p, or s
    # mode options
    COLOUR = 3
    GREY = 1
    DEFAULT = -1

    def __init__(self, ser, rows, cols, min_val=0, max_val=500, clarity=10,
                 min_colour=0., max_colour=1.):
        ''' Creates a serial-stream analyser which displays each line of tab-
            separated serial input as a grayscale image.

        'ser' is a pre-initialised serial.Serial instance, set up with at least
            a port, baudrate, and read timeout.
        'rows' is the number of rows being used in the grid.
        'cols' is the number of columns being used in the grid.
        'min_val' is the smallest expected value to receive from the serial
            stream, and is used to set the 'black' level of the display image.
        'max_val' is the largest expected value to receive from the serial
            stream, and is used to set the 'white' level of the display image.
        'clarity' is a resising parameter which helps avoid interpolation
            between grid positions. Value should be greater than or equal to 1.
            clarity=1 results in quite a blurred image for small grids, whereas
            clarity=10 is quite clear. Additional clarity increases computation
            time.
        'min_colour' is the colour displayed when a data-point is <= min_val.
            It should be a float in the range [0.0, 1.0] or a Blue-Green-Red
            tuple of three such floats (e.g. (0.0, 1.0, 1.0) for yellow).
        'max_colour' is the colour displayed when a data-point is >= max_val.
            It should be of the same type as min_colour.

        Constructor: Grid(serial.Serial, int, int, *int, *int, *int)

        '''
        # wrap the serial interface in an IO buffer for easier access
        self.sio = io.TextIOWrapper(io.BufferedReader(ser))
        # store the set values
        self.rows = rows
        self.cols = cols
        self.min_val = min_val
        self.max_val = max_val
        self.mode = self.GREY if isinstance(min_colour, int) else self.COLOUR
        if self.mode == self.GREY and min_colour == 0. and max_colour == 1.:
            self.mode = self.DEFAULT
        else:
            self._map_scale = np.array(max_colour) - min_colour
            self._map_offset = min_colour
            if self.mode == self.COLOUR:
                self._map = np.array([self._map_scale, self._map_offset]).T

        self.scale = (clarity * rows, clarity * cols)

        # read the first line to try to avoid meaningless reads on connection
        try:
            self.sio.readline()
        except UnicodeDecodeError:
            self.sio.readline()

        # create a resizable window for displaying the grid
        cv2.namedWindow('Data', cv2.WINDOW_NORMAL)

        # display the grid as an image
        try:
            # check validity
            if self.mode == self.COLOUR and len(min_colour) != 3:
                raise Exception('Invalid colour mode, with length {}'\
                                 .format(self.mode))
            assert min_colour != max_colour, 'min_colour and max_colour '\
                                             'cannot be the same.'
            # main loop
            while "running":
                # waits to minorly slow down displaying -> reduces freezes
                key = cv2.waitKey(30)
                if (key & 0xFF) in self.EXIT_KEYS:
                    print('User quit application')
                    break
                elif (key & 0xFF) in self.PAUSE_KEYS:
                    print('User paused -- continue with c, p, or s')
                    while (key & 0xFF) not in self.PAUSE_KEYS:
                        # check for exit attempt
                        if (key & 0xFF) in self.EXIT_KEYS:
                            print('User quit application')
                            return
                        # keep reading data so the buffer doesn't fill up
                        self.sio.readline()
                        # wait for the next key press
                        key = cv2.waitKey(10)
                    print('Display resumed')
                try:
                    self.plot_data() # attempt to read and display the data
                except (UnicodeDecodeError,ValueError) as e:
                    # read issue, occasionally occurs from unreliable serial
                    print(e, file=sys.stderr)
                    continue
        except Exception as e:
            raise e # unexpected Exception occurred
        finally:
            ser.close() # close the serial port to allow others to access
            print('Serial port closed')
            cv2.destroyAllWindows() # close the grid display

    def plot_data(self):
        ''' Reads and displays the next serial line on the grid. '''
        # remove external whitespace, split line into data readings
        line_data = self.sio.readline().strip().split('\t')
        data = []
        for data_point in line_data:
            try:
                data.append(float(data_point))
            except ValueError:
                print('{} could not be converted to a float'\
                      .format(data_point), file=sys.stderr)
        # check the data for inconsistencies
        data = np.array(data)
        min_ = data.min()
        if min_ < self.min_val:
            print('WARNING: datapoint {} is < {} (min_val)'\
                  .format(min_, self.min_val), file=sys.stderr)
        max_ = data.max()
        if max_ > self.max_val:
            print('WARNING: datapoint {} is > {} (max_val)'\
                  .format(max_, self.max_val), file=sys.stderr)
        # scale the data and shape into a grid
        data = ((data - self.min_val) / self.max_val).reshape(
            self.rows, self.cols)
        if self.mode == self.COLOUR:
            data = cv2.merge([data * scale + offset for scale, offset in \
                              self._map])
        elif self.mode == self.GREY:
            data = data * self._map_scale + self._map_offset

        # display the grid image, scaled for clarity
        cv2.imshow('Data', cv2.resize(data, self.scale,
                                      interpolation=cv2.INTER_NEAREST))


if __name__ == '__main__':
    # allow input from file or via questionaire
    sep = ';'
    filename = input('settings filename (press enter if none): ')
    if filename:
        with open(filename, 'r') as in_file:
            port, baud, timeout, rows, cols, min_val, max_val, clarity, \
                    min_colour, max_colour = in_file.readline().split(sep)
    else:
        list_ports()
        port = input('Port: ')
        baud = input('Baudrate: ')
        timeout = input('Timeout (s): ')
        rows = input('Number of rows: ')
        cols = input('Number of cols: ')
        min_val = input('Minimum expected value: ')
        max_val = input('Maximum expected value: ')
        clarity = input('Clarity (int >=1, 1->blurred, 10->quite clear): ')
        min_colour = input('Colour of min (B,G,R)/float[0-1]: ')
        max_colour = input('Colour of max (B,G,R)/float[0-1]: ')
        filename = input('Save settings to: ')
        if filename:
            try:
                with open(filename, 'w') as out_file:
                    out_file.write(sep.join([port, baud, timeout, rows, cols,
                            min_val, max_val, clarity, min_colour, max_colour]))
            except Exception as e:
                print('failed to write to file {}, due to:'.format(filename),
                      file=sys.stderr)
                print(e, file=sys.stderr)
    # attempt to process settings appropriately, or replace with defaults
    try:
        baud = int(baud)
    except Exception:
        print('invalid baudrate {}, setting to 9600'.format(baud))
        baud = 9600
    try:
        timeout = float(timeout)
    except Exception:
        print('invalid value {}, setting to 5 seconds'.format(timeout))
        timeout = 5

    rows = int(rows)
    cols = int(cols)
    min_val = float(min_val)
    max_val = float(max_val)
    try:
        min_colour = eval(min_colour)
    except Exception:
        print('invalid min_colour {}, setting to 0.0 (black)'\
              .format(min_colour))
    try:
        max_colour = eval(max_colour)
    except Exception:
        print('invalid max colour {}, setting to '.format(max_colour), end='')
        if isinstance(min_colour, float):
            max_colour = 1.0
        else:
            max_colour = (1., 1., 1.)
        print(str(max_colour) + ' (white)')

    try:
        clarity = int(clarity)
    except Exception:
        print('invalid clarity value {}, setting to 10'.format(clarity))
        clarity = 10

    # connect to the serial port specified
    ser = serial.Serial(port, baud, timeout=timeout)

    # initialise and hand over to the grid
    Grid(ser, rows, cols, min_val, max_val, clarity, min_colour, max_colour)
