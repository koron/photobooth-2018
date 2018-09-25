import numpy as np
import cv2

from .erosion import Erosion

class gcmask:

    @staticmethod
    def threshold(depth, threshold):
        """
        creates a grabcut's mask from depth image with threshold.
        """
        mask = np.full(depth.shape, cv2.GC_PR_BGD, dtype=np.uint8)
        mask[depth >= threshold] = cv2.GC_BGD
        mask[depth < threshold] = cv2.GC_FGD
        mask[depth <= 0] = cv2.GC_PR_BGD
        return mask

    @staticmethod
    def histogram(depth, near_bottom=180, far_upper=100, erosion_size=5):
        erosion = Erosion(erosion_size)

        near = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY)
        near = erosion.create_mask(near, near_bottom, cv2.THRESH_BINARY)

        far = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY)
        far[far == 0] = 255
        far = erosion.create_mask(far, far_upper, cv2.THRESH_BINARY_INV)

        mask = np.full(near.shape, cv2.GC_BGD, dtype=np.uint8)
        mask[far == 0] = cv2.GC_PR_BGD
        mask[near == 255] = cv2.GC_FGD
        return mask

    @staticmethod
    def grabcut(img, mask):
        """
        applies a grabcut algorithm to the mask.
        """
        rect = (0, 0, img.shape[1], img.shape[0])
        bg = np.zeros((1, 65), np.float64)
        fg = np.zeros((1, 65), np.float64)
        cv2.grabCut(img, mask, rect, bg, fg, 1, cv2.GC_INIT_WITH_MASK)
        return mask

    @staticmethod
    def grey(src):
        """
        generate grey scale image of the mask.
        """
        mask = np.zeros(src.shape, dtype=np.uint8)
        mask[src == cv2.GC_FGD] = 255
        mask[src == cv2.GC_PR_FGD] = 192
        mask[src == cv2.GC_PR_BGD] = 64
        return mask

    @staticmethod
    def grabcut_grey(img, mask):
        """
        applies a grabcut algorithm and return its colored image.
        """
        return gcmask.grey(gcmask.grabcut(img, mask))

    @staticmethod
    def monochrome(mask, threshold=127):
        """
        generate monochrome image of the mask.
        """
        ret, dst = cv2.threshold(gcmask.grey(mask), threshold, 255, cv2.THRESH_BINARY)
        return dst
