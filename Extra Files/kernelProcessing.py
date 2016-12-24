from PIL import Image
from convertImage import *
import numpy as np
import math

def make2dList(rows, cols):
    a=[]
    for row in range(rows): a += [[0]*cols]
    return a

GAUSSIANBLUR = [[1,2,1],
                [2,4,2],
                [1,2,1]]

GAUSSIANBLUR2 = [[1,4,7,4,1],
                [4,16,26,16,4],
                [7,26,41,26,7],
                [4,16,26,16,4],
                [1,4,7,4,1]]

NORMALBLUR = [[1,1,1],
              [1,1,1],
              [1,1,1]]

NORMALBLUR2 = [[1,1,1,1,1],
               [1,1,1,1,1],
               [1,1,1,1,1],
               [1,1,1,1,1],
               [1,1,1,1,1]]

SOBELX = [[-1,0,1],
          [-2,0,2],
          [-1,0,1]]

SOBEL3X = [[-3,0,3],
          [-6,0,6],
          [-3,0,3]]

SOBELY = [[-1,-2,-1],
          [0,0,0],
          [1,2,1]]

SOBEL3Y = [[-3,-6,-3],
          [0,0,0],
          [3,6,3]]

fileName = "clinton.jpg"

img = Image.open(fileName)
pixels = img.load()
newImg = Image.open(fileName)
width,height = img.size
thetaMat = make2dList(height,width)

def kernelOperator(kernel,x,y,pixels,newPixels):
    kernelRangeX, kernelRangeY = len(kernel[0]),len(kernel)
    kernelSum = 0
    sumOfKernelElements = 0
    for kx in range(kernelRangeX):
        for ky in range(kernelRangeY):
            #print((ky,kx),(x-kernelRangeX//2+kx,y-kernelRangeY//2+ky))
            #y is row, x is col, multiplies kernel by pixel and stores in newPix
            kernelSum += kernel[ky][kx]*pixels[x-kernelRangeX//2+kx,
                            y-kernelRangeY//2+ky][0]
            sumOfKernelElements += abs(kernel[ky][kx])
    kernelAvg = int(round(kernelSum/sumOfKernelElements))
    newPixels[x,y] = (kernelAvg,kernelAvg,kernelAvg)


# def kernelOperator(kernel,x,y,pixels,newPixels):
#     kernelRangeX, kernelRangeY = len(kernel[0]),len(kernel)
#     kernelSum = 0
#     pixMatrix = [[None]*kernelRangeX for val in range(kernelRangeY)]
#     for kx in range(kernelRangeX):
#         for ky in range(kernelRangeY):
#             #print((ky,kx),(x-kernelRangeX//2+kx,y-kernelRangeY//2+ky))
#             #y is row, x is col, multiplies kernel by pixel and stores in newPix
#             pixMatrix[kx][ky] = pixels[x-kernelRangeX//2+kx, y-kernelRangeY//2+ky][0]
#     kMat = np.asmatrix(kernel)
#     pMat = np.asmatrix(pixMatrix)
#     kernelSum = np.sum(np.multiply(kMat,pMat))
#     kernelAvg = int(round(kernelSum/(kernelRangeX*kernelRangeY)))
#     newPixels[x,y] = (kernelAvg,kernelAvg,kernelAvg)

def kernelProcessing(kernel,img,newImg):
    width,height = img.size
    kernelRangeX, kernelRangeY = len(kernel[0]),len(kernel)
    pixels = img.load()
    newPixels = newImg.load()
    convertRGBToBW(img)
    for x in range(kernelRangeX//2,width-kernelRangeX//2):
        for y in range(kernelRangeY//2,height-kernelRangeY//2):
            kernelOperator(kernel,x,y,pixels,newPixels)

def sobelOperator(sobelX,sobelY,x,y,pixels,newPixels,thetaMat):
    kernelRangeX, kernelRangeY = len(sobelX[0]),len(sobelX)
    sobelXG = 0
    sobelYG = 0
    sumOfKernelElements = 4
    for kx in range(kernelRangeX):
        for ky in range(kernelRangeY):
            #print((ky,kx),(x-kernelRangeX//2+kx,y-kernelRangeY//2+ky))
            #y is row, x is col, multiplies kernel by pixel and stores in newPix
            sobelXG += sobelX[ky][kx]*pixels[x-kernelRangeX//2+kx,
                            y-kernelRangeY//2+ky][0]
            sobelYG += sobelY[ky][kx]*pixels[x-kernelRangeX//2+kx,
                            y-kernelRangeY//2+ky][0]
    if(sobelXG==0 and sobelYG==0): theta = math.pi
    elif (sobelYG!=0 and sobelXG == 0): theta = math.pi/2
    else: theta = math.atan(sobelYG/sobelXG)
    #this aggregates the x gradient and y gradient
    kernelAvg = int(round((sobelXG**2+sobelYG**2)**0.5/sumOfKernelElements))
    newPixels[x,y] = (kernelAvg,kernelAvg,kernelAvg)
    #this is the orientation of the x gradient vs. y gradient
    thetaMat[y][x] = abs(theta) if theta>=0 else abs(theta+math.pi)

def sobelFilter(sobelX,sobelY,img,newImg,thetaMat):
    width,height = img.size
    RangeX, RangeY = len(sobelX[0]),len(sobelX)
    pixels = img.load()
    newPixels = newImg.load()
    convertRGBToBW(img)
    #first blurring
    kernelProcessing(GAUSSIANBLUR2,img,newImg)
    for x in range(RangeX//2,width-RangeX//2):
        for y in range(RangeY//2,height-RangeY//2):
            sobelOperator(sobelX,sobelY,x,y,pixels,newPixels,thetaMat)
    #print(thetaMat)
    return newPixels,thetaMat


#thetaMat is a matrix of orientation of each pixel
def cannyFilter(sobelX,sobelY,img,newImg,finalImg,thetaMat,tHigh,tLow):
    width,height = img.size
    pixels = img.load()
    newPixels,thetaMat = sobelFilter(sobelX,sobelY,img,newImg,thetaMat)
    finalPixels = finalImg.load()
    #Step 1: Non-Max suppression
    for x in range(1,width-1):
        for y in range(1,height-1):
            roundedTheta = int(round(thetaMat[y][x]/math.pi*4))
            #Edge runs North-South
            if(roundedTheta==0):
                edgeDir1 = (+1,0) #East
                edgeDir2 = (-1,0) #West
            #Edge runs NW-SE
            elif(roundedTheta==1):
                edgeDir1 = (-1,+1) #SW
                edgeDir2 = (+1,-1) #NE
            #Edge runs West-East
            elif(roundedTheta==2):
                edgeDir1 = (0,-1) #North
                edgeDir2 = (0,+1) #South
            #Edge runs NE-SW
            elif(roundedTheta==3):
                edgeDir1 = (-1,-1) #NW
                edgeDir2 = (+1,+1) #SE
            elif(roundedTheta==4):
                continue
            #if it is a max (after non-max suppression)
            if(not cannyCompare(edgeDir1,edgeDir2,x,y,newPixels)):
                newPixels[x,y] = (0,0,0)
    #Step 2: Double Threshold / Hysteresis
    for x in range(1,width-1):
        for y in range(1,height-1):
            if(newPixels[x,y] != (0,0,0)):
                #If false, then not connected
                if(isWithinThreshold(tHigh,tLow,newPixels,x,y) == False):
                    newPixels[x,y] = (0,0,0)


def cannyCompare(Dir1,Dir2,x,y,pixels):
    dx1,dy1 = Dir1
    dx2,dy2 = Dir2
    #x,y is a maximum, so it is an edge
    return (pixels[x,y]>pixels[x+dx1,y+dy1] and pixels[x,y]>pixels[x+dx2,y+dy2])

#blob analysis to determine if current pixel (x,y) has strong pixel near it
#Anything above high is rated "strong", anything below Low is rated "weak" and 
#immediately eliminated.
#Anything between High and Low, while connected to high is kept, else discard
def isWithinThreshold(tHigh,tLow,newPixels,x,y):
    connected = False
    if(newPixels[x,y][0] < tLow):
        newPixels[x,y] = (0,0,0)
        return None
    elif(newPixels[x,y][0]>=tHigh):
        newPixels[x,y] = (255,255,255)
        return None
    else:
        for dx in range(-1,2):
            for dy in range(-1,2):
                if(newPixels[x+dx,y+dy][0]>=tHigh):
                    connected = True
        return connected




finalImg = Image.open(fileName)

#kernelProcessing(GAUSSIANBLUR2,img,newImg)
#convertRGBToBW(img)
#sobelFilter(SOBELX,SOBELY,img,newImg,thetaMat)
#newImg.save("ObamaEdge.jpg")
cannyFilter(SOBELX,SOBELY,img,newImg,finalImg,thetaMat,40,30) #Don't really need finalImg
#newImg.save("test.jpg")
newImg.show()
#newImg.save("cannyCoin.jpg")
#finalImg.show()
# convertRGBToBW(img)
# newPixels = newImg.load()
# kernelOperator(GAUSSIANBLUR,1,1,pixels,newPixels)
# print(pixels[0,0],pixels[0,1],pixels[0,2],pixels[1,0],pixels[1,1],pixels[1,2],pixels[2,0],pixels[2,1],pixels[2,2])







