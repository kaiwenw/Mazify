#Weak but faster way of image segmentation than k-means
#use ONLY for monotonic images with sharp colors
def mazeFill(img,pixels,threshold=255/2):
    width,height = img.size
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

#Gets rid of impure pixels in the filtered image 
def clearImpurities(img,pixels,blobRange=1):
    width,height = img.size
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
            
#connect the islands
def connectIslands(islands,numberOfIslands,step=1):
    #should make it such that it's the number of valid moves
    numberOfIslands = len(islands)
    for i in range(numberOfIslands-1):
        makeBridge(islands,step)

def renameIslands(i1,i2,islands,listOfCoords):
    n1,n2 = i1.number,i2.number
    lo,hi = min(n1,n2),max(n1,n2)
    for coords in listOfCoords:
            if islands[coords].number==hi: 
                islands[coords].number=lo

def flipCoin():
    return random.choice([True, False])

#assume width of 200 and height of 200
def makeBridge(islands,step=1):
    global connectedMatrix, listOfCoords

    while True:
        #row,col = random.randint(0,rows-1),random.randint(0,cols-1)
        #coords flipped x,y = col,row
        #col,row = random.choice(list(islands.keys()))
        col,row = random.choice(listOfCoords)
        if (col+step==200 or connectedMatrix[row][col+step]==None) and \
            (row+step==200 or connectedMatrix[row+step][col]==None):
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



def test(img,step,fileName):
    #INITIALIZING

    #originalsize = img.size
    
    if(img.mode!="RGB"):
        img = img.convert("RGB")

    #good for downsizing
    img = img.resize((200,200), Image.ANTIALIAS)
    #print(img.size)

    width,height = img.size
    pixels = img.load()

    #ImageProcessing
    # mazeFill(img,pixels)
    # clearImpurities(img,pixels)

    dataPts = getPixMatrix(img)
    kMeans(2,dataPts,img,iterationIndex = 2)

    #img.show()

    #TODO:::: ISSUE WITH even 200x200 for circle hole
    #connectedMatrix = (callWithLargeStack(splitToSections,img,pixels))
    connectedMatrix = getPixMatrix(img)
    background = connectedMatrix[0][0]
    #print(connectedMatrix)
    #return
    #make maze!
    islands,numberOfIslands = makeBlankMaze(img,pixels,connectedMatrix,
                    background=background,step=step)

    bridges = makeBlankGrid(islands, step=step)
    #drawBridges(pixels,bridges)

    #get Start and End of Maze
    #start = getStartEnd(fileName)
    #TODO: Check if start,end are valid
    start,end = (150.0, 80.0),(108.0, 121.0)

    mazeBridges = createMazeFromGrid(islands,bridges,start,step=step)
    drawBridges(pixels,mazeBridges,(255,0,0))


    #clearer upsizing: perhaps upsize when displaying
    #img = img.resize((1024,1024),Image.ANTIALIAS)

    return img


##testing function###
def generateMaze(img,step,startPos,background):
    global islands,bridges,connectedMatrix,mazeBridges
    #img = img.resize((200,200), Image.ANTIALIAS)
    
    width,height = img.size
    pixels = img.load()

    # dataPts = getPixMatrix(img)
    # kMeans(2,dataPts,img,iterationIndex = 2)

    connectedMatrix = getPixMatrix(img)
    
    #make maze!
    islands = makeBlankMaze(img,pixels,connectedMatrix,
                    background=background,step=step)

    #make blank grid for recursive backtracking
    bridges = makeBlankGrid(pixels,islands,background,step=step)
    #drawBridges(pixels,bridges)

    #get Start and End of Maze
    #TODO: Check if start,end are valid

    #recursively create a maze
    mazeBridges = createMazeFromGrid(islands,bridges,startPos,step=step)


    drawBridges(pixels,mazeBridges,(255,0,0),background)

    #clearer upsizing: perhaps upsize when displaying
    #img = img.resize((1024,1024),Image.ANTIALIAS)

    return img


# islands = None
# bridges = None
# connectedMatrix = None
# mazeBridges = None

# fileName = "pictures/dog2.png"
# img=Image.open(fileName)
# start,end = getStartEnd(fileName)
# dataPts = getPixMatrix(img)
# kImg,miu = kMeans(2,dataPts,img,iterationIndex = 2)

# background = []

# for c in miu:
#     r,g,b=c
#     if(r<20):
#         background.append(c)


# step = 5
# mazeImg = generateMaze(kImg,step,start,background)
# #mazeImg = mazeImg.resize((400,400),Image.ANTIALIAS)
# #mazeImg.save('testMazeSolver.jpg')
# #print(mazeImg)


# #mazeImg.show()

# solvedCoords = solveMaze(start,end,islands,mazeBridges,step,background)
# mazePixels = mazeImg.load()
# startX,startY = start
# startX,startY = step*int(startX/step),step*int(startY/step)
# endX,endY = end
# endX,endY = step*int(endX/step),step*int(endY/step)

# background.append((255,0,0))
# drawBridges(mazePixels,solvedCoords,(0,255,0),background)
# mazePixels[(startX,startY)] = (0,0,255)
# mazePixels[(endX,endY)] = (0,0,255)
# mazeImg.save("mazePicture.jpg")

# mazeImg.show()
