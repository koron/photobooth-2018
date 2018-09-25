import os
from datetime import datetime
from logging import getLogger, StreamHandler, INFO, DEBUG

import cv2
from PyQt5.QtCore import QObject, pyqtSignal

from photobooth import pipeline
from photobooth import filters

handler = StreamHandler()
handler.setLevel(DEBUG)
logger = getLogger(__name__)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

class SavedItem:
    def __init__(self, basename, capname, maskname, fg, mask, results):
        self.basename = basename
        self.capname = capname
        self.maskname = maskname
        self.fg = fg
        self.mask = mask
        self.results = results

class SaveWorker(QObject):

    finished = pyqtSignal(object)

    def __init__(self, parent, config, cap, themes):
        QObject.__init__(self)
        self.parent = parent
        self.cap = cap
        self.config = config
        self.themes = themes

    def save(self):
        basename = datetime.now().strftime('%Y%m%d/%H/%Y%m%dT%H%M%S')
        maskname = os.path.join(self.config.vardir, 'mid', basename)
        capname = os.path.join(self.config.vardir, 'raw', basename)
        # mask: generate
        logger.debug('mask generating: %s' % basename)
        fg, mask = pipeline.get_near(self.cap, self.config.distance,
                useHist=self.config.mask_use_histogram,
                blurRadius=self.config.mask_blur_radius)
        # save mask
        logger.debug('masks saving: %s' % maskname)
        os.makedirs(os.path.dirname(maskname), exist_ok=True)
        cv2.imwrite(maskname + '.fg.jpg', fg)
        cv2.imwrite(maskname + '.mask.png', mask)
        # save captured image.
        logger.debug('capture saving: %s' % capname)
        os.makedirs(os.path.dirname(capname), exist_ok=True)
        self.cap.save(capname)
        # apply themes
        logger.debug('theme applying')
        results = []
        res_fg = filters.center(fg, self.config.size)
        res_mask = filters.center(mask, self.config.size)
        for t in self.themes:
            curr = pipeline.apply_theme(fg, mask, t)
            results.append(curr)

        self.finished.emit(SavedItem(basename, capname, maskname, fg, mask, results))
