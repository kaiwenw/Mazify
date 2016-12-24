from tkinter import *
from tkinter.filedialog import *
from PIL import Image, ImageTk
from kMeansSeg import *
from mazeGenerator import *
import string



def init(data):
    data.START = 1
    data.CHOOSEMODE = 2
    data.HOW = 3
    data.DISPLAY = 5
    data.MAZE = 6
    data.OUTLINE = 7
    data.SOLUTION = 8
    data.SOLVER = 9
    data.PACMAN = 10
    data.GETBACKGROUND = 11
    data.mode = data.START
    data.file = None
    data.fill = (255,0,0) #color for maze paths
    data.food = (255,255,0) #color for foods
    ###errors
    data.imageError = False
    data.stepSizeError = False
    ###
    data.widthFactor,data.heightFactor = 2,2
    data.imgWidth = data.width//data.widthFactor
    data.imgHeight = data.height//data.heightFactor
    data.ghosts = None
    red = Image.open("source/red.jpg")
    blue = Image.open("source/blue.jpg")
    yellow = Image.open("source/yellow.jpg")
    orange = Image.open("source/orange.jpg")
    data.ghostColors = [red,orange,blue,yellow]

    initImages(data)
    initBackground(data)

def initBackground(data):
    data.backgroundFile = "source/blackBackground.jpg"
    data.bgxFactor = (data.width/200)
    data.bgyFactor = (data.height/200)
    start = 10
    data.backgroundPosition = (start,start)
    data.drawBackgroundPosition = (start*data.bgxFactor,start*data.bgyFactor)
    data.bgStep = 10
    data.backgroundImg = Image.open(data.backgroundFile)
    data.bgIslands,data.bgBridges,data.bgMazeBridges = None,None,None
    getBackground(data)
    data.bgbackground = [(255,0,0),(0,0,0),(255,255,0)]
    data.bgFoodList = set()
    data.bgFoodList = getBackgroundFoodList(data)

    data.backgroundImg = getBackgroundImg(data,data.fill,data.food)
    data.backgroundPhoto = ImageTk.PhotoImage(data.backgroundImg.resize((data.width,data.height),Image.ANTIALIAS))
    data.bgPacmanDir = (1,0)
    data.bgValidPaths = getValidPaths(data,data.backgroundImg,data.bgMazeBridges,data.bgbackground)
    data.bgPacmanPaths = list()
    data.bgPacmanScore = 0
    data.bgSolvedPath = solveBgMaze((10,10),(190,170),
                data.bgIslands,data.bgMazeBridges,data.bgStep,data.bgbackground)
    data.bgPathNum = 0
    data.bgCurrentPathPos = (0,0)
    #initial mouth angle of pacman
    data.bgMouthAngle = 90
    data.bgMouthAngleDecreasing = True

#initialize img/photos and switches
def initImages(data):
    data.background = None
    data.img,data.photo=None,None
    data.kMeansImg,data.photoOutln=None,None
    data.mazeImg,data.mazePhoto=None,None
    data.solvedImg,data.solvedPhoto = None,None
    data.solverImg,data.solverPhoto = None,None
    data.pacmanImg,data.pacmanPhoto = None,None
    data.pacmanOriginalImg = None
    data.outlineSwitch = False
    data.mazeSwitch=False
    data.displaySwitch = False
    data.imageError = False
    data.kNumberError = False
    data.stepSizeError = False
    #true so that pick step first
    data.startPickedError = True
    data.endPickedError = False
    data.kSize = ''
    data.stepSize=""
    data.startPosition = None
    data.drawStartPosition = None
    data.endPosition = None
    data.drawEndPosition = None
    data.drawPlayerPosition = None
    data.playerPosition = None
    data.pacmanPosition = None
    data.drawPacmanPosition = None
    data.pacmanTimer = 0
    data.foodDensity = 10
    data.pacmanScore = 0
    data.SOLVERWIN = 0
    data.SOLVERWON = False
    data.pacmanLives = 2
    data.gameOver = False
    data.pacmanTitleFill = '#%02x%02x%02x' % (0,0,0)
    data.pacmanR = 0
    data.pacmanB = 0
    data.pacmanG = 0
    data.pacmanWIN = False
    data.pacmanWinFill = '#%02x%02x%02x' % (255,255,255)
    data.selectedBackgroundPos = None
    data.drawSelectedBackground = None
    data.invincibleTimer = 30
    data.invincible = False
    

    ####maze vars
    data.pixels = None
    data.islands = None
    data.bridges = None
    data.connectedMatrix = None
    data.mazeBridges = None
    data.miu = None
    data.solvedBridges = None
    data.validPaths = None
    data.playerPaths = list()
    data.foodList = set()
    data.pacmanDir = None
    data.pacmanStep = 2
    data.mouthAngle = 90
    data.mouthAngleDecreasing = True
    ###
    data.xFactor = None
    data.yFactor = None
    data.xShift = None
    data.yShift = None



###HELPER FUNCTIONS#############################################################

def getFileName(data):
    return askopenfilename()

#resizes img and converts it to a photo
def convertImageAndResize(data):
    data.img = data.img.convert("RGB")
    data.img = data.img.resize((data.width//data.widthFactor,
                    data.height//data.heightFactor), Image.ANTIALIAS)
    return ImageTk.PhotoImage(data.img)

#pops up window when processing
def processingPleaseWait(text, function, *args):
    import time, threading
    window = Toplevel() 
    label = Label(window, text = text)
    label.pack()
    done = []
    def call():
        result = function(*args)
        done.append(result)

    thread = threading.Thread(target = call)
    thread.start() # start parallel computation
    while thread.is_alive():
        # code while computing
        window.update()
        time.sleep(0.001)
    # code when computation is done
    label['text'] = str(done)

#draws bridges with fill color
#nondestructively does this
def drawBridges(img,bridges,fill,background):
    temp = img.copy()
    pixels = temp.load()
    def isValid(x,y):
        return pixels[x,y] in background

    def drawBridge(pixels,bridge,fill):
        allCoords = getAllBridgeCoords(bridge)
        for x,y in allCoords:
            if(isValid(x,y)):
                pixels[x,y]=fill
    for bridge in bridges:
        drawBridge(pixels,bridge,fill)
    return temp




#same template as bridges, but now inserts points into a set instead
def getValidPaths(data,img,bridges,background):
    pixels = img.load()
    validPaths = set()
    def isValid(x,y):
        return pixels[x,y] in background
    def getPath(pixels,bridge):
        allCoords = getAllBridgeCoords(bridge)
        for x,y in allCoords:
            if(isValid(x,y)):
                validPaths.add((x,y))
    for bridge in bridges:
        getPath(pixels,bridge)
    return validPaths

#Doesn't return anything, because destructive
def getImageOutline(data,iterationIndex=7):
    #this is pivotal to ensure the processing time of the program
    #img is the 200,200 image for the whole program, whereas kMeansImg and 
    #mazeImg are 400,400 respective versions
    data.img = data.img.resize((200,200),Image.ANTIALIAS)
    dataPts = getPixMatrix(data.img)
    data.kMeansImg,data.miu = kMeans(int(data.kSize),dataPts,data.img,
                            iterationIndex=iterationIndex)
    pix = data.kMeansImg.load()
    data.background = list()
    if(data.background==[]):
        data.background.append(pix[data.selectedBackgroundPos])
    else:
        data.background[0] = pix[data.selectedBackgroundPos]
    data.kMeansImg = data.kMeansImg.resize((data.width//data.widthFactor,
                                data.height//data.heightFactor),Image.ANTIALIAS)
    data.photoOutln = ImageTk.PhotoImage(data.kMeansImg)

#Islands-Bridges Model adopted from 15-112 website. However, modified greatly.
#Recursive backtracking algorithm 
#followed high-level pseudocode from Wikipedia on maze generation, 
#but I implemented all of it and modified it greatly.
def getMaze(data):
    data.connectedMatrix = getPixMatrix(data.img)
    while(data.mazeBridges==[] or data.mazeBridges == None):
        data.islands = makeBlankMaze(data.img,data.pixels,data.connectedMatrix,
                        background=data.background,step=int(data.stepSize))
        data.bridges = makeBlankGrid(data.img,data.islands,data.background,
                            step=int(data.stepSize))
        data.mazeBridges = createMazeFromGrid(data.islands,data.bridges,
                    data.startPosition,step=int(data.stepSize))
    #draw them such that they equal to the exact opposite color than the current cell color.
    data.mazeImg = drawBridges(img=data.img,bridges=data.mazeBridges,
                                    fill=(255,0,0),background=data.background)
    data.validPaths = getValidPaths(data,data.img,data.mazeBridges,data.background)
    data.mazePhoto = ImageTk.PhotoImage(data.mazeImg.resize((data.width//data.widthFactor,
                                data.height//data.heightFactor),Image.ANTIALIAS))

#Inspired by 15112 version of solveMaze
def solveMaze(data,start,end,islands,bridges,step,background):
    #maze = data.maze
    startX,startY = start
    endX,endY = end
    startX,startY = step*int(startX/step),step*int(startY/step)
    endX,endY = step*int(endX/step),step*int(endY/step)
    if(startX,startY) not in islands or (endX,endY) not in islands:
        return None

    NORTH = (0,-step)
    SOUTH = (0,+step)
    EAST = (+step,0)
    WEST = (-step,0)

    def isValid(x,y,direction):
        dx,dy = direction
        return {(x,y),(x+dx,y+dy)} in bridges

    solveVisited = list()
    def solve(x,y,dx,dy):
        # base cases
        if {(x,y),(x+dx,y+dy)} in solveVisited: return False
        solveVisited.append({(x,y),(x+dx,y+dy)})
        if (x+dx,y+dy)==(endX,endY): return True
        # recursive case
        for dirX,dirY in [NORTH,SOUTH,WEST,EAST]:
            if isValid(x+dx,y+dy,(dirX,dirY)):
                if solve(x+dx,y+dy,dirX,dirY): return True
        solveVisited.remove({(x,y),(x+dx,y+dy)})
        return False

    for dirX,dirY in [NORTH,SOUTH,WEST,EAST]:
        if({(startX,startY),(startX+dirX,startY+dirY)} in data.mazeBridges):
            if(solve(startX,startY,dirX,dirY)):
                return solveVisited

def drawSolutions(data):
    data.solvedBridges = solveMaze(data,data.startPosition,data.endPosition,
            data.islands,data.mazeBridges,int(data.stepSize),data.background)
    data.solvedImg = drawBridges(img=data.mazeImg,bridges=data.solvedBridges,
                        fill=(0,255,0),background=data.background)
    data.solvedImg = data.solvedImg.resize((data.width//data.widthFactor,
                                data.height//data.heightFactor),Image.ANTIALIAS)
    data.solvedPhoto = ImageTk.PhotoImage(data.solvedImg)
    return data.solvedPhoto

def getPacmanFoodList(data):
    temp = data.img.copy()
    pixels = temp.load()
    bridges = data.mazeBridges
    def isValid(x,y):
        return pixels[x,y] in data.background
    def getFoodInBridge(pixels,bridge):
        allCoords = getAllBridgeCoords(bridge)
        for x,y in allCoords:
            if(isValid(x,y)):
                if(not (x+y) % data.foodDensity):
                    data.foodList.add((x,y))
    for bridge in bridges:
        getFoodInBridge(pixels,bridge)
    return data.foodList

def getPacmanImg(data,fill,food=(255,255,0)):
    temp = data.img.copy()
    pixels = temp.load()
    bridges = data.mazeBridges
    def isValid(x,y):
        return pixels[x,y] in data.background or pixels[x,y]==food
    def drawBridge(pixels,bridge,fill):
        allCoords = getAllBridgeCoords(bridge)
        for x,y in allCoords:
            if(isValid(x,y)):
                if((x,y) in data.foodList):
                    pixels[x,y] = food
                else:
                    pixels[x,y] = fill
    for bridge in bridges:
        drawBridge(pixels,bridge,fill)
    if(data.pacmanOriginalImg==None):
        data.pacmanOriginalImg = temp.copy()
    temp = temp.resize((data.width//data.widthFactor,
                               data.height//data.heightFactor),Image.ANTIALIAS)
    return temp

def movePacman(data):
    if(data.pacmanPosition==data.endPosition):
        data.pacmanWIN = True
    if(data.pacmanLives == 0):
        data.gameOver = True
    if(data.gameOver):
        return
    def intersect(p1,p2,r):
        def d(x,y):
            return (x**2+y**2)**0.5
        x1,y1 = p1
        x2,y2 = p2
        return d((x2-x1),(y2-y1))<r
    for ghost in list(data.ghosts.values()):
        #only works if pacman isnt in invincible mode
        if(intersect(ghost.position,data.pacmanPosition,r=5) and data.invincible==False):
            data.pacmanLives -= 1
            data.pacmanScore = 0
            data.invincible = True
    px,py = data.pacmanPosition
    px,py = int(px),int(py)
    drawPx,drawPy = data.drawPacmanPosition
    dx,dy = data.pacmanDir
    if(abs(dx)>0 and dy==0):
        if(data.pacmanStep>abs(int(data.stepSize)-(px+dx)%int(data.stepSize))):
            if(dx>0):
                dx = int(data.stepSize)-px%int(data.stepSize)
            elif(dx<0):
                dx = -1*(px%int(data.stepSize))

    elif(dx==0 and abs(dy)>0):
        if(data.pacmanStep>abs(int(data.stepSize)-(py+dy)%int(data.stepSize))):
            if(dy>0):
                dy = int(data.stepSize)-py%int(data.stepSize)
            elif(dy<0):
                dy = -1*(py%int(data.stepSize))

    allSteps = getAllBridgeCoords({(px,py),(px+dx,py+dy)})

    def isValidStep(data,px,py,dx,dy):
        nonlocal allSteps
        for step in allSteps:
            if step not in data.validPaths: return False
        return True

    if(isValidStep(data,px,py,dx,dy)):
        data.pacmanPosition = (px+dx,py+dy)
        data.drawPacmanPosition = (drawPx+dx*data.xFactor,drawPy+dy*data.yFactor)
        data.intersection = set(allSteps).intersection(data.foodList)
        if(len(data.intersection)!=0):
            for eatenFood in list(data.intersection):
                data.foodList.remove(eatenFood)
                data.pacmanScore += 1
        data.pacmanImg = getPacmanImg(data,(255,0,0),food=(255,255,0))
        bigImage = data.pacmanImg.resize((data.width,data.height),Image.ANTIALIAS)
        data.pacmanPhoto = ImageTk.PhotoImage(bigImage)

#ghost class
class Ghost(object):
    def __init__(self,data,position,ghostImg,direction):
        self.position = position
        ghostImg = ghostImg.resize((20,20),Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(ghostImg)
        x,y = position
        #self.drawPosition = (x*data.xFactor+data.xShift,y*data.yFactor+data.yShift)
        self.dir = direction
        self.lastPosition = None
    def isValidStep(data,x,y,dx,dy,allSteps):
        for step in allSteps:
            if step not in data.validPaths: return False
        return True

def moveGhost(data,ghost):
    getGhostDir(data,ghost)
    px,py = ghost.position
    px,py = int(px),int(py)
    dx,dy = ghost.dir
    allSteps = getAllBridgeCoords({(px,py),(px+dx,py+dy)})
    ghost.position = (px+dx,py+dy)

#gets direction for each ghost
def getGhostDir(data,ghost):
    #check if ghost is at an intersection
    if(ghost.position not in data.islands):
        return False
    
    #at an intersection, so get list of possible bridges
    step = int(data.stepSize)
    #allbridges is a list of all possible places the ghost can go
    allBridges = list()
    x,y = ghost.position

    def isValidStep(data,allSteps):
        for step in allSteps:
            if step not in data.validPaths: return False
        return True

    for (dx,dy) in [(step,0),(0,step),(-step,0),(0,-step)]:
        allSteps = getAllBridgeCoords({(x,y),(x+dx,y+dy)})
        if isValidStep(data,allSteps):
            allBridges.append((x+dx,y+dy))
    randomVar = random.random()
    #small markov chains here
    if (ghost.lastPosition in allBridges) and len(allBridges)>1:
        if(randomVar>0.05):
            allBridges.remove(ghost.lastPosition)
    nx,ny = random.choice(allBridges)
    if(nx<x and ny==y):
        ghost.dir = (-1,0)
    elif(nx>x and ny==y):
        ghost.dir = (1,0)
    elif(nx==x and ny>y):
        ghost.dir = (0,1)
    elif(nx==x and ny<y):
        ghost.dir = (0,-1)
    ghost.lastPosition = ghost.position


def drawGhost(canvas,data,ghost):
    x,y = ghost.position
    x,y = x*4,y*4
    canvas.create_image(x,y,image=ghost.photo)


################################################################################

####DRAW MODES######
def drawSplashScreen(canvas,data):
    Title = "Kevin's Mazify!"
    canvas.create_text(data.width//2,data.height//4,text=Title,
                    font="Arial 40 bold",fill="#%02x%02x%02x" % (255,255,255))
    canvas.create_rectangle(data.width//2-150,data.height//2-50,
                            data.width//2+150,data.height//2+50,fill='black')
    canvas.create_text(data.width//2,data.height//2,text = "Press P to Play",font="Arial 30 italic",fill="grey")
    canvas.create_rectangle(data.width//2-150,data.height*2//3-50,
                        data.width//2+150,data.height*2//3+50,fill='black')
    canvas.create_text(data.width//2,data.height*2//3,text = "Press H for Help",
                                font="Arial 30 italic",fill="grey")

def drawChooseMode(canvas,data):
    Title = "Play Mode"
    canvas.create_text(20,20,text="Press b to go back",font="Arial 20",
                                        anchor="w",fill="white")
    canvas.create_text(data.width//2,data.height//6,text=Title,
                                font="Arial 40 bold",fill="white")
    canvas.create_rectangle(data.width//2-300,data.height//2-100,
                data.width//2+300,data.height//2+200,fill='black',outline='black')
    canvas.create_text(data.width//2,data.height//2-40, 
                    text="Mazify your photos!",font="Arial 35 bold",fill="grey")
    canvas.create_text(data.width//2,data.height//2+40,
            text="Press c to choose image",font="Arial 30 bold",fill="grey")
    if(data.imageError):
        canvas.create_text(data.width//2,data.height*2//3,
            text="Please use an image (.gif,.png,.jpg) file",
            font="Arial 20 bold", fill="red")
    else:
        canvas.create_text(data.width//2,data.height*2//3,
            text="(choose any icon with two colors)",
            font = "Arial 20",fill='grey')

def drawDisplay(canvas,data):
    Title = "Display Mode"
    canvas.create_text(20,20,text="Press b to go back",font="Arial 20",anchor="w",fill="white")
    canvas.create_text(data.width//2,data.height//6,text=Title,font="Arial 40 bold",fill="white")
    canvas.create_rectangle(data.width//5,data.height*7//9,
                            data.width*4//5,data.height*8//9+20,fill="black")
    #simulate loading screen
    canvas.create_text(data.width//2,data.height*5//6+5,
                                        text="Num. of Colors: %s" % data.kSize,
                font="Arial 20",fill="grey")
    if(data.kNumberError):
        canvas.create_text(data.width//2,data.height*5//6,
            text="Please input a valid stepsize before continuing",
                    font="Arial 20 bold",fill="grey")

    canvas.create_text(data.width//2,data.height*4//5,
        text="Select Number of Colors (2-9), Press d to delete",
                                            font="Arial 20 bold",fill="grey")
    canvas.create_image(data.width//2,data.height//5,image=data.photo,anchor="n")
    canvas.create_text(data.width//2,data.height*6//7+20,
        text="Is this right image? (Y/N)",font="Arial 20 bold",fill="grey")

def drawGetBackground(canvas,data):
    Title = "Get Background Color"
    canvas.create_text(20,20,text="Press b to go back",
                                font="Arial 20",anchor="w",fill="white")
    canvas.create_text(data.width//2,data.height//6,text=Title,
                                            font="Arial 40 bold",fill="white")
    canvas.create_rectangle(data.width*2//10,data.height*6.5//9,
                                data.width*8//10,data.height*8//9,fill="black")

    canvas.create_text(data.width//2,data.height*3//4,
        text="Select the Color to Draw Maze On",font="Arial 20 bold",fill="grey")
    canvas.create_image(data.width//2,data.height//5,image=data.photo,anchor="n")
    canvas.create_text(data.width//2,data.height*5//6,
                    text="Press Y to continue.",
                    font="Arial 20 bold",fill="grey")
    if(data.drawSelectedBackground!=None):
        x,y = data.drawSelectedBackground
        canvas.create_oval(x-3,y-3,x+3,y+3,fill="green")


def drawRightOutline(canvas,data):
    Title = "Outline Mode"
    canvas.create_text(20,20,text="Press b to go back",
                            font="Arial 20",anchor="w",fill="white")
    canvas.create_text(data.width//2,data.height//6,text=Title,
                                    font="Arial 40 bold",fill="white")
    
    #loading
    if(data.outlineSwitch==False):
        canvas.create_text(data.width//2,data.height//2,
                            text="loading...",font="Arial 15 bold",fill="white")
    else:
        canvas.create_rectangle(data.width*2//10-30,data.height*6//9,
                        data.width*8//10+30,data.height*10//11,fill='black')
        canvas.create_text(data.width//2,data.height*7//9+10,
                        text="(Longer Branch = Easier Maze)",font="Arial 20",fill='grey')
        canvas.create_text(data.width//2,data.height*7//9+35,text="Branch Length: %s" % data.stepSize,
                font="Arial 20",fill="grey")
        canvas.create_text(data.width//2,data.height*3//4,
            text="1. Select Length of Maze Branches, Press d to delete",
                                font="Arial 20 bold",fill="grey")
        canvas.create_image(data.width//2,data.height//5,image=data.photoOutln,anchor="n")
        canvas.create_text(data.width//2,data.height*8//9,
            text="Is this right color scheme? Yes!/No,try again... (Y/N)",
                                font="Arial 20",fill="grey")
        if(data.startPickedError==False and data.startPosition!=None):
            x,y = data.drawStartPosition
            canvas.create_oval(x-3,y-3,x+3,y+3,fill="light blue")
        if(data.stepSizeError):
            canvas.create_text(data.width//2,data.height*5//6+20,
                text="Please input a valid stepsize before continuing",
                        font="Arial 20 bold",fill="white")
        else:
            canvas.create_text(data.width//2,data.height*5//6+20,
                text="2. Pick a VALID Start Position on the Image.",
                        font="Arial 20 bold",fill="grey")


def drawMazeMode(canvas,data):
    Title = "Maze Mode! :-)"
    canvas.create_text(20,20,text="Press b to go back",font="Arial 20",anchor="w",fill="white")
    canvas.create_text(data.width//2,data.height//6,text=Title,font="Arial 40 bold",fill="white")

###DISPLAYING MAZE
    if(data.mazeSwitch==False):
        canvas.create_text(data.width//2,data.height//2,text="loading...",
                            font="Arial 20 bold",fill="white")
    else:
        canvas.create_image(data.width//2,data.height//5,
                            image=data.mazePhoto,anchor = "n")
        x,y = data.drawStartPosition
        canvas.create_rectangle(data.width//2-250,data.height*4//5-20,
                            data.width//2+250,data.height*8//9,fill="black")
        canvas.create_oval(x-3,y-3,x+3,y+3,fill="light blue")
        if(data.endPosition==None and data.drawEndPosition==None):
            canvas.create_text(data.width//2,data.height*4//5,
                text="Please Pick an End Position for the Maze.",
                        font="Arial 20 bold",fill="grey")
        else:
            ex,ey = data.drawEndPosition
            canvas.create_oval(ex-3,ey-3,ex+3,ey+3,fill="blue") 
            canvas.create_text(data.width//2,data.height*4//5,
                text="Press G for Solver Mode :-D", font="Arial 20 bold",fill="grey")
            canvas.create_text(data.width//2,data.height*6//7,
                text="Press P for Pacman!!! :-)",font="Arial 20 bold",fill="grey")

def drawSolverMode(canvas,data):
    Title = "Solver Mode! :-D"
    canvas.create_text(20,20,text="Press b to go back",
                font="Arial 20",anchor="w",fill='white')
    canvas.create_text(data.width//2,data.height//6,text=Title,
                        font="Arial 40 bold",fill='white')
    if(data.solverPhoto==None):
        canvas.create_image(data.width//2,data.height//5,
                image=data.mazePhoto,anchor = "n")
    else:
        canvas.create_image(data.width//2,data.height//5,
                            image=data.solverPhoto,anchor = "n")
    canvas.create_rectangle(data.width//2-200,data.width*4//5-30,
                    data.width//2+200,data.width*4//5+30,fill='black')
    canvas.create_text(data.width//2,data.width*4//5,
                text="Press s to see a solution",font="Arial 30 bold",fill='grey')
    sx,sy = data.drawStartPosition
    canvas.create_oval(sx-8,sy-8,sx+8,sy+8,fill="light blue")
    canvas.create_text(sx,sy,text="S",font="Arial 10 bold")
    ex,ey = data.drawEndPosition
    canvas.create_oval(ex-8,ey-8,ex+8,ey+8,fill="blue")
    canvas.create_text(ex,ey,text="E",font="Arial 10 bold")
    px,py = data.drawPlayerPosition
    canvas.create_oval(px-5,py-5,px+5,py+5,fill="yellow")
    if(data.SOLVERWON):
        canvas.create_rectangle(data.width//2-350,data.height//2-100,
                    data.width//2+350,data.height//2+100,fill="dark red")
        canvas.create_text(data.width//2,data.height//2,
                text="CONGRATULATIONS, YOU WON!",font="Arial 40 bold",fill="white")
        canvas.create_text(data.width//2,data.height//2+40,
                    text="Press r to reset",font="Arial 40 bold",fill="white")

def drawSolution(canvas,data):
    Title = "Solution"
    canvas.create_text(20,20,text="Press b to go back",font="Arial 20",anchor="w",fill='white')
    canvas.create_text(data.width//2,data.height//6,text=Title,font="Arial 40 bold",fill='white')
    canvas.create_image(data.width//2,data.height//5,image=data.solvedPhoto,anchor = "n")
    sx,sy = data.drawStartPosition
    canvas.create_oval(sx-8,sy-8,sx+8,sy+8,fill="light blue")
    canvas.create_text(sx,sy,text="S",font="Arial 10 bold")
    ex,ey = data.drawEndPosition
    canvas.create_oval(ex-5,ey-5,ex+5,ey+5,fill="blue")
    canvas.create_text(ex,ey,text="E",font="Arial 10 bold")

def drawPacman(canvas,data,topleft,bottomright,fill):
    x1,y1 = topleft
    x2,y2 = bottomright
    radius = (y2-y1)//2
    dx,dy = data.pacmanDir
    orientation = 0
    angle = data.mouthAngle
    if(dx>0 and dy==0):
        orientation = 0
    elif(dx<0 and dy==0):
        orientation = 180
    elif(dx==0 and dy<0):
        orientation = 90
    elif(dx==0 and dy>0):
        orientation = 270
    startAngle = orientation + angle/2
    endAngle = orientation - angle/2
    extent = 360-(startAngle-endAngle)
    canvas.create_arc(x1,y1,x2,y2,start=startAngle,extent=extent,
                        style="pieslice",fill=fill)



def drawPacmanMode(canvas,data):
    Title = "PACMAN MODE"
    canvas.create_image(0,0,image=data.pacmanPhoto,anchor = "nw")
    liveFill = "black"
    if(data.pacmanLives<2):
        liveFill = "red"
    canvas.create_text(300,20,text="Pacman Lives: %d" % (data.pacmanLives),
                        font="Arial 30 bold",anchor="w",fill=liveFill)
    canvas.create_text(20,20,text="Press b to go back",font="Arial 20",
                        anchor="w",fill="black")
    canvas.create_text(data.width//2,data.height//6,text=Title,
                        font="Arial 40 bold",fill=data.pacmanTitleFill)
    canvas.create_text(data.width-20,20,text="Score: %d" % data.pacmanScore,
                    font="Arial 20",anchor="e",fill="black")
    sx,sy = data.drawStartPosition
    sx,sy = (sx-data.xShift)*data.xFactor,(sy-data.yShift)*data.yFactor
    canvas.create_oval(sx-10,sy-10,sx+10,sy+10,fill="light blue")
    canvas.create_text(sx,sy,text="S",fill="black",font="Arial 10 bold")
    ex,ey = data.drawEndPosition
    ex,ey = (ex-data.xShift)*data.xFactor,(ey-data.yShift)*data.yFactor
    canvas.create_oval(ex-10,ey-10,ex+10,ey+10,fill="blue")
    canvas.create_text(ex,ey,text="E",fill="black",font="Arial 10 bold")
    px,py = data.drawPacmanPosition
    px,py = (px-data.xShift)*data.xFactor,(py-data.yShift)*data.yFactor
    
    fill="yellow"
    if(data.invincible):
        if(data.invincibleTimer%2==0):
            if(data.invincibleTimer>=15):
                if(fill=="yellow"):
                    fill="blue"
                else:
                    fill="yellow"
            else:
                if(fill=="yellow" or fill=="blue"):
                    fill="red"
                else:
                    fill="yellow"

    drawPacman(canvas,data,(px-10,py-10),(px+10,py+10),fill=fill)
    for i in range(len(data.ghosts)):
        drawGhost(canvas,data,data.ghosts[i])
    if(data.gameOver):
        canvas.create_rectangle(100,300,700,500,fill="red")
        canvas.create_text(400,400,text="Game Over! Press b to go back",
                            fill="black",font="Arial 30 bold")
    if(data.pacmanWIN):
        canvas.create_rectangle(100,300,700,500,fill=data.pacmanTitleFill)
        canvas.create_text(400,400,text="Great! You Won! Score: %d." % data.pacmanScore,
                            fill=data.pacmanWinFill,font="Arial 30 bold")
    

def drawHelpMode(canvas,data):
    Title = "How to Play"
    canvas.create_text(20,20,text="Press b to go back",font="Arial 20",
                        anchor="w",fill="white")
    canvas.create_text(data.width//2,data.height//6,text=Title,
                        font="Arial 40 bold",fill="white")
    canvas.create_rectangle(data.width//9,data.height//5,
                    data.width*8//9,data.height*7//8,fill="black")
    canvas.create_text(data.width//5,data.height//4+20,
        text="Game Description: Mazify! randomly creates a valid \nmaze from a two-colored icon",
        font="Arial 20",fill="grey",anchor="w")
    canvas.create_text(data.width//5,data.height//4+70,text="Instructions",
                font="Arial 20 underline",fill="grey",anchor="w")
    #each line is approx. 35 pix
    canvas.create_text(data.width//5,data.height//4+105,
        text="1. Choose a two-colored icon to Mazify!",font="Arial 20",
        fill="grey",anchor="w")
    canvas.create_text(data.width//5,data.height//4+140,
        text="2. Follow instructions to process image and generate maze",
                    font="Arial 20",
        fill="grey",anchor="w")
    canvas.create_text(data.width//5,data.height//4+175,
        text="3. Pick an interactively fun mode: ",font="Arial 20",
        fill="grey",anchor="w")
    canvas.create_text(data.width//4,data.height//4+210,
        text="Solver Mode: An orthodox game of maze-solving in an\n \
        \t      unorthodox maze of your choice. \n\
        \t      Generated uniquely every time for \n\
        \t      maximal enjoyment!",font="Arial 20",
        fill="grey",anchor="nw")
    canvas.create_text(data.width//4,data.height//4+210+3*35,
        text="Pacman Mode: You must help hungry Pacman get to \n \
        \t      the end destination while avoiding \n \
        \t      dangerous enemies. On the way, \n \
        \t      eat as many cookie crumbs and \n \
        \t      grab up as many points as possible \n \
        \t      before Cookie Monster eats you!",
        font="Arial 20",
        fill="grey",anchor="nw")
    canvas.create_text(data.width//5,data.height//4+210+8*35-20,
        text="4. Have Fun! :-)",font="Arial 20",fill="grey",anchor="w")

###BACKGROUND
def drawBackground(canvas,data):
    #draw maze, so use data.timer for backtracking to make move
    canvas.create_rectangle(0,0,data.width,data.height,fill="black")
    canvas.create_image(10,10,image=data.backgroundPhoto,anchor='nw')
    canvas.create_text(data.width-20,20,text="Score: %d" % data.bgPacmanScore,
                    font="Arial 20",anchor="e",fill='white')
    bgx,bgy = data.drawBackgroundPosition
    bgx += 10
    bgy += 10
    drawBgPacman(canvas,data,(bgx-10,bgy-10),(bgx+10,bgy+10),fill="yellow")

def drawBgPacman(canvas,data,topleft,bottomright,fill):
    x1,y1 = topleft
    x2,y2 = bottomright
    radius = (y2-y1)//2
    dx,dy = data.bgPacmanDir
    orientation = 0
    angle = data.bgMouthAngle
    if(dx>0 and dy==0):
        orientation = 0
    elif(dx<0 and dy==0):
        orientation = 180
    elif(dx==0 and dy<0):
        orientation = 90
    elif(dx==0 and dy>0):
        orientation = 270
    startAngle = orientation + data.bgMouthAngle/2
    endAngle = orientation - data.bgMouthAngle/2
    extent = 360-(startAngle-endAngle)
    canvas.create_arc(x1,y1,x2,y2,start=startAngle,extent=extent,
                            style="pieslice",fill=fill)

def getBackground(data):
    img = Image.open(data.backgroundFile)
    connectedMatrix = getPixMatrix(img)
    background=[(0,0,0)]
    pixels = img.load()
    step = data.bgStep
    data.bgIslands = makeBlankMaze(img,pixels,connectedMatrix,
                        background=background,step=step)
    data.bgBridges = makeBlankGrid(img,data.bgIslands,background,step=step)
    data.bgMazeBridges = createMazeFromGrid(data.bgIslands,data.bgBridges,
                                    (10,10),step=step)
    data.backgroundImg = drawBridges(img=img,bridges=data.bgMazeBridges,
                                    fill=(255,0,0),background=background)
    data.backgroundPhoto = ImageTk.PhotoImage(data.backgroundImg.resize((data.width,data.height),Image.ANTIALIAS))
    return data.backgroundPhoto

#insert mazeBridges
#make it so that solveVisited is a list, that records every move of the pacman
def solveBgMaze(start,end,islands,bridges,step,background):
    #maze = data.maze

    startX,startY = start
    endX,endY = end
    startX,startY = step*int(startX/step),step*int(startY/step)
    endX,endY = step*int(endX/step),step*int(endY/step)
    if(startX,startY) not in islands or (endX,endY) not in islands:
        return None

    NORTH = (0,-step)
    SOUTH = (0,+step)
    EAST = (+step,0)
    WEST = (-step,0)

    def isValid(x,y,direction):
        dx,dy = direction
        return {(x,y),(x+dx,y+dy)} in bridges

    solveVisited = list()
    def solve(x,y):
        # base cases
        if (x,y) in solveVisited: return False
        solveVisited.append((x,y))
        if (x,y)==(endX,endY): return True
        # recursive case
        for dirX,dirY in [NORTH,SOUTH,WEST,EAST]:
            #print((x,y),(x+dx,y+dy),isValid(x,y,(dx,dy)))
            if isValid(x,y,(dirX,dirY)):
                if solve(x+dirX,y+dirY): return True
        solveVisited.remove((x,y))
        return False
    solve(startX,startY)
    return solveVisited


def getBackgroundImg(data,fill,food):
    temp = data.backgroundImg.copy()
    pixels = temp.load()
    bridges = data.bgMazeBridges
    def drawBridge(pixels,bridge,fill):
        allCoords = getAllBridgeCoords(bridge)
        for x,y in allCoords:
            if((x,y) in data.bgFoodList):
                pixels[x,y] = food
            else:
                pixels[x,y]=fill
    for bridge in bridges:
        drawBridge(pixels,bridge,fill)
    return temp

def getBackgroundFoodList(data):
    bgFoodDensity = 12
    temp = data.backgroundImg.copy()
    pixels = temp.load()
    bridges = data.bgMazeBridges
    def getFoodInBridge(pixels,bridge):
        allCoords = getAllBridgeCoords(bridge)
        for x,y in allCoords:
            if(not (x+y) % bgFoodDensity):
                data.bgFoodList.add((x,y))
    for bridge in bridges:
        getFoodInBridge(pixels,bridge)
    return data.bgFoodList

def getBgPacmanDir(data):
    if(len(data.bgSolvedPath)==1):
        initBackground(data)
    if(data.backgroundPosition==data.bgSolvedPath[0]):
        data.bgSolvedPath.pop(0)
    nx,ny = data.bgSolvedPath[0]
    cx,cy = data.backgroundPosition
    if(nx<cx and ny==cy):
        data.bgPacmanDir = (-1,0)
    elif(nx>cx and ny==cy):
        data.bgPacmanDir = (1,0)
    elif(nx==cx and ny>cy):
        data.bgPacmanDir = (0,1)
    elif(nx==cx and ny<cy):
        data.bgPacmanDir = (0,-1)

def moveBgPacman(data):
    px,py = data.backgroundPosition
    px,py = int(px),int(py)
    drawPx,drawPy = data.drawBackgroundPosition
    dx,dy = data.bgPacmanDir
    allSteps = getAllBridgeCoords({(px,py),(px+dx,py+dy)})

    def isValidStep(data,px,py,dx,dy):
        nonlocal allSteps
        for step in allSteps:
            if step not in data.bgValidPaths: return False
        return True
    if(isValidStep(data,px,py,dx,dy)):
        data.backgroundPosition = (px+dx,py+dy)
        data.drawBackgroundPosition = (drawPx+dx*data.bgxFactor,drawPy+dy*data.bgyFactor)
        intersection = set(allSteps).intersection(data.bgFoodList)
        if(len(intersection)!=0):
            for eatenFood in list(intersection):
                data.bgFoodList.remove(eatenFood)
                data.bgPacmanScore += 1
        if({(px,py),(px+dx,py+dy)} not in data.bgPacmanPaths):
            data.bgPacmanPaths.append({(px,py),(px+dx,py+dy)})
        else:
            data.bgPacmanPaths.remove({(px,py),(px+dx,py+dy)})
        data.backgroundImg = getBackgroundImg(data,data.fill,data.food)
        data.backgroundPhoto = ImageTk.PhotoImage(data.backgroundImg.resize((data.width,data.height),Image.ANTIALIAS))


def mousePressed(event, data):
    #Images top edge is at height//5
    if(data.mode==data.GETBACKGROUND):
        yShift = data.height//5
        xShift = (data.width-data.imgWidth)//2
        (x,y) = (event.x-xShift,event.y-yShift)
        xFactor = data.imgWidth/200
        yFactor = data.imgHeight/200
        if(0<=x<=data.imgWidth and 0<=y<=data.imgHeight):
            x,y = (int(x/xFactor),int(y/yFactor))
            data.selectedBackgroundPos = x,y
            data.drawSelectedBackground = (x*xFactor+xShift,y*yFactor+yShift)
            

    elif(data.mode==data.OUTLINE):
        if(data.stepSize==""):
            return
        yShift = data.height//5
        xShift = (data.width-data.imgWidth)//2
        (x,y) = (event.x-xShift,event.y-yShift)
        xFactor = data.imgWidth/200
        yFactor = data.imgHeight/200
        if(0<=x<=data.imgWidth and 0<=y<=data.imgHeight):
            x,y = (int(x/xFactor),int(y/yFactor))
            step = int(data.stepSize)
            x,y = step*int(x/step),step*int(y/step)
            pix = data.img.load()
            if(pix[x,y] not in data.background): return
            data.startPosition = x,y
            data.drawStartPosition = (x*xFactor+xShift,y*yFactor+yShift)
            data.startPickedError=False
            data.playerPosition = data.startPosition
            data.drawPlayerPosition = data.drawStartPosition
            data.pacmanPosition = data.startPosition
            data.drawPacmanPosition = data.drawStartPosition
            data.startPickedError = False
        data.xFactor = xFactor
        data.yFactor = yFactor
        data.xShift = xShift
        data.yShift = yShift
    elif(data.mode==data.MAZE):
        yShift = data.height//5
        xShift = (data.width-data.imgWidth)//2
        (x,y) = (event.x-xShift,event.y-yShift)
        xFactor = data.imgWidth/200
        yFactor = data.imgHeight/200
        if(0<=x<=data.imgWidth and 0<=y<=data.imgHeight):
            x,y = (int(x/xFactor),int(y/yFactor))
            step = int(data.stepSize)
            x,y = step*int(x/step),step*int(y/step)
            if((x,y) in data.validPaths):
                data.endPosition = x,y
                data.drawEndPosition = (x*xFactor+xShift,y*yFactor+yShift)
                data.endPickedError=False
    pass

def keyPressed(event, data):
    ####START SPLASH SCREEN
    if(data.mode==data.START):
        if(event.keysym=="p"):
            data.mode=data.CHOOSEMODE
            #to reset parameters when 'b' is used to escape crashing
            initImages(data)
        elif(event.keysym=='h'):
            data.mode=data.HOW

    #CHOOSE PICTURE
    elif(data.mode==data.CHOOSEMODE):
        if(event.keysym=="b"):
            data.mode=data.START
            data.imageError=False
        elif(event.keysym=="c"):
            data.file = getFileName(data)
            #safety measure
            if(not data.file.endswith(".gif") and not data.file.endswith(".png")\
                 and not data.file.endswith(".jpg")): 
                data.imageError = True
                return
            data.img = Image.open(data.file)
            data.pixels = data.img.load()
            data.photo = convertImageAndResize(data)
            data.mode = data.DISPLAY

    #DISPLAY PICTURE
    elif(data.mode==data.DISPLAY):
        if(event.keysym=="b" or event.keysym=="n"):
            data.mode=data.CHOOSEMODE
            data.file=None
            data.timer=0
            initImages(data)
        elif(event.keysym in string.digits):
            data.kSize += event.keysym
            data.kNumberError = False
        elif(event.keysym == "d"):
            data.kSize = data.kSize[0:-1]
        elif(data.kSize==""):
            data.kNumberError = True
            return
        elif(event.keysym=="y"):
            data.mode=data.GETBACKGROUND

    elif(data.mode==data.GETBACKGROUND):
        if(event.keysym=="b"):
            data.mode = data.DISPLAY
        elif(data.selectedBackgroundPos==None):
            return
        elif(event.keysym=="y"):
            if(data.outlineSwitch==False):
                data.mode=data.OUTLINE
                processingPleaseWait("...please wait",getImageOutline,data)
                #getImageOutline(data)
                data.outlineSwitch = True

    #OUTLINE MODE
    elif(data.mode==data.OUTLINE):
        if(event.keysym=="b" or event.keysym=='n'):
            data.mode = data.CHOOSEMODE
            data.file=None
            data.timer=0
            init(data)
        elif(event.keysym in string.digits):
            data.stepSize += event.keysym
            data.stepSizeError = False
            #data.startPickedError = False
        elif(event.keysym == "d"):
            data.stepSize = data.stepSize[0:-1]
        elif(data.stepSize==""):
            data.stepSizeError = True
            return
        elif(data.startPickedError):
            return
        elif(event.keysym=="y"):
            data.background.append(data.food)
            data.background.append(data.fill)
            startX,startY = data.startPosition
            step = int(data.stepSize)
            startX,startY = step*int(startX/step),step*int(startY/step)
            pixels = data.img.load()
            if(pixels[(startX,startY)] not in data.background or data.startPosition==None):
                data.startPickedError = True
                return
            data.mode=data.MAZE
            #generate maze
            if(data.mazeSwitch==False):
                processingPleaseWait("...please wait",getMaze,data)
                data.mazeSwitch = True
            pass
    #MAZE MODE
    elif(data.mode==data.MAZE):
        if(data.gameOver):
            if(event.keysym=="b"):
                init(data)
            return
        if(event.keysym=="b"):
            data.mode = data.CHOOSEMODE
            data.file=None
            data.timer=0
            init(data)
        elif(event.keysym=='g'):
            data.mode = data.SOLVER
        elif(event.keysym=="p"):
            data.pacmanDir = (int(data.pacmanStep),0)
            data.mode = data.PACMAN
            data.foodList = getPacmanFoodList(data)
            data.pacmanImg = getPacmanImg(data,(255,0,0),data.food)
            data.pacmanPhoto = ImageTk.PhotoImage(data.pacmanImg.resize((data.width,data.height),Image.ANTIALIAS))
            ###create ghosts
            data.ghosts = dict()
            for i in range(len(data.ghostColors)):
            #for i in range(1):
                position = random.choice(list(data.islands.keys()))
                direction = random.choice([(1,0),(0,1),(-1,0),(0,-1)])
                data.ghosts[i] = Ghost(data,position,data.ghostColors[i],direction)
                data.ghosts[i].lastPosition = position


    elif(data.mode==data.SOLVER):
        if(data.SOLVERWON):
            if(event.keysym=="r"):
                init(data)
            else:
                return
        if(event.keysym=="b"):
            data.mode = data.MAZE
        elif(event.keysym=="s"):
            endX,endY = data.endPosition
            step = int(data.stepSize)
            endX,endY = step*int(endX/step),step*int(endY/step)
            pixels = data.img.load()
            
            #if(pixels[(endX,endY)] not in data.background or data.endPosition==None):
            if(data.endPosition==None):
                data.endPickedError = True
                return
            data.mode = data.SOLUTION
            data.solvedPhoto = drawSolutions(data)
        elif(event.keysym in ["Up","Down","Left","Right"]):
            step = int(data.stepSize)
            #step = 1
            px,py = data.playerPosition
            px,py = int(px),int(py)
            drawPx,drawPy = data.drawPlayerPosition
            def isValidStep(data,px,py,dx,dy):
                allSteps = getAllBridgeCoords({(px,py),(px+dx,py+dy)})
                for step in allSteps:
                    if step not in data.validPaths: return False
                return True
            if(event.keysym=="Up"):
                dx,dy = (0,-step)
            elif(event.keysym=="Down"):
                dx,dy = (0,+step)
            elif(event.keysym=="Left"):
                dx,dy = (-step,0)
            elif(event.keysym=="Right"):
                dx,dy = (+step,0)
            if(isValidStep(data,px,py,dx,dy)):
                data.playerPosition = (px+dx,py+dy)
                data.drawPlayerPosition = (drawPx+dx*data.yFactor,drawPy+dy*data.yFactor)
                if({(px,py),(px+dx,py+dy)} not in data.playerPaths):
                    data.playerPaths.append({(px,py),(px+dx,py+dy)})
                else:
                    data.playerPaths.remove({(px,py),(px+dx,py+dy)})
                data.solverImg = drawBridges(img=data.mazeImg,bridges=data.playerPaths,
                        fill=(0,255,0),background=data.background)
                data.solverImg = data.solverImg.resize((data.width//data.widthFactor,
                                            data.height//data.heightFactor),Image.ANTIALIAS)
                data.solverPhoto = ImageTk.PhotoImage(data.solverImg)
            if(data.playerPosition == data.endPosition):
                data.SOLVERWON = True


    ##Solution
    elif(data.mode==data.SOLUTION):
        if(event.keysym=="b"):
            data.mode=data.SOLVER

    #PACMAN MODE
    elif(data.mode==data.PACMAN):
        if(data.pacmanWIN):
            init(data)
        if(event.keysym=="b"):
            init(data)
        elif(event.keysym in ["Up","Down","Left","Right"]):
            step = data.pacmanStep
            px,py = data.pacmanPosition
            px,py = int(px),int(py)
            drawPx,drawPy = data.drawPacmanPosition
            def isValidStep(data,px,py,dx,dy):
                allSteps = getAllBridgeCoords({(px,py),(px+dx,py+dy)})
                for step in allSteps:
                    if step not in data.validPaths: return False
                return True
            if(event.keysym=="Up"):
                dx,dy = (0,-step)
            elif(event.keysym=="Down"):
                dx,dy = (0,+step)
            elif(event.keysym=="Left"):
                dx,dy = (-step,0)
            elif(event.keysym=="Right"):
                dx,dy = (+step,0)
            data.pacmanDir = (dx,dy)

    #HOW TO PLAY
    elif(data.mode==data.HOW):
        if(event.keysym=="b"):
            data.mode=data.START
    pass

def timerFired(data):
    if(data.mode==data.START or 
        data.mode==data.HOW or data.mode==data.CHOOSEMODE or 
        data.mode==data.DISPLAY or data.mode==data.MAZE or
        data.mode==data.SOLVER or data.mode==data.OUTLINE or
        data.mode==data.GETBACKGROUND or data.mode==data.SOLUTION):
        getBgPacmanDir(data)
        if(data.bgMouthAngleDecreasing):
            data.bgMouthAngle -= 14
        else:
            data.bgMouthAngle += 14
        if(data.bgMouthAngle<10 or data.bgMouthAngle>80):
            data.bgMouthAngleDecreasing = not data.bgMouthAngleDecreasing
        moveBgPacman(data)
    elif(data.mode==data.PACMAN):
        if(data.gameOver or data.pacmanWIN):
            return
        if(data.pacmanR!=250):
            data.pacmanR += 10
        elif(data.pacmanR==250 and data.pacmanG!=250):
            data.pacmanG += 10
        elif(data.pacmanR==10 and data.pacmanG==10 and data.pacmanB!=250):
            data.pacmanB += 10
        else:
            data.pacmanR,data.pacmanG,data.pacmanB = 0,0,0
        r = data.pacmanR 
        g = data.pacmanG
        b = data.pacmanB
        if(data.pacmanB>0):
            g,r = 0,0
        elif(data.pacmanG>0):
            r = 0
        data.pacmanTitleFill = '#%02x%02x%02x' % (r,g,b)
        if(data.invincible):
            data.invincibleTimer -= 1
        if(data.invincibleTimer==0):
            data.invincible = False
        if(data.pacmanWIN):
            data.pacmanWinFill = '#%02x%02x%02x' % (255-r,255-g,255-b)
            return
        if(data.mouthAngleDecreasing):
            data.mouthAngle -= 14
        else:
            data.mouthAngle += 14
        if(data.mouthAngle<10 or data.mouthAngle>80):
            data.mouthAngleDecreasing = not data.mouthAngleDecreasing
        movePacman(data)
        for i in range(len(data.ghosts)):
            moveGhost(data,data.ghosts[i])

#########################################################


def redrawAll(canvas, data):
    #insert: drawBackground
    if(data.mode==data.START or
        data.mode==data.HOW or data.mode==data.CHOOSEMODE or 
        data.mode==data.DISPLAY or data.mode==data.MAZE or
        data.mode==data.SOLVER or data.mode==data.OUTLINE or
        data.mode==data.GETBACKGROUND or data.mode==data.SOLUTION):
        drawBackground(canvas,data)
    if(data.mode==data.START):
        drawSplashScreen(canvas,data)
    elif(data.mode==data.CHOOSEMODE):
        drawChooseMode(canvas,data)
    elif(data.mode==data.HOW):
        drawHelpMode(canvas,data)
    elif(data.mode==data.DISPLAY):
        drawDisplay(canvas,data)
    elif(data.mode==data.GETBACKGROUND):
        drawGetBackground(canvas,data)
    elif(data.mode==data.OUTLINE):
        drawRightOutline(canvas,data)
    elif(data.mode==data.MAZE):
        drawMazeMode(canvas,data)
    elif(data.mode==data.SOLUTION):
        drawSolution(canvas,data)
    elif(data.mode==data.SOLVER):
        drawSolverMode(canvas,data)
    elif(data.mode==data.PACMAN):
        drawPacmanMode(canvas,data)
    pass

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    init(data)
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(800, 800)
