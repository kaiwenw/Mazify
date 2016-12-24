from PIL import Image
import random
import copy


def getPixMatrix(img):
    width,height = img.size
    result = [[None]*width for i in range(height)]
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            result[y][x] = pixels[x,y]
    return result

def turnMatrixToPix(matrix, pix):
    width,height = len(matrix[0]),len(matrix)
    for x in range(width):
        for y in range(height):
            pix[x,y] = matrix[y][x]
    return pix

def getDistance(pix1,pix2):
    r1,g1,b1 = pix1
    r2,g2,b2 = pix2
    return ((r2-r1)**2+(g2-g1)**2+(b2-b1)**2)**0.5

def kMeans(k,dataPts,img,iterationIndex = 5):
    pix = img.load()
    #miu is the centroids
    miu = [[None] for i in range(k)]
    #assume dataPts is a matrix
    a = copy.deepcopy(dataPts)
    yRange,xRange = len(a),len(a[0])
    #random initialization of dataPts
    for i in range(k):
        r,g,b = random.randint(0,255),random.randint(0,255),random.randint(0,255)
        miu[i] = (r,g,b)

    #while(*until Convergence*):
    for i in range(iterationIndex):
        #find nearest centroid for all points
        for y in range(yRange):
            for x in range(xRange):
                minDist = 255**3 #largest possible distance
                minCentroid = 0
                #find minimum distance to centroid
                for i in range(k):
                    dist = getDistance(miu[i],dataPts[y][x])
                    if(dist<minDist):
                        minDist = dist
                        minCentroid = i
                a[y][x] = minCentroid

        for i in range(k):
            rNew,gNew,bNew = 0,0,0
            n = 0 #number of points assigned to this centroid
            for x in range(xRange):
                for y in range(yRange):
                    if(a[y][x]==i):
                        r,g,b = dataPts[y][x]
                        rNew += r
                        gNew += g
                        bNew += b
                        n += 1
            if(n==0): continue
            rNew //= n
            gNew //= n
            bNew //= n
            miu[i] = (rNew,gNew,bNew)
    #fill pixels with centroid pixels
    for x in range(xRange):
        for y in range(yRange):
            centroid = a[y][x]
            pix[x,y] = miu[centroid]
    return img,miu
