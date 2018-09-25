import sys
import os
import threading
import random
from pathlib import Path
from datetime import datetime
from logging import getLogger, StreamHandler, INFO, DEBUG

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import cv2
import numpy as np

from photobooth import D415
from photobooth import Capture
from photobooth import Theme
from photobooth import filters
from photobooth import pipeline
from photobooth import patterns
import gui
import config

handler = StreamHandler()
handler.setLevel(DEBUG)
logger = getLogger(__name__)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

class CameraWindow(QtWidgets.QMainWindow):

    shooted = QtCore.pyqtSignal(object)
    combined = QtCore.pyqtSignal(object)
    uploaded = QtCore.pyqtSignal(object)

    def __init__(self):
        super(CameraWindow, self).__init__()
        self.initUI()
        self.instaAPI = None
        if config.instagram_enable:
            w = gui.LoginWorker(self, config)
            w.loggedIn.connect(self.loggedIn)
            w.start()

    def initUI(self):
        self.countImages = [
            QtGui.QPixmap('resource/count1.png'),
            QtGui.QPixmap('resource/count2.png'),
            QtGui.QPixmap('resource/count3.png'),
            QtGui.QPixmap('resource/count4.png'),
            QtGui.QPixmap('resource/count5.png'),
        ]
        self.themes = [
            Theme.load('theme/01').resize(*config.size),
            Theme.load('theme/02').resize(*config.size),
            Theme.load('theme/03').resize(*config.size),
            Theme.load('theme/04').resize(*config.size),
            Theme.load('theme/05').resize(*config.size),
        ]

        self.setWindowTitle('Camera - Photobooth 2018')

        self.cameraWidget = gui.ImageWidget(config)
        self.setCentralWidget(self.cameraWidget)
        self.setupLabels(showShoot=True)

        self.camera = D415()
        self.camera.enable_colorize(True)
        self.captureTimer = QtCore.QTimer(self)
        self.captureTimer.timeout.connect(self.capture)
        self.captureTimer.start(50)

        self.completeTimer = QtCore.QTimer(self)

        self.transparentBg = patterns.transparent()

    def loggedIn(self, instaAPI):
        self.instaAPI = instaAPI
        self.shootLabel.show()

    def setupLabels(self, showShoot=True):
        shoot = QtWidgets.QLabel('shoot', self)
        shoot.setPixmap(QtGui.QPixmap('resource/camera.png'))
        shoot.move(1920-512-20, 1080-512)
        shoot.resize(512, 512)
        shoot.mousePressEvent = self.shootPrepare
        if not showShoot:
            shoot.hide()
        self.shootLabel = shoot

        count = QtWidgets.QLabel('count', self)
        count.resize(800, 800)
        count.move((1920-800) / 2, (1080 - 800) / 2)
        count.hide()
        self.countLabel = count

        hourglass = QtWidgets.QLabel('hourglass', self)
        hourglass.setPixmap(QtGui.QPixmap('resource/hourglass.png'))
        hourglass.setGeometry(1920 - 512, 40, 512, 512)
        hourglass.hide()
        self.hourglass = hourglass

    def capture(self):
        c = self.camera.capture()
        if c is None:
            return
        self.lastCapture = c
        img = c.rough_fg(config.distance, bg=self.transparentBg)
        img = cv2.flip(img, 1)
        x1 = int((1920 - 1080) / 2)
        x2 = int(x1 + 1080)
        cv2.line(img, (x1, 0), (x1, 1079), (0, 0, 255), 2)
        cv2.line(img, (x2, 0), (x2, 1079), (0, 0, 255), 2)
        self.cameraWidget.setImage(img)

    def shootPrepare(self, event):
        self.shootCount = config.countdown - 1
        self.shootLabel.hide()
        self.countLabel.show()
        self.countLabel.setPixmap(self.countImages[self.shootCount])
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.shootCountdown)
        timer.start(1000)
        self.countdownTimer = timer

    def shootCountdown(self):
        self.shootCount -= 1
        if self.shootCount < 0:
            self.countdownTimer.stop()
            self.countdownTimer = None
            return self.shootExec()
        self.countLabel.setPixmap(self.countImages[self.shootCount])

    def shootExec(self):
        self.captureTimer.stop()
        self.countLabel.hide()
        self.hourglass.show()
        if self.lastCapture is None:
            return self.restartCamera()
        self.shooted.emit(self.lastCapture.color)
        w = gui.SaveWorker(self, config, self.lastCapture, self.themes)
        w.finished.connect(self.chooseTheme)
        thread = threading.Thread(target=w.save)
        thread.start()

    def chooseTheme(self, savedItem):
        self.hourglass.hide()
        uploadWidget = gui.UploadWidget(config)
        uploadWidget.chosen.connect(self.chosenTheme)
        uploadWidget.setImages(savedItem.results)
        self.lastBasename = savedItem.basename
        self.lastResults = savedItem.results
        self.setCentralWidget(uploadWidget)
        self.combined.emit(random.choice(savedItem.results))

    def chosenTheme(self, num):
        self.cameraWidget = gui.ImageWidget(config)
        self.setCentralWidget(self.cameraWidget)
        if num >= 0 and num < len(self.lastResults):
            self.setupLabels(showShoot=False)
            logger.debug('uploading %d' % num)
            img = self.lastResults[num]
            self.lastResults = None
            self.cameraWidget.setImage(img)
            return self.uploadImage(self.lastBasename, img)
        self.setupLabels()
        logger.debug('canceled')
        logger.debug('')
        self.lastResults = None
        self.restartCamera()

    def uploadImage(self, basename, img):
        self.hourglass.show()
        name = os.path.join(config.vardir, 'upload', basename+'.jpg')
        os.makedirs(os.path.dirname(name), exist_ok=True)
        cv2.imwrite(name, img)
        self.uploaded.emit(img)
        if self.instaAPI is None:
            self.hourglass.hide()
            self.restartCamera()
            return
        w = gui.UploadWorker(self, config, self.instaAPI, name)
        w.uploaded.connect(self.uploadedImage)
        thread = threading.Thread(target=w.upload)
        thread.start()
        self.completeTimer.singleShot(5000, self.returnToCamera)

    def uploadedImage(self, data):
        logger.debug('uploaded: %s' % data)
        logger.debug('')

    def returnToCamera(self):
        self.hourglass.hide()
        self.restartCamera()

    def restartCamera(self):
        self.shootLabel.show()
        self.captureTimer.start()

class SubWindow(QtWidgets.QMainWindow):

    def __init__(self, parent):
        super(SubWindow, self).__init__(parent)
        self.setStyleSheet('background-color: #204080')
        self.imageWidget = gui.ImageWidget(config)
        self.setCentralWidget(self.imageWidget)
        self.defaultBG = np.tile(np.uint8((128, 64, 32)), (1080, 1920, 1))
        self.bindToMain(parent)
        self.returnTimer = QtCore.QTimer(self)
        self.returnTimer.timeout.connect(self.returnDefault)
        self.returnTimeout = config.sub_return_timeout
        self.steadyTimer = QtCore.QTimer(self)
        self.steadyTimer.timeout.connect(self.showSteady)
        self.steadyTimeout = config.sub_steady_interval
        self.steadyTimer.timeout.connect(self.showSteady)

        self.showSteady()
        self.steadyTimer.start(self.steadyTimeout)

    def bindToMain(self, main):
        self.mainWindow = main  
        main.shooted.connect(self.showTemporary)
        main.combined.connect(self.showTemporary)
        main.uploaded.connect(self.showTemporary)

    def setImage(self, image):
        self.imageWidget.setImage(image)

    def returnDefault(self):
        self.returnTimer.stop()
        self.steadyTimer.start(self.steadyTimeout)
        self.showSteady()

    def showTemporary(self, img):
        self.steadyTimer.stop()
        self.returnTimer.stop()
        self.returnTimer.start(self.returnTimeout)
        self.setImage(img)

    def showSteady(self):
        p = Path(os.path.join(config.vardir, 'upload'))
        files = list(p.glob('**/*.jpg'))
        f = random.choice(files)
        img = cv2.imread(f.as_posix())
        self.setImage(img)

def main():
    app = QtWidgets.QApplication(sys.argv)
    w1 = CameraWindow()
    desktop = app.desktop()
    if desktop.screenCount() >= 2:
        w2 = SubWindow(w1)
        w2.setGeometry(desktop.screenGeometry(1))
        w2.showFullScreen()
    w1.showFullScreen()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
