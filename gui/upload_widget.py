import cv2

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from .pixmap import toQPixmap

class UploadWidget(QtWidgets.QWidget):

    chosen = QtCore.pyqtSignal(object)
    size = (480, 480)
    margin = (16, 16)

    def __init__(self, config):
        super(UploadWidget, self).__init__()
        self.config = config

        self.label1 = QtWidgets.QLabel('item1', self)
        self.label2 = QtWidgets.QLabel('item2', self)
        self.label3 = QtWidgets.QLabel('item3', self)
        self.label4 = QtWidgets.QLabel('item4', self)
        self.label5 = QtWidgets.QLabel('item5', self)
        self.label6 = QtWidgets.QLabel('cancel', self)

        self.label1.resize(*self.size)
        self.label2.resize(*self.size)
        self.label3.resize(*self.size)
        self.label4.resize(*self.size)
        self.label5.resize(*self.size)
        self.label6.resize(*self.size)

        x = (1920 - (self.size[0]*3 + self.margin[0] * 2)) / 2
        y = (1080 - (self.size[1]*2 + self.margin[1])) / 2
        dx = self.size[0] + self.margin[0]
        dy = self.size[1] + self.margin[1]
        self.label1.move(x + dx*0, y + dy*0)
        self.label2.move(x + dx*1, y + dy*0)
        self.label3.move(x + dx*2, y + dy*0)
        self.label4.move(x + dx*0, y + dy*1)
        self.label5.move(x + dx*1, y + dy*1)
        self.label6.move(x + dx*2, y + dy*1)

        self.label1.mousePressEvent = self.makeChoice0
        self.label2.mousePressEvent = self.makeChoice1
        self.label3.mousePressEvent = self.makeChoice2
        self.label4.mousePressEvent = self.makeChoice3
        self.label5.mousePressEvent = self.makeChoice4
        self.label6.mousePressEvent = self.makeChoice5

        self.labels = [
            self.label1,
            self.label2,
            self.label3,
            self.label4,
            self.label5,
            self.label6,
        ]

        self.label6.setPixmap(QtGui.QPixmap('resource/cancel.png'))

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.timeoutTick)
        self.cancelMax = config.choose_timeout
        self.cancelCount = config.choose_timeout
        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setGeometry(0, 1080-16, 1920, 16)

    def setImages(self, images):
        for i in range(5):
            img = cv2.resize(images[i], self.size)
            self.labels[i].setPixmap(toQPixmap(img))
        self.timer.start(1000)

    def makeChoice0(self, event):
        self.timer.stop()
        self.chosen.emit(0)

    def makeChoice1(self, event):
        self.timer.stop()
        self.chosen.emit(1)

    def makeChoice2(self, event):
        self.timer.stop()
        self.chosen.emit(2)

    def makeChoice3(self, event):
        self.timer.stop()
        self.chosen.emit(3)

    def makeChoice4(self, event):
        self.timer.stop()
        self.chosen.emit(4)

    def makeChoice5(self, event):
        self.timer.stop()
        self.chosen.emit(-1)

    def timeoutTick(self):
        self.cancelCount -= 1
        if self.cancelCount <= 0:
            self.timer.stop()
            self.chosen.emit(-1)
            return
        v = (self.cancelMax - self.cancelCount) * 100 / self.cancelMax
        self.progress.setValue(v)
