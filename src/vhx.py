
import sys

from PyQt6.QtCore       import Qt, QPointF
from PyQt6.QtGui        import QGuiApplication, QPainter, QColor, QPen, QFontMetrics, QFont
from PyQt6.QtWidgets    import QApplication, QWidget

Ticks = (100,50,10)  ## how often to draw a line and size
RWidth, RSize, RHeight = 1500, 70, 1000  

### ------------------------- vhx --------------------------
''' Pressing the 'command' key, on my mac, and one of the square 
    brackets anchors the rulers current 'x' position if horizontal 
    or its current 'y' position if vertical ''' 
### --------------------------------------------------------
class VHX(QWidget):  ## yet another screen pixel ruler 
### --------------------------------------------------------
    def __init__(self):
        super().__init__()

        self.resize(RWidth, RSize)
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
        self.resize(self.width(), RSize) if self.horizontal else\
            self.resize(RSize, self.height() )
        painter.setBrush(QColor(128, 255, 0)) 
        painter.drawRect(0, 0, self.width(), self.height() )
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        painter.setPen(QPen(Qt.GlobalColor.darkGray, .5)) 
        painter.drawRect(0, 0, self.width(), self.height())
        painter.setPen(QPen(Qt.GlobalColor.black, 1.0)) 
        metrics = QFontMetrics(self.font)
        self.drawHorizontalLines(painter, metrics) if self.horizontal else\
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
                    painter.drawLine(i, 20, i, RSize)
                    if i == w * t: p = p + 4
                    painter.drawText(i-p, 15, txt)
                else:  ## just draw lines
                    painter.drawLine(i, 35, i, RSize)

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
        mod = e.modifiers()   
        if key == Qt.Key.Key_V:  ## select vertical
            self.horizontal = False
            self.resize(RSize, RHeight)
            self.center()
        elif key == Qt.Key.Key_H: ## select horizontal
            self.horizontal = True
            self.resize(RWidth, RSize)
            self.center()
        elif e.key() in (Qt.Key.Key_BracketRight, Qt.Key.Key_BracketLeft):
            self.scaleThis(key, 1) if mod & Qt.KeyboardModifier.ControlModifier else\
                self.scaleThis(key, 0)  
        elif key in (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape):
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
            if y >= self.scrnHeight - RSize/2:
                y = int(self.scrnHeight - RSize/2)
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
    
    def scaleThis(self, key, switch):     
        if key == Qt.Key.Key_BracketRight:
            scale = 100
        else:
            scale = -100
        p = self.pos();  x, y = p.x(), p.y()
        if self.horizontal and (self.width() + scale) > 100: 
            self.resize(self.width() + scale, self.height())
            if switch != 0:  
                switch = x
            elif scale == 100:
                 x -= 50         
            else:
                x += 50    
        elif self.height() + scale > 100:    
            self.resize(self.width(), self.height() + scale)
            if switch != 0:  
                switch = y
            elif scale == 100:
                 y -= 50         
            else:
                 y += 50  
        self.move(x,y)
        self.update()

    def center(self):
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        if self.horizontal:
            x = int(((ctr.x() * 2 ) - RWidth)/2)
            self.move(x, ctr.y()-100)
        else:
            y = int((((ctr.y() * 2 ) - RHeight)/2))
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

