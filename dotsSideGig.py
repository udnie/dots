import random
import os
import math

from os import path

from PyQt5.QtCore    import Qt, QTimer, QPointF, QRectF,QSize
from PyQt5.QtGui     import QCursor, QPixmap, QPainter, QBrush, QFontMetrics, \
                            QPen, QPolygonF, QColor, QFont
from PyQt5.QtWidgets import QWidget, QMessageBox, QGraphicsSimpleTextItem, \
                            QLabel, QDesktopWidget, \
                            QGraphicsItemGroup, QGraphicsLineItem, QScrollArea, \
                            QGridLayout, QVBoxLayout, QGraphicsEllipseItem

from dotsShared      import common, paths, pathcolors

PlayKeys = ('resume','pause')

### ---------------------- dotsSideGig ---------------------
''' dotsSideGigs: DoodleMaker, Pointitem, Doodle, TagIt, and 
    MsgBox. '''
### --------------------------------------------------------
class PointItem(QGraphicsEllipseItem):
    
    def __init__(self, parent, pt, idx):
        super().__init__()

        self.pathMaker = parent
      
        self.pt = pt
        self.idx = idx

        self.setZValue(idx) 
        self.type = 'pt'
     
        v = 6  ## so its centered
        self.setRect(pt.x()-v*.5, pt.y()-v*.5, v, v)
        self.setBrush(QColor("white"))

        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, False)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, False)
          
        self.setAcceptHoverEvents(True)

 ### --------------------------------------------------------
    def hoverEnterEvent(self, e):
        if self.pathMaker.pathSet:
            self.pathMaker.addPointTag(self)   
   
    def hoverLeaveEvent(self, e):
        if self.pathMaker.pathSet:
            self.pathMaker.removePointTag() 

    def mousePressEvent(self, e):    
        if self.pathMaker.key not in ('del','opt'):   
            return
        self.pathMaker.removePointTag()
        if self.pathMaker.key == 'del':  
            self.pathMaker.delPointItem(self)
        elif self.pathMaker.key == 'opt': 
            self.pathMaker.insertPointItem(self)
        self.pathMaker.key = ''
        e.accept()
        
### --------------------------------------------------------
class MsgBox(QMessageBox):  ## thanks stackoverflow

    def __init__(self, text, pause=2):
        super().__init__()

        self.timeOut = pause
        self.setText("\n" + text)
        self.setStandardButtons(QMessageBox.NoButton)
       
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

        self.exec_()

    def enterEvent(self, e):  
        self.close()

    def changeContent(self):
        self.timeOut -= 1
        if self.timeOut <= 0:
            self.close()

    def closeEvent(self, e):
        self.timer.stop()
        e.accept() 

### --------------------------------------------------------
class TagIt(QGraphicsSimpleTextItem):
    
    def __init__(self, control, tag, color, zval=None):
        super().__init__()

        if control in PlayKeys and "Random" in tag:
            tag = tag[7:]
            self.color = QColor(0,255,127)
        elif control == 'pathMaker':
            if " 0.00%" in tag:
                color = QColor("LIGHTSEAGREEN")
            if len(tag.strip()) > 0: self.color = QColor(color)
        elif control == 'points':
            self.color = QColor(color)
        else:
            self.color = QColor(255,165,0)
            if "Random" in tag: tag = tag[0:6] 
        if color:
            self.color = QColor(color)

        if zval != None:
            if len(tag) > 0:  
                tag = tag + ": " + str(zval)
            else:
                tag =  str(zval)
    
        if control == 'points':
            self.type = 'pt'
        else:
            self.type = 'tag'

        self.text = tag   
        self.font = QFont('Arial', 12)
        metrics   = QFontMetrics(self.font)
        self.rect = QRectF(0, 0, metrics.width(self.text)+13, 19)
        self.waypt = 0

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget): 
        brush = QBrush()
        brush.setColor(self.color)
        brush.setStyle(Qt.SolidPattern)

        painter.fillRect(self.boundingRect(), brush)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(Qt.black)
        painter.setFont(self.font)
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self.text)
 
### --------------------------------------------------------
class DoodleMaker(QWidget): 

    def __init__(self, parent):
        super().__init__()

        self.pathMaker = parent
        self.sideWays  = self.pathMaker.sideWays

        self.resize(530,320)

        widget = QWidget()
        gLayout = QGridLayout(widget)
        gLayout.setDefaultPositioning(3, Qt.Horizontal)
        gLayout.setHorizontalSpacing(5)
        gLayout.setOriginCorner(0)
        gLayout.setContentsMargins(0, 0, 0, 0)

        for file in getPathList():    
            df = Doddle(parent, file)
            gLayout.addWidget(df)

        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(False)
        scroll.setWidget(widget)
   
        vLayout = QVBoxLayout(self)
        vLayout.addWidget(scroll)

### --------------------------------------------------------
class Doddle(QLabel):  

    def __init__(self, parent, file):
        super().__init__()

        self.pathMaker = parent
        self.sideWays  = self.pathMaker.sideWays
   
        self.file = file
        scalor = .10
        self.W, self.H = 150, 100

        self.font = QFont('Arial', 13)
        self.pen = QPen(QColor(0,0,0))                     
        self.pen.setWidth(1)                                       
        self.brush = QBrush(QColor(255,255,255,255)) 
        ## scale down screen drawing --  file, scalor, offset
        self.df = getPts(self.file, scalor, 10)  
  
    def minimumSizeHint(self):
        return QSize(self.W, self.H)

    def sizeHint(self):
        return self.minimumSizeHint()

    def mousePressEvent(self, e): 
        self.pathMaker.pts = getPts(self.file)
        self.pathMaker.addPath()
        self.pathMaker.openPathFile = os.path.basename(self.file)
        self.pathMaker.pathChooserOff() 
        e.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(self.brush) 
        painter.setPen(QPen(QColor("DODGERBLUE"), 2, Qt.DashDotLine))
        painter.drawPolygon(QPolygonF(self.df))
        painter.setBrush(Qt.NoBrush) 
        painter.setPen(QPen(Qt.darkGray, 2)) 
        painter.drawRect(0, 0, self.W, self.H)
        painter.setPen(QPen(Qt.black, 2)) 
        metrics = QFontMetrics(self.font)
        txt = os.path.basename(self.file)
        p = int((self.W - metrics.width(txt))/2 )
        painter.drawText(p, self.H-10, txt)

### --------------------------------------------------------
def distance(x1, x2, y1, y2):
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt((dx * dx ) + (dy * dy))

def getPathList(bool=False):  ## used by DoodleMaker
    try:                            ## also by context menu
        files = os.listdir(paths['paths'])
    except IOError:
        MsgBox("getPathList: No Path Directory Found!", 5)
        return None  
    filenames = []
    for file in files:
        if file.lower().endswith('path'): 
            if bool:    
                file = os.path.basename(file)  ## short list
                filenames.append(file)
            else:
                filenames.append(paths['paths'] + file)
    if not filenames:
        MsgBox("getPathList: No Paths Found!", 5)
    return filenames

def getPts(file, scalor=1.0, inc=0):  ## also used by pathChooser
    try:
        tmp = []
        with open(file, 'r') as fp: 
            for line in fp:
                ln = line.rstrip()  
                ln = list(map(float, ln.split(',')))   
                tmp.append(QPointF(ln[0]*scalor+inc, ln[1]*scalor+inc))
        return tmp
    except IOError:
        MsgBox("getPts: Error reading pts file")

def getColorStr():  
    random.seed()
    p = pathcolors
    return p[random.randint(0,len(p)-1)]

### --------------------- dotsSideGig ----------------------

