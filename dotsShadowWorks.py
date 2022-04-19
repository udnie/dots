
import cv2
import numpy as np

from PyQt5.QtCore       import Qt, QPointF, QPoint, QRectF
from PyQt5.QtGui        import QColor, QPen, QPainterPath, QRegion, QTransform, \
                               QPainter
from PyQt5.QtWidgets    import QSlider, QWidget, QGroupBox, QGraphicsPixmapItem, \
                               QLabel, QSlider, QHBoxLayout,  QVBoxLayout, QPushButton, \
                               QGraphicsEllipseItem, QDial
                               
from dotsShared         import common

PathStr = ["topLeft","topRight","botRight","botLeft"]
V = common["V"]  ## the diameter of a pointItem, same as in ShadowWorks

### ------------------- dotsShadowWorks --------------------
''' classes: pointItem, shadowWidget, shadow, and cv2 functions '''
### --------------------------------------------------------
class PointItem(QGraphicsEllipseItem):
### --------------------------------------------------------
    def __init__(self, pt, ptStr, parent):
        super().__init__()

        self.fab = parent
         
        self.type  = "point"
        self.ptStr = ptStr
        
        self.dragCnt = 0
          
        ## -V*.5 so it's centered on the path 
        self.x = pt.x()-V*.5
        self.y = pt.y()-V*.5
        self.setZValue(50) 
        
        self.setRect(self.x, self.y, V, V)  
        
        self.setPen(QPen(QColor("gray"), 1))
        if self.ptStr in ("topLeft","topRight"):
            self.setBrush(QColor("yellow"))
        else:
            self.setBrush(QColor("lime"))
                        
 ### --------------------------------------------------------
    def mousePressEvent(self, e):  
        e.accept() 
        
    def mouseMoveEvent(self, e):
        self.dragCnt += 1
        if self.dragCnt % 5 == 0:            
            self.moveIt(e.pos()) 
            self.fab.updateShadow()                  
        e.accept()
                       
    def mouseReleaseEvent(self, e):
        self.moveIt(e.pos())
        self.fab.updateShadow()
        e.accept()
                                        
    def moveIt(self, e):     
        pos = self.mapToScene(e)
        x, y = pos.x(), pos.y()
        self.setRect(x-V*.5, y-V*.5, V,V)  ## set current point    
        if self.ptStr == "topLeft":  ## push right
            w, y1 = self.current(0,1)            
            self.fab.path[0] = QPointF(x,y) 
            self.fab.path[1] = QPointF(x+w,y1)
            self.fab.topRight.setRect(x+(w-V*.5), y1-V*.5, V,V)       
        elif self.ptStr == "botLeft":    
            w, y1 = self.current(3,2)            
            self.fab.path[3] = QPointF(x,y) 
            self.fab.path[2] = QPointF(x+w,y1)
            self.fab.botRight.setRect(x+(w-V*.5), y1-V*.5, V,V)          
        else:  
            i = PathStr.index(self.ptStr)  ## move only 
            self.fab.path[i] = QPointF(x,y)                  
        
    def current(self,a,b):
        l = self.fab.path[a].x()
        r = self.fab.path[b].x()
        return r - l,  self.fab.path[b].y()

### --------------------------------------------------------        
class ShadowWidget(QWidget): 
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()
                                        
        self.fab = parent
        
        self.type = 'widget'
        self.save = QPoint(0,0)
                
        self.setAccessibleName('widget')
                
        hbox = QHBoxLayout()
        hbox.addWidget(self.sliderGroup())
        hbox.addSpacing(5) 
        hbox.addWidget(self.buttonGroup())
        self.setLayout(hbox)
        
        self.setFixedHeight(int(self.fab.WidgetH))
        self.setStyleSheet("background-color: rgb(230,230,230)")
        self.setContentsMargins(-2,15,-2,-15)
             
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
                                 
        self.show()
                
### --------------------------------------------------------                      
    def resizeEvent(self, e):
        path = QPainterPath()  ## thanks python fixing - that's a web site
        # the rectangle must be translated and adjusted by 1 pixel in order to 
        # correctly map the rounded shape
        rect = QRectF(self.rect()).adjusted(1.5, 1.5, -2.5, -2.5)
        path.addRoundedRect(rect, 5, 5)
        # QRegion is bitmap based, so the returned QPolygonF (which uses float
        # values must be transformed to an integer based QPolygon
        region = QRegion(path.toFillPolygon(QTransform()).toPolygon())
        self.setMask(region) 
        
    def paintEvent(self, e):  ## thanks stack over flow
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)   
        rectPath = QPainterPath()                      
        height = self.height()-5                    
        rectPath.addRoundedRect(QRectF(2, 2, self.width()-5, height), 5, 5)
        painter.setPen(QPen(QColor(0,125,255), 3, Qt.SolidLine, 
                Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor(0,150,245, 235))
        painter.drawPath(rectPath)
              
    def mousePressEvent(self, e):
        self.save = e.globalPos()
        e.accept()

    def mouseMoveEvent(self, e):
        self.moveThis(e)
        e.accept()
        
    def mouseReleaseEvent(self, e):
        self.moveThis(e)
        e.accept()
                      
    def moveThis(self, e):
        dif = QPoint(e.globalPos() - self.save)
        self.move(self.pos() + dif) 
        self.save = e.globalPos()
        
    def mouseDoubleClickEvent(self, e):
        self.fab.closeWidget()
        e.accept()
        
### -------------------------------------------------------- 
    def sliderGroup(self):
        groupBox = QGroupBox("Rotate     Scale   Opacity   ")
        
        groupBox.setFixedWidth(170)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        groupBox.setStyleSheet("background: rgb(245, 245, 245)")
   
        self.rotateValue = QLabel("0", alignment=Qt.AlignCenter)
        self.rotaryDial = QDial()
        self.rotaryDial.setMinimum(0)
        self.rotaryDial.setMaximum(360)
        self.rotaryDial.setValue(0)
        self.rotaryDial.setFixedWidth(60)
        self.rotaryDial.setWrapping(False)
        self.rotaryDial.setNotchesVisible(True)
        self.rotaryDial.setNotchTarget(15.0)
        self.rotaryDial.valueChanged.connect(self.Rotate)
    
        self.scaleValue = QLabel("1.00")
        self.scaleSlider = QSlider(Qt.Orientation.Vertical,                   
            minimum=50, maximum=200, singleStep=1, value=100)
        self.scaleSlider.setFocusPolicy(Qt.StrongFocus)
        self.scaleSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.scaleSlider.setTickInterval(25)  
        self.scaleSlider.valueChanged.connect(self.Scale)   
        
        self.opacityValue = QLabel(".50")
        self.opacitySlider = QSlider(Qt.Orientation.Vertical,                   
            minimum=0, maximum=100, singleStep=1, value=50)
        self.opacitySlider.setFocusPolicy(Qt.StrongFocus)
        self.opacitySlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.opacitySlider.setTickInterval(16)  
        self.opacitySlider.valueChanged.connect(self.Opacity)
                  
        sbox = QHBoxLayout()  ## sliders  
        sbox.addSpacing(-10)    
        sbox.addWidget(self.rotaryDial)  
        sbox.addSpacing(10)       
        sbox.addWidget(self.scaleSlider) 
        sbox.addSpacing(10)                
        sbox.addWidget(self.opacitySlider) 
        
        vabox = QHBoxLayout()  ## values
        vabox.addSpacing(0) 
        vabox.addWidget(self.rotateValue)        
        vabox.addSpacing(0) 
        vabox.addWidget(self.scaleValue)     
        vabox.addSpacing(0) 
        vabox.addWidget(self.opacityValue)  
        vabox.setAlignment(Qt.AlignmentFlag.AlignBottom)
         
        vbox = QVBoxLayout()  
        vbox.addLayout(sbox)
        vbox.addLayout(vabox)
        
        groupBox.setLayout(vbox)
        return groupBox

    def buttonGroup(self):
        groupBox = QGroupBox("Feeling Lucky?")
        
        groupBox.setFixedWidth(100)
        groupBox.setStyleSheet("background: rgb(245, 245, 245)")
                     
        hideBtn = QPushButton("Hide")
        flipBtn  = QPushButton("Flip")
        newBtn  = QPushButton("New")
        delBtn  = QPushButton("Delete")
        quitBtn = QPushButton("Close")
    
        hideBtn.clicked.connect(self.fab.hideAll)
        flipBtn.clicked.connect(self.fab.flip)
        newBtn.clicked.connect(self.fab.newShadow)
        delBtn.clicked.connect(self.fab.deleteShadow)
        quitBtn.clicked.connect(self.fab.closeWidget)
    
        hbox = QVBoxLayout(self)
        hbox.addWidget(hideBtn)
        hbox.addWidget(flipBtn)
        hbox.addWidget(newBtn)
        hbox.addWidget(delBtn)
        hbox.addWidget(quitBtn)
                
        groupBox.setLayout(hbox)
        return groupBox
    
    def Rotate(self, val):
        self.fab.rotateShadow(val)
        self.rotateValue.setText("{:3d}".format(val))
        ## setting rotate in shadowMaker
  
    def Scale(self, val):
        op = (val/100)
        self.fab.scaleShadow(op)
        self.scaleValue.setText("{0:.2f}".format(op))
        ## setting rotate in shadowMaker
        
    def Opacity(self, val):
        op = (val/100)
        self.fab.shadow.setOpacity(op)
        self.fab.alpha = op
        self.opacityValue.setText("{0:.2f}".format(op)) 
                                                                                                                                                                              
### --------------------------------------------------------
class Shadow(QGraphicsPixmapItem): 
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
       
        self.fab = parent
       
        self.type = "shadow" 
        self.anime = None 
        self.setZValue(self.fab.pixitem.zValue()-1) 
                                       
        self.dragCnt = 0
        self.save    = QPointF(0.0,0.0)
        self.skip    = False
                           
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True)
          
### --------------------------------------------------------
    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            pen = QPen(QColor("lime"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def mousePressEvent(self, e): 
        self.save = self.mapToScene(e.pos())    
        self.fab.addPoints()  
        if e.button() == Qt.MouseButton.RightButton:
            self.skip = True      
            self.fab.addWidget()
        e.accept() 
        
    def mouseMoveEvent(self, e):
        self.dragCnt += 1
        if self.dragCnt % 5 == 0:                     
            self.updatePath(self.mapToScene(e.pos()))  
            self.fab.updateOutline()
        e.accept()
                       
    def mouseReleaseEvent(self, e): 
        self.updatePath(self.mapToScene(e.pos())) 
        if self.skip:
            self.skip = False  ## skip updating shadow as ran widget 
        else: 
            self.fab.updateOutline()
            self.fab.updateShadow()  ## cuts off shadow at 0.0y of scene if not moving
        e.accept()
                     
    def updatePath(self, val):   
        dif = val - self.save
        self.setPos(self.pos()+dif)         
        for i in range(4):  
            self.fab.path[i] = self.fab.path[i] + dif
            self.fab.updatePoints(i, self.fab.path[i].x(), self.fab.path[i].y())
        self.save = val
                       
### --------------------------------------------------------      
    def initPoints(self):  ## initial path and points setting       
        self.fab.path = []
        self.fab.outline = None
        
        b = self.boundingRect()  
        p = self.pos() 
        
        self.fab.path.append(p)  
        self.fab.path.append(QPointF(p.x() + b.width(), p.y()))  
        self.fab.path.append(QPointF(p.x() + b.width(), p.y() + b.height()))         
        self.fab.path.append(QPointF(p.x(), p.y() + b.height()))
      
        self.fab.updateOutline()  
        self.fab.addPoints()                                                                                                                                                                                                                                         

    def deleteShadow(self):
        self.fab.deleteShadow()
                                                                                 
### --------------------------------------------------------        
def initShadow(file, w, h, flop):  ## replace all colors with grey    
    img = cv2.imread(file, cv2.IMREAD_UNCHANGED)   
    if flop: img = cv2.flip(img, 1)  ## works after the read   
    rows, cols, _ = img.shape

    wuf = img.copy()  
    for i in range(rows):
        for j in range(cols):
            pixel = img[i,j]
            if pixel[-1] != 0:  ## not transparent      
                wuf[i,j] = (20,20,20,255)
                                           
    img = cv2.resize(np.array(wuf), (int(w), int(h)), interpolation = cv2.INTER_CUBIC)
    img = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT)
                                
    height, width, ch = img.shape
    bytesPerLine = ch * width  ## 4 bits of information -- alpha channel 
    
    return img, width, height, bytesPerLine

### --------------------------------------------------------          
def setPerspective(path, w, h, cpy, viewW, viewH):  ## update gray copy based on path xy's         
    p = []                      
    for i in range(4):  ## make cv2 happy - get current location of points from path
        x,y = int(path[i].x()), int(path[i].y()) 
        p.append([x,y])
            
    dst = np.float32([p[0], p[1], p[3], p[2]])        
    src = np.float32([[0,0], [w,0], [0, h], [w,h]])
        
    M = cv2.getPerspectiveTransform(src, dst)  ## compute the Matrix
    img = cv2.warpPerspective(cpy, M, (viewW, viewH))

    height, width, ch = img.shape
    bytesPerLine = ch * width  ## 4 bits of information
        
    img = cv2.resize(img, (width, height), interpolation = cv2.INTER_CUBIC)  ## helps smooth out edges
    img = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT)    
    
    return img, width, height, bytesPerLine    
                                                                                                            
### ------------------- dotsShadowWorks --------------------

