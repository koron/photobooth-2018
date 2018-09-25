import numpy as np

def transparent(size=(1080, 1920), color1=(224, 224, 224), color2=(192, 192, 192)):
    img = fill(color=color1, size=size)
    d = 8
    for y in range(size[0]):
        for x in range(size[1]):
            if (int(x/d) + int(y/d)) % 2 == 1:
                img[y][x] = color2
    return img

def fill(size=(1080, 1920), color=(0,0,0)):
    return np.tile(np.uint8(color), size + (1,))
