from PIL import Image, ImageFilter
import random
from kMeansSeg import *


#helper function
#returns the set of coords between two bridges (including the two ends)
def getAllBridgeCoords(bridge):
    bridge = list(bridge)
    allBridgeCoords = set()
    startX,startY = bridge[0][0], bridge[0][1]
    endX,endY = bridge[1][0],bridge[1][1]
    if(endX<startX or endY<startY):
        startX,endX = endX,startX
        startY,endY = endY,startY
    difX, difY = endX-startX, endY-startY
    if(difX==0):
        for dy in range(difY+1):
            allBridgeCoords.add((startX,startY+dy))
            #pixels[startX,startY+dy] = fill
    elif(difY==0):
        for dx in range(difX+1):
            allBridgeCoords.add((startX+dx,startY))
            #pixels[startX+dx,startY] = fill
    return allBridgeCoords

#turns 2D array into a set
def setOfMatrix(matrix):
    result = set()
    for row in matrix:
        result = result.union(set(row))
    return result

def callWithLargeStack(f,*args):
    import sys
    import threading
    sys.setrecursionlimit(2**14) # max recursion depth of 16384
    isWindows = (sys.platform.lower() in ["win32", "cygwin"])
    if (not isWindows): return f(*args) # sadness...
    threading.stack_size(2**27)  # 64MB stack
    # need new thread to get the redefined stack size
    def wrappedFn(resultWrapper): resultWrapper[0] = f(*args)
    resultWrapper = [None]
    #thread = threading.Thread(target=f, args=args)
    thread = threading.Thread(target=wrappedFn, args=[resultWrapper])
    thread.start()
    thread.join()
    return resultWrapper[0]

#Creates a connectedMatrix that specifies the connectivity of colors
#TODO: DICTIONARY OF key (start position and color) corresponding to position of all pixels in the block
def splitToSections(img,pixels,background):
    width,height = img.size
    connectedMatrix = [[None]*width for row in range(height)]
    #to distinguish blocks of same color
    #blockCount = 1
    def colorFill(pixels, x, y, connectedMatrix, colorToMatch):
        #off board
        global testList
        if ((x < 0) or (x >= width) or
            (y < 0) or (y >= height)):
            return
        
        #already connected
        if (connectedMatrix[y][x]!=None):
            return

        # "fill" this cell
        color = pixels[x,y]
        if(color == colorToMatch):
            connectedMatrix[y][x] = colorToMatch
            #recursively check neighbours
            colorFill(pixels, x, y+1, connectedMatrix, colorToMatch) #down
            colorFill(pixels, x, y-1, connectedMatrix, colorToMatch) #up
            colorFill(pixels, x-1, y, connectedMatrix, colorToMatch) #left
            colorFill(pixels, x+1, y, connectedMatrix, colorToMatch) #right

    for x in range(width):
        for y in range(height):
            colorToMatch = pixels[x,y]
            #background is white
            if connectedMatrix[y][x]==None and colorToMatch in background:                

                colorFill(pixels,x,y,connectedMatrix,
                                    colorToMatch)
    return connectedMatrix

#only shows the ShowThis color
def filterColor(showThis):
    for x in range(width):
        for y in range(height):
            if(connectedMatrix[y][x]!=showThis):
                pixels[x,y] = (255,255,255)

###MAZE MAKING####
class Struct(object): pass

def makeIsland(number):
    island = Struct()
    island.east = island.south = False
    island.number = number
    return island

#make a blank maze inside the object
def makeBlankMaze(img,pixels,connectedMatrix,background = None, step=1):
    width,height = img.size
    y,x = len(connectedMatrix),len(connectedMatrix[0])
    #islands is a dictionary of values, with a coord 
    islands = dict()
    counter = 0
    for y in range(0,height,step):
        for x in range(0,width,step):
            #If it is a valid cell, make an island here
            if(connectedMatrix[y][x] in background):
                islands[(x,y)] = makeIsland(counter)
                counter+=1
    return islands

def makeBlankGrid(img,islands,background,step=1):
    pixels = img.load()
    NORTH = (0,-step)
    SOUTH = (0,+step)
    EAST = (+step,0)
    WEST = (-step,0)
    directions = [NORTH,SOUTH,WEST,EAST]
    #bridges in format [...{(starting x,y), ending(x,y)}...]
    #store in sets so order doesn't matter
    bridges = list()
    def isValidBridge(bridges,x,y,dx,dy):
        nonlocal pixels
        #not a valid destination
        if (x+dx,y+dy) not in islands: return False
        #already in bridges
        if ({(x,y),(x+dx,y+dy)} in bridges): return False
        allCoords = getAllBridgeCoords({(x,y),(x+dx,y+dy)})
        for coord in allCoords:
            if(pixels[coord] not in background):
                return False
        return True
    #finds all possible islands, and finds all possible connections between them
    for (x,y) in islands:
        for (dx,dy) in directions:
            if isValidBridge(bridges,x,y,dx,dy):
                bridges.append({(x,y),(x+dx,y+dy)})
    return bridges

def createMazeFromGrid(islands,bridges,start,step=1):
    NORTH = (0,-step)
    SOUTH = (0,+step)
    EAST = (+step,0)
    WEST = (-step,0)
    directions = [NORTH,SOUTH,WEST,EAST]
    startX,startY = start
    startX,startY = step*int(startX/step),step*int(startY/step)
    mazeBridges = list()
    #We can know if the cells are already connected if they are in the same set.
    visited = set()
    cellStack = list()
    def isValid(x,y,direction):
        dx,dy = direction
        return({(x,y),(x+dx,y+dy)} in bridges)

    def possibleDirections(x,y,visited, bridges):
        nonlocal directions
        possible = list()
        for dx,dy in directions:
            if(((x+dx,y+dy) not in visited) and ({(x,y),(x+dx,y+dy)} in bridges)):
                possible.append((dx,dy))
        return possible

    def createMaze(x,y):
        nonlocal directions, mazeBridges, bridges, visited, cellStack
        visited.add((x,y))
        cellStack.append((x,y))
        #when there are still bridges left over OR cellstack is empty, meaning returned to the beginning
        while(len(bridges)!=1 and len(cellStack)>0):
            #has neighbours that aren't visited yet
            x,y = cellStack[-1]
            if(len(possibleDirections(x,y,visited,bridges))!=0):
                dx,dy = random.choice(possibleDirections(x,y,visited,bridges))
                mazeBridges.append({(x,y),(x+dx,y+dy)})
                bridges.remove({(x,y),(x+dx,y+dy)})
                x,y = x+dx, y+dy
                cellStack.append((x,y))
                visited.add((x,y))
                continue
            #backtrack until has possible directions
            else:
                cellStack.pop()
                continue

        return mazeBridges
    return createMaze(startX,startY)

