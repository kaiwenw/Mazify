from PIL import Image

img = Image.open("pacman.png")
#img = img.convert("RGB")
img = img.resize((400,400),Image.ANTIALIAS)
pixels = img.load()
width,height = img.size
step = 5
for x in range(width):
    for y in range(height):
        if(pixels[x,y]==(0,0,0,0)):
            pixels[x,y] = (255,255,255)
        else:
            pixels[x,y] = (0,0,0)
        # if((height-y)<step):
        #     print(pixels[x,y])
        #     pixels[x,y] = (255,255,255)
img.show()

# img.save("mapleleaf.png")


