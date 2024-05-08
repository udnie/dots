
import sys

from PyQt6.QtCore       import Qt, QPointF
from PyQt6.QtGui        import QGuiApplication, QPainter, QColor, QPen, QFontMetrics, QFont
from PyQt6.QtWidgets    import QApplication, QWidget

ExitKeys = (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape)
SizeKeys = (Qt.Key.Key_Less, Qt.Key.Key_Greater)  ## '</>'
Ticks    = (100,50,10)  ## how often to draw a line and size

VWidth, VHeight, BHeight = 1200, 70, 900  

# from PyQt6.QtCore import QT_VERSION_STR
# from PyQt6.QtCore import PYQT_VERSION_STR

# print("PyQt version:", PYQT_VERSION_STR) 
# print("Python version:", QT_VERSION_STR)

### ------------------------- vhx --------------------------
class VHX(QWidget):  ## yet another screen pixel ruler 
### --------------------------------------------------------
    def __init__(self):
        super().__init__()

        self.resize(VWidth, VHeight)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setWindowOpacity(.80)

        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.FramelessWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)

        self.type = 'widget'
        self.setAccessibleName('widget')

        self.widget = QWidget(self)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        
        self.initXY = self.pos()
        self.horizontal = True 
        
        self.center()
        self.scrnWidth, self.scrnHeight = getScreenSize()
  
        self.font = QFont()
        self.font.setFamily("Helvetica")
        self.font.setPointSize(13)
                
        self.show()

### --------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        if self.horizontal:  ## need to keep one component constant
            self.resize(self.width(), VHeight)  ## fixes a small bug 
        else:                
            self.resize(VHeight, self.height() )
        painter.setBrush(QColor(128, 255, 0)) 
        painter.drawRect(0, 0, self.width(), self.height() )
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        painter.setPen(QPen(Qt.GlobalColor.darkGray, .5)) 
        painter.drawRect(0, 0, self.width(), self.height())
        painter.setPen(QPen(Qt.GlobalColor.black, 1.0)) 
        metrics = QFontMetrics(self.font)
        if self.horizontal:
            self.drawHorizontalLines(painter, metrics)  
        else:
            self.drawVerticalLines(painter, metrics)  

    def drawHorizontalLines(self, painter, metrics): 
        for t in Ticks:  ## start at 100
            w = int(self.width() / t) 
            for i in range (1, w+1):
                i = i * t
                txt = str(i)
                p = metrics.boundingRect(txt)
                p = p.width()
                if t > 10:
                    painter.drawLine(i, 20, i, VHeight)
                    if i == w * t: p = p + 4
                    painter.drawText(i-p, 15, txt)
                else:  ## just draw lines
                    painter.drawLine(i, 35, i, VHeight)

    def drawVerticalLines(self, painter, metrics):  
        for t in Ticks:  
            w = self.width()-10
            h = int(self.height() / t) 
            for i in range (1, h+1):
                i = i * t
                txt = str(i)
                p = metrics.boundingRect(txt)
                p = p.width() - 2
                if t > 10:
                    painter.drawLine(5, i, w + 2, i)
                    painter.drawText(w-p, i-3, txt)
                else:
                    painter.drawLine(5, i, w-29, i)
       
    def keyPressEvent(self, e):
        key = e.key()
        if key == Qt.Key.Key_V:
            self.horizontal = False
            self.resize(VHeight, BHeight)
            self.center()
        elif key == Qt.Key.Key_H:
            self.horizontal = True
            self.resize(VWidth, VHeight)
            self.center()
        elif key in SizeKeys:
            self.scaleThis(key)
        elif key in ExitKeys:
            self.close()
                
    def mousePressEvent(self, e):
        self.initXY = e.globalPosition()
        e.accept()

    def mouseMoveEvent(self, e):
        delta = QPointF(e.globalPosition() - self.initXY)
        x = self.x() + delta.x()
        y = self.y() + delta.y()
        ## leave some pixels on the screen -- 200px 
        if self.horizontal:
            x = constrain(x, self.width(), self.scrnWidth, 200)
        else:
            y = constrain(y, self.height(), self.scrnHeight, 200)
        ## so it doesn't get lost and go off screen
        if self.horizontal:
            if y >= self.scrnHeight - VHeight/2:
                y = int(self.scrnHeight - VHeight/2)
        else:
            if x >= self.scrnWidth - self.width()/2:
                x = int(self.scrnWidth - self.width()/2)
            elif x <= self.width()/2:
                x = int(self.width()/2)
        self.move(int(x),int(y))
        self.initXY = e.globalPosition()
        e.accept()

    def mouseDoubleClickEvent(self, e):
        self.close()  
    
    def scaleThis(self, key):
        if key == Qt.Key.Key_Greater:
            scale = 100
        else:
            scale = -100
        p = self.pos()
        x, y = p.x(), p.y()
        if self.horizontal and (self.width() + scale) > 100: 
            self.resize(self.width() + scale, self.height())
            if scale == 100:
                x -= 50         
            else:
                x += 50         
        elif self.height() + scale > 100:
            self.resize(self.width(), self.height() + scale)
            if scale == 100:
                y -= 50         
            else:
                y += 50  
        self.move(x,y)
        self.update()

    def center(self):
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        if self.horizontal:
            x = int(((ctr.x() * 2 ) - VWidth)/2)
            self.move(x, ctr.y()-100)
        else:
            y = int((((ctr.y() * 2 ) - BHeight)/2))
            x = int(ctr.x()-self.width()/2)
            self.move(x, y-50)

def getScreenSize():
    d = QGuiApplication.primaryScreen().availableGeometry()
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
    sys.exit(app.exec())

### ------------------------- vhx --------------------------
