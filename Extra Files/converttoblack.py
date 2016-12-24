from PIL import Image

img = Image.open("blackBackground.jpg")
pixels = img.load()
width,height = img.size
#img = img.convert("RGB")
step = 10
for x in range(width):
    for y in range(height):
        if(((height-y)<step)):
            pixels[x,y] = (255,255,255)
            print(pixels[x,y])
        else:
            pixels[x,y] = (0,0,0)
img.show()

img.save("blackBackground.jpg")


