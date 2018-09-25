import cv2
import numpy as np
import os

from .gcmask import gcmask

class Capture:

    def __init__(self, color, depth, depthScale, colorDepth=None):
        self.color = color
        self.depth = depth
        self.depthScale = depthScale
        self.colorDepth = colorDepth

    def save(self, name):
        cv2.imwrite('%s.color.jpg' % name, self.color)
        np.savez_compressed('%s.depth.npz' % name, depth=self.depth, scale=self.depthScale)
        if self.colorDepth is not None:
            cv2.imwrite('%s.depth.png' % name, self.colorDepth)

    def rough_fgmask(self, distance):
        m = gcmask.threshold(self.depth, distance / self.depthScale)
        m = gcmask.monochrome(m)
        return m

    def rough_fg(self, distance, color=(0,0,0), bg=None):
        if bg is None:
            bg = np.tile(np.uint8(color), self.color.shape[:2] + (1,))
        mask = self.rough_fgmask(distance)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        return np.where(mask == 255, self.color, bg)

    @staticmethod
    def load(name):
        color = cv2.imread('%s.color.jpg' % name)
        with np.load('%s.depth.npz' % name) as npz:
            depth = npz['depth']
            scale = npz['scale']
        f = '%s.depth.png' % name
        if not os.path.exists(f):
            return Capture(color, depth, scale)
        colorDepth = cv2.imread(f)
        return Capture(color, depth, scale, colorDepth)
