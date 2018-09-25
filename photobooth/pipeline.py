import cv2
import numpy as np

from .gcmask import gcmask
from .filters import filters

class pipeline:

    @staticmethod
    def get_near(cap, meter, useHist=True, blurRadius=65):
        if cap.colorDepth is not None and useHist:
            depth = gcmask.histogram(cap.colorDepth)
        else:
            depth = gcmask.threshold(cap.depth, meter / cap.depthScale)
        mono = gcmask.monochrome(gcmask.grabcut(cap.color, depth))
        blur = filters.gaussian_blur(mono, blurRadius)
        img = filters.get_fg(cap.color, blur)
        mask = filters.smooth_mask(blur)
        return img, mask

    @staticmethod
    def apply_theme(img, mask, theme):
        dst = np.copy(theme.back)
        if theme.mid is not None:
            dst = filters.combine_png(dst, theme.mid) 

        sz = theme.size()
        img = filters.center(img, sz)
        mask = filters.center(mask, sz)
        dst = filters.combine(dst, img, mask)

        if theme.over is not None:
            dst = filters.combine_png(dst, theme.over)

        return dst

    @staticmethod
    def step_by_step(cap, meter, theme=None, blurRadius=33):
        yield cap.color
        yield cap.colorDepth
        rough = cap.rough_fgmask(meter)
        yield rough
        pre_gc = gcmask.threshold(cap.depth, meter / cap.depthScale)
        yield gcmask.grey(pre_gc)
        post_gc = gcmask.grabcut(cap.color, pre_gc)
        yield gcmask.grey(post_gc)
        mono = gcmask.monochrome(post_gc)
        yield mono
        blur = filters.gaussian_blur(mono, blurRadius)
        yield blur
        mask = filters.threshold(blur, 112)
        yield mask
        mask = filters.smooth_mask(mask)
        yield mask
        yield cap.color
        mid = filters.fill_bg(cap.color, mask)
        yield mid
        clahe = filters.clahe(mid)
        yield clahe
        if theme is not None:
            fg = pipeline.apply_theme(clahe, mask, theme)
            yield fg
