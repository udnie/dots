import sys

from PyQt5.QtCore    import Qt, QPoint
from PyQt5.QtGui     import QPainter, QColor, QPen, QFont, QFontMetrics, QBrush
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDesktopWidget

ExitKeys = (Qt.Key_X, Qt.Key_Q, Qt.Key_Escape)
SizeKeys = (Qt.Key_Less, Qt.Key_Greater)
Ticks = (100,50,10)

ctrWidth, ctrHeight = 600, 70

### ------------------------- vhx --------------------------
class VHX(QMainWindow):  ## yet another screen pixel ruler 
### --------------------------------------------------------
    def __init__(self):
        super().__init__()

        self.resize(ctrWidth, ctrHeight)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True);
     
        self.setWindowFlags(  ## my birthday present from stackoverflow
            Qt.Window | \
            Qt.CustomizeWindowHint | \
            Qt.WindowStaysOnTopHint
        )

        self.widget = QWidget(self)
        self.widget.setFocusPolicy(Qt.StrongFocus)
        self.widget.setFocus()
       
        self.setCentralWidget(self.widget);
        self.initXY = self.pos()

        self.horizontal = True 
        self.center()
        self.scrnWidth, self.scrnHeight = getScreenSize()
  
        self.grabMouse()

        self.show()

### --------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(128, 255, 0, 175)) 
        painter.drawRect(0, 0, self.width(), self.height() )
        painter.setBrush(Qt.NoBrush) 
        painter.setPen(QPen(Qt.darkGray, .5)) 
        painter.drawRect(0, 0, self.width(), self.height())
        painter.setPen(QPen(Qt.black, 1.0)) 
        metrics = QFontMetrics(QFont('Arial', 13))
        if self.horizontal:
            self.drawHorizontalLines(painter, metrics)  
        else:
            self.drawVerticalLines(painter, metrics)  

    def drawHorizontalLines(self, painter, metrics): 
        for t in Ticks:
            w = int(self.width() / t) 
            for i in range (1, w+1):
                i = i * t
                txt = str(i)
                p = metrics.width(txt) + 5
                if t > 10:
                    painter.drawLine(i, 20, i, ctrHeight)
                    painter.drawText(i-p, 15, txt)
                else:  ## just draw lines
                    painter.drawLine(i, 35, i, ctrHeight)

    def drawVerticalLines(self, painter, metrics):  
        for t in Ticks:  
            w = self.width()-10
            h = int(self.height() / t) 
            for i in range (1, h+1):
                i = i * t
                txt = str(i)
                p = metrics.width(txt)
                if t > 10:
                    painter.drawLine(5, i, w, i)
                    painter.drawText(w-p, i-3, txt)
                else:
                    painter.drawLine(5, i, w-25, i)
       
    def keyPressEvent(self, e):
        key = e.key()
        if key == Qt.Key_V:
            self.horizontal = False
            self.resize(70,600)
            self.center()
        elif key == Qt.Key_H:
            self.horizontal = True
            self.resize(600,70)
            self.center()
        elif key in SizeKeys:
            self.scaleThis(key)
        elif key in ExitKeys:
            self.close()

    def mousePressEvent(self, e):
        self.initXY = e.globalPos()
        e.accept()

    def mouseMoveEvent(self, e):
        delta = QPoint(e.globalPos() - self.initXY)
        x = self.x() + delta.x()
        y = self.y() + delta.y()
        ## leave some pixels on the screen -- 200px 
        if self.horizontal:
            x = constrain(x, self.width(), self.scrnWidth, 200)
        else:
            y = constrain(y, self.height(), self.scrnHeight, 200)
        ## so it doesn't get lost and go off screen
        if self.horizontal:
            if y >= self.scrnHeight - ctrHeight/2:
                y = int(self.scrnHeight - ctrHeight/2)
        else:
            if x >= self.scrnWidth - self.width()/2:
                x = int(self.scrnWidth - self.width()/2)
            elif x <= self.width()/2:
                x = int(self.width()/2)
        self.move(x,y)
        self.initXY = e.globalPos()
        e.accept()

    def mouseDoubleClickEvent(self, e):
        self.close()
    
    def scaleThis(self, key):
        if key == Qt.Key_Greater:
            scale = 100
        else:
            scale = -100
        if self.horizontal and (self.width() + scale) > 100: 
            self.resize(self.width() + scale, self.height())
        elif self.height() + scale > 100:
            self.resize(self.width(), self.height() + scale)
        self.update()

    def center(self):
        ctr = QDesktopWidget().availableGeometry().center()
        if self.horizontal:
            x = int(((ctr.x() * 2 ) - ctrWidth)/2)
            self.move(x, ctr.y()-100)
        else:
            y = int((((ctr.y() * 2 ) - ctrWidth)/2))
            x = int(ctr.x()-self.width()/2)
            self.move(x, y-50)

def getScreenSize():
    d = QDesktopWidget().availableGeometry()
    return d.x() + d.width(), d.y() + d.height()

def constrain(xy, objSize, screenSize, px):
    if xy >= screenSize - px:    ## chk right
        return int(screenSize - px)  
    elif xy <= -(objSize - px):  ## chk left
        return int(-(objSize - px))
    else:
        return int(xy)

### --------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    vhx = VHX()
    sys.exit(app.exec_())

### ------------------------- vhx --------------------------
