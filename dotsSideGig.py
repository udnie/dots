
import random
import os
import math

from PyQt5.QtCore    import Qt, QTimer, QPointF, QRectF,QSize
from PyQt5.QtGui     import QPainter, QBrush, QFontMetrics, \
                            QPen, QPolygonF, QColor, QFont
from PyQt5.QtWidgets import QWidget, QMessageBox, QGraphicsSimpleTextItem, \
                            QLabel, QScrollArea, QGridLayout, QVBoxLayout

from dotsShared      import paths, pathcolors, PlayKeys

### ---------------------- dotsSideGig ---------------------
''' dotsSideGigs: DoodleMaker, Doodle, TagIt, and MsgBox. '''
### --------------------------------------------------------
class MsgBox(QMessageBox):  ## thanks stackoverflow
### --------------------------------------------------------
    def __init__(self, text, pause=2):
        super().__init__()

        self.timeOut = pause
        self.setText("\n" + text)
        self.setStandardButtons(QMessageBox.StandardButton.NoButton)
       
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

        self.exec()

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
### --------------------------------------------------------   
    def __init__(self, control, tag, color, zval=None):
        super().__init__()
    
        if control == 'paths':
            color = 'lime'
            if "Locked Random" in tag:
                tag = tag[14:] 
            elif "Random" in tag:
                tag = tag[7:]
            n = tag.find('path') + 5
            tag = tag[0:n]
        elif control in PlayKeys and "Random" in tag:
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
            if "Locked Random" in tag:
                tag = tag[0:13] 
            elif "Random" in tag:
                tag = tag[0:6] 
        if color:
            self.color = QColor(color)

        if zval != None and control != 'paths':
            if len(tag) > 0:  
                tag = tag + ": " + str(zval)
            else:
                tag = str(zval)
    
        if control == 'points':
            self.type = 'ptTag'  ## changed from 'pt'
        else:
            self.type = 'tag'

        self.text = tag   

        self.font = QFont()
        self.font.setFamily("Helvetica")
        self.font.setPointSize(12)

        metrics = QFontMetrics(self.font)
        p = metrics.boundingRect(self.text)
        p = p.width()
 
        self.rect = QRectF(0, 0, p+13, 19)
        self.waypt = 0

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget): 
        brush = QBrush()
        brush.setColor(self.color)
        brush.setStyle(Qt.BrushStyle.SolidPattern)

        painter.fillRect(self.boundingRect(), brush)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(self.font)
        painter.drawText(self.boundingRect(), 
            Qt.AlignmentFlag.AlignCenter, self.text)
 
### --------------------------------------------------------
class DoodleMaker(QWidget): 
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.pathMaker = parent
        self.resize(530,320)

        widget = QWidget()
        gLayout = QGridLayout(widget)
        gLayout.setDefaultPositioning(3, Qt.Orientation.Horizontal)
        gLayout.setHorizontalSpacing(5)
        # gLayout.setOriginCorner(0)  ## not sure if this is being used anymore
        gLayout.setContentsMargins(5, 5, 5, 5)

        for file in getPathList():    
            df = Doddle(parent, file)
            gLayout.addWidget(df)

        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(False)
        scroll.setWidget(widget)
   
        vLayout = QVBoxLayout(self)
        vLayout.addWidget(scroll)

### --------------------------------------------------------
class Doddle(QLabel):  
### --------------------------------------------------------
    def __init__(self, parent, file):
        super().__init__()

        self.pathMaker = parent
   
        self.file = file
        scalor = .10
        self.W, self.H = 150, 100

        self.font = QFont()
        self.font.setFamily("Helvetica")
        self.font.setPointSize(12)

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
        painter.setPen(QPen(QColor("DODGERBLUE"), 2, Qt.PenStyle.DashDotLine))
        painter.drawPolygon(QPolygonF(self.df))
        painter.setBrush(Qt.BrushStyle.NoBrush) 
        painter.setPen(QPen(Qt.GlobalColor.darkGray, 2)) 
        painter.drawRect(0, 0, self.W, self.H)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))

        metrics = QFontMetrics(self.font)
        txt = os.path.basename(self.file)
        p = metrics.boundingRect(txt)
        p = p.width()

        p = int((self.W - p)/2 )
        painter.drawText(p, self.H-10, txt)

### --------------------------------------------------------
def getPathList(bool=False):  ## used by DoodleMaker & context menu
    try:                      ## also by 
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
                if len(ln) == 0: continue  ## skip empty lines
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

