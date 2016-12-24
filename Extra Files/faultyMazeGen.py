from PIL import Image
import pylab
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import random


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


def almostEqual(d1, d2):
    epsilon = 10**-10
    return (abs(d2 - d1) < epsilon)

# def normalizeColors(img):
#     width,height = img.size
#     img.convert("RGB")
#     pixels = img.load()
#     colors = dict()
#     for x in range(width):
#         for y in range(height):
#             if(nearestColor(pixels[x,y]) in colors):
#                 colors[pixels[x,y]]
#                 pass

# #returns true if percentage error is within threshold, false otherwise
# def isSimilarColor(color1,color2,threshold):
#     percentError = 0
#     r1,g1,b1 = color1
#     r2,g2,b2 = color2
#     distance=((r2-r1)**2+(g2-g1)**2+(b2-b1)**2)**0.5
#     #percentage =distance/(((255)^2+(255)^2+(255)^2)**0.5)
#     print(round(distance))
#     return distance < threshold

# def colorFill(pixels, x, y, connectedMatrix, colorToMatch,threshold):
#     #off board
#     if ((x < 0) or (x >= width) or
#         (y < 0) or (y >= height)):
#         return 
#     #already connected
#     if (connectedMatrix[y][x]!=None):
#         return

#     # "fill" this cell
#     color = pixels[x,y]
#     if(isSimilarColor(color,colorToMatch,threshold)):
#         pixels[x,y] = colorToMatch
#         connectedMatrix[y][x] = colorToMatch
#         #recursively check neighbours
#         colorFill(pixels, x+1, y, connectedMatrix, colorToMatch,threshold)
#         colorFill(pixels, x-1, y, connectedMatrix, colorToMatch,threshold)
#         colorFill(pixels, x, y+1, connectedMatrix, colorToMatch,threshold)
#         colorFill(pixels, x, y-1, connectedMatrix, colorToMatch,threshold)




# def makeWhite(pixels,whiteThres):
#     for x in range(width):
#         for y in range(height):
#             r,g,b = pixels[x,y]
#             if(r>whiteThres and g>whiteThres and b>whiteThres):
#                 pixels[x,y] = (255,255,255)


# def mazeFill(pixels,threshold):
#     connectedMatrix = [[None]*width for row in range(height)]
#     for x in range(width):
#         for y in range(height):
#             if connectedMatrix[y][x]==None:
#                 colorToMatch = pixels[x,y]
#                 #print(colorToMatch)
#                 callWithLargeStack(colorFill,pixels,x,y,connectedMatrix,
#                                     colorToMatch,threshold)
#     return connectedMatrix

#makeWhite(pixels,150)
#img.show()
#print(setOfMatrix(callWithLargeStack(mazeFill,pixels,40)))
#img.show()

def mazeFill2(pixels,threshold=255/2):
    threshold = 255/2
    for x in range(width):
        for y in range(height):
            r,g,b = pixels[x,y]
            if(r>threshold): r = 255
            else: r = 0
            if(g>threshold): g = 255
            else: g = 0
            if(b>threshold): b = 255
            else: b = 0
            pixels[x,y] = r,g,b

def clearImpurities(pixels,blobRange=1):
    def isLegal(x,y):
        if(x<0 or x>=width or y<0 or y>=height):
            return False
        else:
            return True
    for x in range(width):
        for y in range(height):
            colorsDict = dict()
            mostFreqColor = None
            mostFreqCount = 0
            color = pixels[x,y]
            colorsDict[color] = 1
            #should be adjustible blob analysis range
            for dx in range(-blobRange,blobRange+1):
                for dy in range(-blobRange,blobRange+1):
                    if(isLegal(x+dx,y+dy)):
                        newColor = pixels[x+dx,y+dy]
                        colorsDict[newColor] = colorsDict.get(newColor,0) + 1
                        if(mostFreqCount<colorsDict[newColor]):
                            mostFreqCount = colorsDict[newColor]
                            mostFreqColor = newColor
            pixels[x,y] = mostFreqColor

def splitToSections(pixels):
    connectedMatrix = [[None]*width for row in range(height)]
    #to distinguish blocks of same color
    #blockCount = 1
    def colorFill(pixels, x, y, connectedMatrix, colorToMatch):
        # print("colorFill(pixels, %d, %d, connectedMatrix, colorToMatch)" % (x,y))
        #off board
        if ((x < 0) or (x >= width) or
            (y < 0) or (y >= height)):
            return
        #already connected
        if (connectedMatrix[y][x]!=None):
            return

        #print("colorFill(pixels, %d, %d, connectedMatrix,)" % (x,y), colorToMatch)
        # "fill" this cell
        color = pixels[x,y]
        if(color == colorToMatch):
            connectedMatrix[y][x] = colorToMatch
            #recursively check neighbours
            colorFill(pixels, x, y+1, connectedMatrix, colorToMatch) #up
            colorFill(pixels, x, y-1, connectedMatrix, colorToMatch) #down
            colorFill(pixels, x-1, y, connectedMatrix, colorToMatch) #left
            colorFill(pixels, x+1, y, connectedMatrix, colorToMatch) #right

    for x in range(width):
        for y in range(height):
            colorToMatch = pixels[x,y]
            if connectedMatrix[y][x]==None and colorToMatch!=(255,255,255):                
                #print(colorToMatch)
                colorFill(pixels,x,y,connectedMatrix,
                                    colorToMatch)
    return connectedMatrix

#only shows the ShowThis color
def filterColor(showThis):
    for x in range(width):
        for y in range(height):
            if(connectedMatrix[y][x]!=showThis):
                pixels[x,y] = (255,255,255)

# def makeBlankMaze(pixels, start, end, connectedMatrix, step=1):
#     startX,startY = start
#     endX,endY = end
#     endX,endY = int(endX),int(endY)
#     #islands is a dictionary of values, with a coord 
#     #corresponding to an island struct
#     islands = dict()
#     counter = 0
#     reachedEnd = False
#     def makeMaze(x,y):
#         nonlocal endX,endY,connectedMatrix, pixels
#         nonlocal islands, step,counter,reachedEnd
#         #cannot start/be on white space
#         #print(x,y,endX,endY)
#         if(connectedMatrix[y][x] == None or connectedMatrix[endY][endX]==None):
#             return
#         if((x,y) in islands): return
#         if((x,y) == (endX,endY)): reachedEnd = True
#         if(reachedEnd): return islands
#         islands[(x,y)] = makeIsland(counter)
#         counter += 1

#         makeMaze(x+step,y)
#         makeMaze(x-step,y)
#         makeMaze(x,y+step)
#         makeMaze(x,y-step)
#     makeMaze(int(startX),int(startY))
#     return islands, counter

def makeBlankMaze(pixels,connectedMatrix,step=1):
    rows,cols = len(connectedMatrix),len(connectedMatrix[0])
    #islands is a dictionary of values, with a coord 
    #corresponding to an island struct
    islands = dict()
    counter = 0
    for row in range(0,rows,step):
        for col in range(0,cols,step):
            #If it is a valid cell, make an island here
            if(connectedMatrix[row][col]!=None):
                islands[(col,row)] = makeIsland(counter)
                counter+=1
    return islands,counter

class Struct(object): pass

def makeIsland(number):
    island = Struct()
    island.east = island.south = False
    island.number = number
    return island

def connectIslands(islands,numberOfIslands,step=1):
    #should make it such that it's the number of valid moves
    numberOfIslands = len(islands)
    for i in range(numberOfIslands+500):
        makeBridge(islands,step)

def makeBridge(islands,step=1):
    global connectedMatrix, listOfCoords
    #print((listOfCoords))
    while True:
        #row,col = random.randint(0,rows-1),random.randint(0,cols-1)
        #coords flipped x,y = col,row
        #col,row = random.choice(list(islands.keys()))
        col,row = random.choice(listOfCoords)
        if (col+step==200 or connectedMatrix[row][col+step]==None) and (row+step==200 or connectedMatrix[row+step][col]==None):
            return
        start = islands[(col,row)]
        if flipCoin(): #try to go east
            #hit a wall: if going east isn't valid, i.e. next value is different
            if col+step==200 or connectedMatrix[row][col+step]==None: 
                print(col,row)
                print('1')
                continue
            target = islands[(col+step,row)]
            if start.number==target.number: 
                print('2')
                continue
            #the bridge is valid, so 1. connect them and 2. rename them
            start.east = True
            #renameIslands(start,target,islands)
        else: #try to go south
            if row+step == 200 or connectedMatrix[row+step][col]==None: 
                print(col,row)
                print('3')
                continue
            target = islands[(col,row+step)]
            if start.number==target.number: 
                print('4')
                continue
            #the bridge is valid, so 1. connect them and 2. rename them
            start.south = True
            #renameIslands(start,target,islands)
        #only got here if a bridge was made
        renameIslands(start,target,islands,listOfCoords)
        listOfCoords.remove((col,row))
        return

def renameIslands(i1,i2,islands,listOfCoords):
    n1,n2 = i1.number,i2.number
    lo,hi = min(n1,n2),max(n1,n2)
    for coords in listOfCoords:
            if islands[coords].number==hi: 
                islands[coords].number=lo

def flipCoin():
    return random.choice([True, False])

def getStartEnd(fileName):
    x1 = mpimg.imread(fileName)
    fig1 = pylab.figure(1, figsize=(11,9))
    ax1 = fig1.add_subplot(1,1,1)
    ax1.imshow(x1)
    ax1.axis('image')
    ax1.axis('off')
    print("Click start and end coords")
    x = fig1.ginput(2)
    return x[0],x[1]


# def solveMaze(pixels,start,end):
#     #ensures that they're part of the mod class
#     start,end = getStartEnd(fileName)
#     startX,startY = start
#     startX,startY = step*int(startX/step),step*int(startY/step)
#     endX,endY = end
#     endX,endY = step*int(endX/step),step*int(endY/step)

#     maze = data.maze
#     rows,cols = len(maze),len(maze[0])
#     visited = set()
#     targetRow,targetCol = rows-1,cols-1
#     def solve(row,col):
#         # base cases
#         if (row,col) in visited: return False
#         visited.add((row,col))
#         if (row,col)==(targetRow,targetCol): return True
#         # recursive case
#         for drow,dcol in [NORTH,SOUTH,EAST,WEST]:
#             if isValid(data, row,col,(drow,dcol)):
#                 if solve(row+drow,col+dcol): return True
#         visited.remove((row,col))
#         return False
#     return visited if solve(0,0) else None



#TODO:
fileName = "dog.jpg"
img = Image.open(fileName)
originalsize = img.size
if(img.mode!="RGB"):
    img = img.convert("RGB")
#good for downsizing
img = img.resize((200,200), Image.ANTIALIAS)
img.save(fileName)
width,height = img.size
pixels = img.load()
#img.show()


mazeFill2(pixels)
clearImpurities(pixels)
connectedMatrix = (callWithLargeStack(splitToSections,pixels))
#print(len(connectedMatrix),len(connectedMatrix[0]))
#print(connectedMatrix)

step = 5


islands,numberOfIslands = makeBlankMaze(pixels,connectedMatrix,step=step)
listOfCoords = list()
for coord in islands:
    listOfCoords.append(coord)
    #pixels[coord] = (255,0,0)
    # if(islands[coord].number==2):
    #     pixels[coord] = (255,0,0)

connectIslands(islands,numberOfIslands,step=step)


def isValid(row,col):
    return (0<=row<200 and 0<=col<200)

testCount = 0
for (col,row) in islands:
    island = islands[(col,row)]
    if(island.east or col+step==200 or connectedMatrix[row][col+step]==None):
        for i in range(1,step+1):
            if(isValid(row,col+i) and pixels[col+i,row]==(0,0,0)):
                pixels[(col+i,row)] = (255,0,0)
    if(island.south or row+step==200 or connectedMatrix[row+step][col]==None):
        for i in range(1,step+1):
            if(isValid(row+i,col) and pixels[col,row+i]==(0,0,0)):
                pixels[(col,row+i)] = (255,0,0)
    pixels[(col,row)] = (255,0,0)
    testCount += 1

# a = list()

# for i in listOfCoords:
#     a.append(islands[i].number)

# a.sort()
# print(a)

img.save("out.jpg")

# testCoord1, testCoord2 = getStartEnd("out.jpg")
# print(testCount, numberOfIslands, len(islands), len(listOfCoords))
# print(listOfCoords)
# #### If row+step or col+step == 200, then make wall south or east so blocks repeated paths
# print(testCoord1,testCoord2)
img.show()

# img.show()

#clearer upsizing: perhaps upsize when displaying
#img = img.resize(originalsize,Image.NEAREST)


