import cv2

class Monitor:
    def __init__(self, factor=1.0):
        self.factor = factor

    def showMain(self, img):
        if self.factor != 1.0:
            w = int(img.shape[1] * self.factor)
            h = int(img.shape[0] * self.factor)
            img = cv2.resize(img, (w, h))
        cv2.imshow('Main Monitor', img)

    def waitKey(self, wait=0):
        return cv2.waitKey(wait) & 0xFF

    def close(self):
        cv2.destroyAllWindows()
