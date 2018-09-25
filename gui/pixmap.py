import cv2
import PyQt5.QtGui as QtGui

def toQPixmap(in1):
    src = cv2.cvtColor(in1, cv2.COLOR_BGR2BGRA)
    qimage = QtGui.QImage(src.data, src.shape[1], src.shape[0],
            src.shape[1]*4, QtGui.QImage.Format_ARGB32_Premultiplied)
    pixmap = QtGui.QPixmap.fromImage(qimage)
    return pixmap
