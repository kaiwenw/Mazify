

import sys

from queue import Queue
from PIL import Image
from convertImage import *


import pylab
import matplotlib.pyplot as plt
import matplotlib.pyplot as mplt
import numpy as np

#almostEqual for pixels
def almostEqual(x,y,epsilon=3):
    return abs(x[0]-y[0])<epsilon and abs(x[1]-y[1])<epsilon

##Input Start/Out Mode
#returns (start,end)
def readStartEnd(imageName):
    x1 = mplt.imread(imageName)
    fig1 = pylab.figure(1, figsize=(11,9))
    ax1 = fig1.add_subplot(1,1,1)
    ax1.imshow(x1)
    ax1.axis('image')
    ax1.axis('off')
    print("Click start and end coords")
    x = fig1.ginput(2)
    print("click the top left and bottom right corner")
    y = fig1.ginput(2)
    XBounds = (y[0][0],y[1][0])
    YBounds = (y[0][1],y[1][1])
    mplt.close(fig1)

    return(x[0],x[1],XBounds,YBounds)


#BFS general structure is taken from 
#http://stackoverflow.com/questions/12995434/representing-and-solving-a-maze-given-an-image
#Modified from...

def BFS(start, end, pixels, XBounds, YBounds):
    lowXBound,highXBound = XBounds
    lowYBound,highYBound = YBounds

    def getAdjacent(n,step = 1):
        x,y = n
        return [(x-step,y),(x,y-step),(x+step,y),(x,y+step)] #ENWS

    def isLegal(pixels,x,y):
        nonlocal lowXBound,highXBound,lowYBound,highYBound
        R,B,G = pixels[x,y]
        t = 200
        if ((x < lowXBound) or (x > highXBound) or
        (y < lowYBound) or (y > highYBound) or
        R<t):
            return False # off-board!
        else: return True

    queue = Queue()
    queue.put([start]) # Wrapping the start tuple in a list

    while not queue.empty():

        path = queue.get() 
        pixel = path[-1]
        #print(pixel,end = '  ')

        #if pixel == end:
        if almostEqual(pixel,end):
            return path

        #loop through all directions by factor of step
        for adjacent in getAdjacent(pixel,step=2):
            x,y = adjacent
            if isLegal(pixels,x,y):
                pixels[x,y] = (127,127,127) # see note
                new_path = list(path)
                new_path.append(adjacent)
                queue.put(new_path)
    print ("Queue has been exhausted. No answer was found.")

if __name__ == '__main__':

    mazeFile = "maze4.jpg"

    start,end,XBounds,YBounds = readStartEnd(mazeFile)

    base_img = Image.open(mazeFile)
    base_pixels = base_img.load()

    convertFromRGBToBW2(base_pixels,base_img)


    path = BFS(start, end, base_pixels, XBounds, YBounds)

    path_img = Image.open(mazeFile)
    path_pixels = path_img.load()


    for position in path:
        x,y = position
        path_pixels[x,y] = (255,0,0) # red

    path_img.show()
