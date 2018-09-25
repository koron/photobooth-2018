from logging import getLogger, StreamHandler, INFO, DEBUG

import cv2
from PyQt5.QtCore import QObject, pyqtSignal

handler = StreamHandler()
handler.setLevel(DEBUG)
logger = getLogger(__name__)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

class UploadWorker(QObject):

    uploaded = pyqtSignal(object)

    def __init__(self, parent, config, api, name):
        QObject.__init__(self)
        self.parent = parent
        self.config = config
        self.api = api
        self.name = name

    def upload(self):
        self.api.uploadPhoto(self.name, caption=self.config.instagram_caption)
        self.uploaded.emit(True)
