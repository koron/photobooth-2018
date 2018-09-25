import cv2
import numpy as np

class filters:

    @staticmethod
    def gaussian_blur(mask, radius):
        return cv2.GaussianBlur(mask, (radius, radius), 0)

    @staticmethod
    def threshold(src, p, typ=cv2.THRESH_BINARY):
        r, dst = cv2.threshold(src, p, 255, typ)
        return dst

    @staticmethod
    def clahe(src):
        lab1 = cv2.cvtColor(src, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab1)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        lab2 = cv2.merge((clahe.apply(l), a, b))
        return cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)

    @staticmethod
    def combine(bg, fg, mask):
        m = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255
        return (bg * (1 - m) + fg * m).astype(np.uint8)

    @staticmethod
    def combine_png(bg, png):
        fg, alpha = png[:,:,:3], png[:,:,3]
        return filters.combine(bg, fg, alpha)

    @staticmethod
    def fill_bg(src, mask, bgcolor=(0, 0, 0)):
        bg = np.tile(np.uint8(bgcolor), src.shape[:2] + (1,))
        return filters.combine(bg, src, mask)

    @staticmethod
    def get_fg(src, blur, threshold=112, bgcolor=(255,255,255)):
        """
        blurマスクを使って前景を取り出し、色を調整する。
        """
        mask = filters.threshold(blur, threshold)
        mid = filters.fill_bg(src, mask, bgcolor)
        return filters.clahe(mid)

    @staticmethod
    def smooth_mask(blur, threshold=160, radius=3):
        binary = filters.threshold(blur, threshold)
        return filters.gaussian_blur(binary, radius)

    @staticmethod
    def center(img, sz):
        h = img.shape[0]
        w = img.shape[1]
        left = int((w - sz[0]) / 2)
        right = left + sz[0]
        top = int((h - sz[1]) / 2)
        bottom = top + sz[1]
        if left == 0 and top == 0 and w == sz[0] and h == sz[1]:
            return img
        return img[top:bottom, left:right]
