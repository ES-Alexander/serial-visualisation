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
                 colour_map=None):
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
        'colour_map' is a list of (intensity, colour) pairs, where intensity is
            a float in the range [0.0, 1.0], and colour is either a single
            float in the same range for greyscale, or a Blue-Green-Red tuple
            of three such floats (e.g. (0.0, 1.0, 1.0) for yellow). If a
            colour map is specified, it must include at least two colours.

        Constructor: Grid(serial.Serial, int, int, *int, *int, *int,
                          *List[float, float/tuple(float(x3))])

        '''
        # store the set values
        self.ser = ser
        self.rows = rows
        self.cols = cols
        self.min_val = min_val
        self.max_val = max_val
        if colour_map:
            self.intensities = []
            self.colours = []
            for intensity, colour in colour_map:
                self.intensities.append(intensity)

                self.colours.append(colour if hasattr(colour, '__len__') \
                                    else [colour])
            self.colours = np.array(self.colours, dtype=float)
            if len(self.colours[0]) == 1:
                self.mode = self.GREY
            else:
                self.mode = self.COLOUR
        else:
            self.mode = self.DEFAULT

        self.scale = (clarity * rows, clarity * cols)

        # create a resizable window for displaying the grid
        cv2.namedWindow('Data', cv2.WINDOW_NORMAL)

        # display the grid as an image
        try:
            # main loop
            while "running":
                # waits to minorly slow down displaying -> reduces freezes
                key = cv2.waitKey(1)
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
        # clear the serial buffer and ignore the first partial line
        self.ser.reset_input_buffer()
        self.ser.readline()
        # get the latest data
        try:
            data = self.ser.readline().strip().split(b'\t')
            data = np.array(data, dtype=float)
        except ValueError as e:
            print(e, file=sys.stderr)
            print(data)
            return

        min_ = data.min()
        if min_ < self.min_val:
            print('WARNING: datapoint {} is < {} (min_val)'\
                  .format(min_, self.min_val), file=sys.stderr)
        max_ = data.max()
        if max_ > self.max_val:
            print('WARNING: datapoint {} is > {} (max_val)'\
                  .format(max_, self.max_val), file=sys.stderr)
        # scale the data and shape into a grid
        data = ((data - self.min_val) / (self.max_val - self.min_val))
        data = self.apply_colour_map(data)#.reshape(self.rows, self.cols)

        # display the grid image, scaled for clarity
        cv2.imshow('Data', cv2.resize(data, self.scale,
                                      interpolation=cv2.INTER_NEAREST))

    def apply_colour_map(self, data):
        ''' Applies the stored colour map to the data. '''
        if self.mode == self.DEFAULT:
            return data # already in desired form
        if self.mode == self.COLOUR:
            B = data.copy()
            G = data.copy()
            R = data.copy()
            channels = [B,G,R]
        else:
            channels = np.array([data])

        last = len(self.intensities) - 1
        for c_ind, channel in enumerate(channels):
            for index, colour in enumerate(self.colours):
                # scale each region as a linear colourmap between its bounds
                new_intens = self.intensities[index] # current intensity value
                if index == 0:
                    channel[data <= new_intens] = colour[c_ind]
                else:
                    scale = colour[c_ind] - offset
                    if index < last:
                        indices = (prev_intens < data) & (data <= new_intens)
                    else:
                        indices = (prev_intens < data)
                    if not indices.any():
                        continue
                    vals = data[indices]
                    min_val = vals.min()
                    channel[indices] = scale * (channel[indices] - prev_intens)\
                            / (new_intens - prev_intens) + offset
                offset = colour[c_ind]
                prev_intens = new_intens # update old intensity value
        if len(channels) == 1:
            return channels[0].reshape(self.rows, self.cols)
        return cv2.merge(channels).reshape(self.rows, self.cols, 3)

if __name__ == '__main__':
    # allow input from file or via questionaire
    sep = ';'
    filename = input('settings filename (press enter if none): ')
    if filename:
        with open(filename, 'r') as in_file:
            port, baud, timeout, rows, cols, min_val, max_val, clarity, \
                    colour_map = in_file.readline().split(sep)
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
        colour_map = input('Colour map:\n\te.g. grey: [[0,0],[0.5,0.3],[1,1]]'\
                           '\n\t\t coloured: [[0,[0,1,1]],[1,[0,0.1,1]]]\n\t'\
                           '\t default linear greyscale intensity: <Enter>\n')
        filename = input('Save settings to: ')
        if filename:
            try:
                with open(filename, 'w') as out_file:
                    out_file.write(sep.join([port, baud, timeout, rows, cols,
                            min_val, max_val, clarity, colour_map]))
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
        clarity = int(clarity)
    except Exception:
        print('invalid clarity value {}, setting to 10'.format(clarity))
        clarity = 10

    if colour_map:
        try:
            colour_map = eval(colour_map)
        except Exception:
            print('invalid colour map \n{}\n setting to default linear'\
                  'greyscale'.format(colour_map))
            colour_map = None
    else:
        colour_map = None

    # connect to the serial port specified
    ser = serial.Serial(port, baud, timeout=timeout)
    if not ser.isOpen():
        print('Serial could not be opened, close any serial connections and '\
              'try again')
        exit()

    # initialise and hand over to the grid
    Grid(ser, rows, cols, min_val, max_val, clarity, colour_map)
