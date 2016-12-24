from PIL import Image

# def convertImage(name):
    
#     image = Image.open(name)
#     image = image.convert('RGB')
#     image.save('out.png')

# convertImage("./morphologyTest/dil1.GIF")



#thresholding and conversion
def convertFromRGBToBW2(pixels, img):
    width, height = img.size #tuple containing width and height of image
    t = 200
    for x in range(width):
        for y in range(height):
            (R,G,B) = pixels[x,y]
            total = R+G+B
            avg = total//3
            if(avg>t):
                pixels[x,y] = (0,0,0)
            else:
                pixels[x,y] = (255,255,255)


def convertFromRGBToBW3(pixels, img):
    width,height = img.size
    t = 20
    for x in range(width):
        for y in range(height):
            (R,G,B) = pixels[x,y]
            total = R+G+B
            avg = total//3
            if(avg>t):
                pixels[x,y] = (255,255,255)
            else:
                pixels[x,y] = (0,0,0)

def convertRGBToBW(img):
    width,height = img.size
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            (R,G,B) = pixels[x,y]
            total = R+G+B
            avg = total//3
            pixels[x,y] = (avg,avg,avg)
    return pixels



# img = Image.open("maze2.jpg")
# pixels = img.load()
# convertFromRGBToBW2(pixels,img)
# img.show()
# print('hello')
# img.close()
