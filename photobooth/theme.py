import os
import numpy as np
import cv2

class Theme:
    def __init__(self, back, over, mid=None):
        self.back = back
        self.over = over
        self.mid = mid

    def _load(name):
        if not os.path.exists(name):
            return None
        return cv2.imread(name, cv2.IMREAD_UNCHANGED)

    def load(name):
        back = cv2.imread('%s.back.png' % name)
        if back is None:
            raise Exception("can't read theme's back: " + name)
        over = Theme._load('%s.over.png' % name)
        mid = Theme._load('%s.mid.png' % name)
        return Theme(back, over, mid)

    def _resize(img, w, h):
        if img is None:
            return None
        return cv2.resize(img, (w, h))

    def resize(self, w, h):
        back = Theme._resize(self.back, w, h)
        over = Theme._resize(self.over, w, h)
        mid  = Theme._resize(self.mid, w, h)
        return Theme(back, over, mid)

    def size(self):
        return (self.back.shape[1], self.back.shape[0])
