#!/usr/bin/env python

import sys
import numpy as np
import os
import scipy
import scipy.misc

def main():
    os.system('convert ./challenge.gif ./challenge.png')  # get expanded gif frames
    images = get_images()
    bitstring = ''
    skip = 12  # How many images to skip
    count = 0
    while True:
        if count > len(images):
            break
        image = images[count]
        #scipy.misc.imshow(image)
        if count == 0:  # Do a special process for the first one
            gap = 12
            for number in range(0, len(image), gap):  # Grab first three boxes
                offset = 10
                x      = number + offset
                n_image = image[:, x:x + gap]
                if len(n_image[0]) > 10:
                    bit = read_bit(n_image)  # Find and add bits
                    bitstring += bit
        else:  # Some special rules for specific ranges
            if count < 360:
                box = image[:, 28:39]
            elif 360 < count < 500:
                box = image[:, 25:39]
            elif 500 < count < 650:
                box = image[:, 25:38]
            elif 650 < count < 900:
                box = image[:, 22:34]
            elif 900 < count < 920:
                box = image[:, 23:38]
            elif 920 < count < 1117:
                box = image[:, 21:32]
            else:
                box = image[:, 21:39]
            bit = read_bit(box)
            bitstring += bit
        count += skip
    bitstring += '0'
    #print bitstring, len(bitstring)
    bits = [bitstring[x:x + 8] for x in range(0, len(bitstring), 8)]
    text = ''
    for item in bits:
        final_bit = '0' + item
        value = int('0' + item, 2)
        text += (chr(value))
    print(text)
    os.system('rm ./challenge-*.png')

def read_bit(box):
    '''
    Takes image box and returns bit
    '''
    try:
        location = 25
        box[location]
    except IndexError:
        location = 9
    width    = 0
    state    = False
    previous = False
    for x in range(len(box[1])):  # Same code as in 0O code
        pixel = box[location, x]
        black = (pixel < 200)
        if state == False and black == True:
            state = True
            previous = True
        elif state == True and black == True and previous == True:
            pass
        elif state == True and black == True and previous == False:
            state = False
            break
        elif state == True and black != True:
            previous = False
            width += 1
    if state:
        return '1'
    else:
        return '0'

def get_images():
    '''
    Opens all images
    '''
    images = []
    for count in range(1150):
        try:
            n_image = scipy.misc.imread('./challenge-%i.png' % count)
            images.append(n_image)
        except IOError:
            break
    return images


if __name__ == "__main__":
    sys.exit(main())
