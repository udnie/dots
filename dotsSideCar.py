import random
import os

from os import path

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsShared      import common, paths
from dotsPixItem     import PixItem

### ---------------------- dotsSideCar ---------------------
''' dotsSideCar: PointItem, DoodleMaker, Doodle, and Tagit classes 
    used by pathmaker and sideWays also pixTest, transFormPixitem, 
    toggleGrid and MsgBox plus some small functions '''
### --------------------------------------------------------
class SideCar():

    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.scene  = parent.scene
        self.mapper = parent.mapper   
        
        self.gridZ   = common["gridZ"] 
        self.gridSet = False
        self.gridGroup = None

### --------------------------------------------------------
    def pixTest(self):
        if not self.canvas.pathMakerOn:
            self.canvas.pixCount = self.mapper.toFront(0.0)  
            for _ in range(10):
                self.canvas.pixCount += 1
                pix = PixItem(paths["spritePath"] + 'apple.png',
                        self.canvas.pixCount,
                        0, 0, 
                        self.canvas)
                x = int(constrain(
                        self.xy(common["viewW"]),
                        pix.width, 
                        common["viewW"], 
                        pix.width * -common["factor"]))
                y = int(constrain(
                        self.xy(common["viewH"]),
                        pix.height, 
                        common["viewH"],
                        pix.height * -common["factor"]))
                pix.x, pix.y = x, y
                pix.setPos(x,y)
                rotation = random.randrange(-5, 5) * 5
                scale = random.randrange(95, 105)/100.0
                self.transFormPixItem(pix, rotation, scale)
         
    def transFormPixItem(self, pix, rotation, scale):
        op = QPointF(pix.width/2, pix.height/2)
        pix.setTransformationMode(Qt.SmoothTransformation)
        pix.setTransformOriginPoint(op)
        pix.scale, pix.rotation = scale, rotation
        pix.setScale(scale)
        pix.setRotation(rotation)
        self.scene.addItem(pix)
  
    def xy(self, max):
        return random.randrange(-40, max+40)

### --------------------------------------------------------
    def toggleGrid(self):
        if self.gridSet:
            self.scene.removeItem(self.gridGroup)
            self.gridSet = False
        else: 
            self.gridGroup = QGraphicsItemGroup()  
            self.gridGroup.setZValue(common["gridZ"])
            self.scene.addItem(self.gridGroup)
            self.gridSet = True

            gs = common["gridSize"]
            pen = QPen(QColor(0,0,255))

            for i in range(int(common["viewH"]/gs)):
                self.addLines(QGraphicsLineItem(0.0, gs*i,
                    float(common["viewW"]), gs*i), pen)
            for j in range(int(common["viewW"]/gs)):
                self.addLines(QGraphicsLineItem(gs*j, 0.0,
                    gs*j, float(common["viewH"])), pen)
        
    def addLines(self, line, pen):
        line.type = 'grid'
        line.setPen(pen)
        line.setOpacity(common["factor"])
        line.setZValue(common["gridZ"])
        line.setFlag(QGraphicsLineItem.ItemIsMovable, False)
        self.gridGroup.addToGroup(line)

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

    def closeEvent(self, event):
        self.timer.stop()
        event.accept() 

### --------------------------------------------------------
def mirrorSet(self, mirror):
    self.flopped = mirror   
    self.setPixmap(QPixmap.fromImage(
        self.imgFile.mirrored(
        horizontal=self.flopped,
        vertical=False)))
    self.setTransformationMode(Qt.SmoothTransformation)

def constrain(lastXY, objSize, panelSize, overlap):
    if lastXY + objSize > panelSize - overlap:
        return panelSize - (objSize + overlap)
    elif lastXY < overlap:
        return overlap
    else:
        return lastXY

def setCursor():
    cur = QCursor()
    cur.setPos(QDesktopWidget().availableGeometry().center())

### --------------------------------------------------------
class TagIt(QGraphicsSimpleTextItem):
    
    def __init__(self, control, tag, color):
        super().__init__()

        if control in ['pause','resume'] and "Random" in tag:
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

        self.type = 'tag'
        self.text = tag   
        self.font = QFont('Modern', 12)
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
class PointItem(QGraphicsEllipseItem):
    
    def __init__(self, parent, pt, idx):
        super().__init__()

        self.sideWays = parent
        self.pathMaker = parent.pathMaker

        self.pt = pt
        self.idx = idx

        self.last = QPointF(0,0)
        self.type = 'pt'
        self.set = False

        v = 6  ## so its centered
        self.setRect(pt.x()-v*.5, pt.y()-v*.5, v, v)

        self.setBrush(QColor("white"))
        self.setZValue(self.sideWays.tagZ) 
           
        self.setAcceptHoverEvents(True)

### --------------------------------------------------------
    def hoverEnterEvent(self, e):
        pct = (self.idx/len(self.pathMaker.pts))*100
        s = self.sideWays.makePtsTag(self.pt, self.idx, pct)
        self.sideWays.addPtsTag(s, self.pt)
        self.set = True

    def hoverLeaveEvent(self, e):
        self.removeTag() 

    def mousePressEvent(self, e):    
        if self.pathMaker.key not in ('del','opt'):   
            return
        self.removeTag()
        if self.pathMaker.key == 'del':  # delete
            self.sideWays.deletePointItem(self)
        elif self.pathMaker.key == 'opt': # add one
            self.sideWays.addPointItem(self)
        e.accept()

    def removeTag(self):
        if self.set:
            self.sideWays.removePtsTag() 
        self.set = False
 
### --------------------------------------------------------
class DoodleMaker(QWidget): 

    def __init__(self, parent):
        super().__init__()

        self.resize(490,320)

        widget = QWidget()
        gLayout = QGridLayout(widget)
        gLayout.setDefaultPositioning(3, Qt.Horizontal)
        gLayout.setHorizontalSpacing(5)
        gLayout.setOriginCorner(0)
        gLayout.setContentsMargins(0, 0, 0, 0)

        for file in parent.getPathList(): ## from pathMaker   
            df = Doddle(file, parent)
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

    def __init__(self, file, parent):
        super().__init__()

        self.pathmaker = parent

        self.file = file
        scalor = .10
        self.W, self.H = 140, 100

        self.font = QFont('Modern', 13)
        self.pen = QPen(QColor(0,0,0))                     
        self.pen.setWidth(1)                                       
        self.brush = QBrush(QColor(255,255,255,255)) 
        ## scale down screen drawing --  file, scalor, offset
        self.df = self.pathmaker.getpts(self.file, scalor, 10)  
  
    def minimumSizeHint(self):
        return QSize(self.W, self.H)

    def sizeHint(self):
        return self.minimumSizeHint()

    def mousePressEvent(self, e): 
        self.pathmaker.pts = self.pathmaker.getpts(self.file)
        self.pathmaker.drawPolygon()
        self.pathmaker.openPathFile = os.path.basename(self.file)
        self.pathmaker.pathChooserOff() 

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

### ---------------------- dotsSideCar ---------------------

