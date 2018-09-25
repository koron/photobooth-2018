import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from .pixmap import toQPixmap

class ImageWidget(QtWidgets.QWidget):

    def __init__(self, config, pixmap=None):
        super(ImageWidget, self).__init__()
        self.config = config
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        if self.pixmap is None:
            painter.setPen(QtCore.Qt.black)
            painter.setBrush(QtCore.Qt.black)
            painter.drawRect(0, 0, self.width(), self.height())
            return
        painter.drawPixmap(self.x, self.y, self.w, self.h, self.pixmap)

    def setPixmap(self, pixmap):
        self.pixmap = pixmap
        self.x = 0
        self.y = 0
        self.w = pixmap.width()
        self.h = pixmap.height()
        if self.w < self.config.screen_size[0]:
            self.x = (self.config.screen_size[0] - self.w) / 2
        if self.h < self.config.screen_size[1]:
            self.y = (self.config.screen_size[1] - self.h) / 2
        self.update()

    def setImage(self, image):
        self.setPixmap(toQPixmap(image))
