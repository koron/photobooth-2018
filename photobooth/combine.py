import numpy as np
import cv2

def combine(bg, fg, mask):
    m = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255
    return (bg * (1 - m) + fg * m).astype(np.uint8)
