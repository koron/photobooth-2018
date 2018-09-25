import cv2

class Erosion:
    def __init__(self, size=3):
        self.size = size
        self.less = Erosion._gen_element(size)
        self.more = Erosion._gen_element(size * 2)

    def _gen_element(size):
        return cv2.getStructuringElement(cv2.MORPH_RECT, (size+1, size+1), (size, size))

    def create_mask(self, depth, thresh, typ):
        ret, depth = cv2.threshold(depth, thresh, 255, typ)
        return self.filter(depth)

    def filter(self, mat):
        return cv2.erode(cv2.dilate(mat, self.less), self.more)
