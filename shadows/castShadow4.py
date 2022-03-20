
import sys
import cv2
import numpy as np
import math

from PyQt5.QtCore    import Qt, QPointF, QPoint, QTimer, QRectF
from PyQt5.QtGui     import QColor, QImage, QPixmap, QFont, QGuiApplication, QPolygonF, QPen, \
                            QPainterPath, QRegion, QTransform, QPainter
from PyQt5.QtWidgets import QSlider, QWidget, QApplication, QGraphicsView,  QGroupBox, \
                            QGraphicsScene, QGraphicsPixmapItem, QLabel, QGraphicsPolygonItem, \
                            QSlider, QHBoxLayout,  QVBoxLayout, QPushButton, \
                            QGraphicsEllipseItem, QFileDialog, QFrame

ExitKeys = (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape)
DispWidth, DispHeight = 900, 600
Width, Height = 950, 710
Btns = 902
Fixed = 250  ## max pixmap size
Xoff, Yoff, Opacity = 0, 0, 50  ## no scale, no rgb
V = 12.0  ## the diameter of a pointItem
PathStr = ["topLeft","topRight","botRight","botLeft"]

### --------------------------------------------------------
class PointItem(QGraphicsEllipseItem):
### --------------------------------------------------------
    def __init__(self, pt, ptStr, parent):
        super().__init__()

        self.shadow = parent
        self.fab    = parent.fab
         
        self.type  = "pt"
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
            self.shadow.path[0] = QPointF(x,y) 
            self.shadow.path[1] = QPointF(x+w,y1)
            self.shadow.topRight.setRect(x+(w-V*.5), y1-V*.5, V,V)       
        elif self.ptStr == "botLeft":    
            w, y1 = self.current(3,2)            
            self.shadow.path[3] = QPointF(x,y) 
            self.shadow.path[2] = QPointF(x+w,y1)
            self.shadow.botRight.setRect(x+(w-V*.5), y1-V*.5, V,V)          
        else:  
            i = PathStr.index(self.ptStr)  ## move only 
            self.shadow.path[i] = QPointF(x,y)                  
        
    def current(self,a,b):
        l = self.shadow.path[a].x()
        r = self.shadow.path[b].x()
        return r - l,  self.shadow.path[b].y()

### --------------------------------------------------------        
class ShadowMenu(QWidget):  ## a true widget
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()
                                        
        self.fab  = parent
        self.save = 0,0
                    
        hbox = QHBoxLayout()
        hbox.addWidget(self.sliderGroup())
        hbox.addSpacing(5) 
        hbox.addWidget(self.buttonGroup())
        self.setLayout(hbox)
        self.setFixedHeight(200)
          
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
                              
        self.show()
                
### --------------------------------------------------------                      
    def resizeEvent(self, e):
        path = QPainterPath()  ## thanks python fixing
        # the rectangle must be translated and adjusted by 1 pixel in order to 
        # correctly map the rounded shape
        rect = QRectF(self.rect()).adjusted(1.5, 1.5, -2.5, -2.5)
        path.addRoundedRect(rect, 5, 5)
        # QRegion is bitmap based, so the returned QPolygonF (which uses float
        # values must be transformed to an integer based QPolygon
        region = QRegion(path.toFillPolygon(QTransform()).toPolygon())
        self.setMask(region) 
        
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)   
        rectPath = QPainterPath()                      
        height = self.height()-5                    
        rectPath.addRoundedRect(QRectF(2, 2, self.width()-5, height), 5, 5)
        painter.setPen(QPen(QColor("DODGERBLUE"), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(QColor("lightgrey"))
        painter.drawPath(rectPath)
              
    def mousePressEvent(self, e):
        self.save = e.globalPos()
        e.accept()

    def mouseMoveEvent(self, e):
        dif = QPoint(e.globalPos() - self.save)
        self.move(self.pos() + dif) 
        self.save = e.globalPos()
        e.accept()

### -------------------------------------------------------- 
    def sliderGroup(self):
        groupBox = QGroupBox("Scale and Opacity")
        groupBox.setFixedWidth(150)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.scaleValue = QLabel("1.00")
        self.scaleSlider = QSlider(Qt.Orientation.Vertical,                   
            minimum=50, maximum=150, singleStep=1, value=100)
        self.scaleSlider.setFocusPolicy(Qt.StrongFocus)
        self.scaleSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.scaleSlider.setTickInterval(10)  
        self.scaleSlider.valueChanged.connect(self.Scale)   
        
        self.opacityValue = QLabel("1.00")
        self.opacitySlider = QSlider(Qt.Orientation.Vertical,                   
            minimum=0, maximum=100, singleStep=1, value=50)
        self.opacitySlider.setFocusPolicy(Qt.StrongFocus)
        self.opacitySlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.opacitySlider.setTickInterval(10)  
        self.opacitySlider.valueChanged.connect(self.Opacity)
                  
        sbox = QHBoxLayout()  ## sliders      
        sbox.addWidget(self.scaleSlider)                  
        sbox.addWidget(self.opacitySlider) 
        
        vabox = QHBoxLayout()  ## values
        vabox.addSpacing(15) 
        vabox.addWidget(self.scaleValue)     
        vabox.addSpacing(15) 
        vabox.addWidget(self.opacityValue)  
        vabox.setAlignment(Qt.AlignmentFlag.AlignBottom)
         
        vbox = QVBoxLayout()  
        vbox.addLayout(sbox)
        vbox.addLayout(vabox)
        
        groupBox.setLayout(vbox)
        return groupBox

    def buttonGroup(self):
        groupBox = QGroupBox("Feel Lucky?")
        groupBox.setFixedWidth(75)
                     
        hideBtn = QPushButton("Hide")
        flipBtn  = QPushButton("Flip")
        newBtn  = QPushButton("New")
        quitBtn = QPushButton("Close")
    
        hideBtn.clicked.connect(self.fab.hideAll)
        flipBtn.clicked.connect(self.fab.flip)
        newBtn.clicked.connect(self.fab.newMenu)
        quitBtn.clicked.connect(self.fab.closeMenu)
    
        hbox = QVBoxLayout(self)
        hbox.addWidget(hideBtn)
        hbox.addWidget(flipBtn)
        hbox.addWidget(newBtn)
        hbox.addWidget(quitBtn)
                
        groupBox.setLayout(hbox)
        return groupBox
                  
    def Opacity(self, val):
        op = (val/100)
        self.fab.shadow.setOpacity(op)
        self.fab.alpha = val
        self.opacityValue.setText("{0:.2f}".format(op)) 
        
    def Scale(self, val):
        op = (val/100)
        self.fab.scaleShadow(val)
        self.scaleValue.setText("{0:.2f}".format(op))
                                                                                                                                                                                  
### --------------------------------------------------------
class Shadows(QGraphicsPixmapItem):  ## handles paths and points
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
       
        self.fab   = parent
        self.scene = parent.scene
        
        self.topLeft  = None
        self.topRight = None
        self.botLeft  = None
        self.botRight = None
       
        self.path = []  ## maintain path per session 
        self.points = []  
                         
        self.type = "shadow"
        self.setZValue(10)   
  
        self.dragCnt = 0
        self.imgSize = 0,0
        self.save = 0,0
                                
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
          
### --------------------------------------------------------
    def mousePressEvent(self, e): 
        self.save = self.mapToScene(e.pos())    
        self.addPoints()
        if e.button() == Qt.RightButton:
            self.fab.addMenu()
        e.accept() 
        
    def mouseMoveEvent(self, e):
        self.dragCnt += 1
        if self.dragCnt % 5 == 0:                     
            self.updatePath(self.mapToScene(e.pos()))  
            self.fab.updateOutline()
        e.accept()
                       
    def mouseReleaseEvent(self, e):
        self.updatePath(self.mapToScene(e.pos())) 
        self.fab.updateOutline()
        self.fab.updateShadow()  ## cuts off at 0.0y of scene if not moving
        e.accept()
          
    def updatePath(self, val):   
        dif = val - self.save
        self.setPos(self.pos()+dif)         
        for i in range(4):  
            self.path[i] = self.path[i] + dif
            self.updatePoints(i, self.path[i].x(), self.path[i].y())
        self.save = val
                       
### --------------------------------------------------------      
    def initPoints(self):  ## initial path and points setting       
        self.path = []
        self.fab.outline = None
        
        b = self.boundingRect()  
        p = self.pos() 
        
        self.path.append(p)  
        self.path.append(QPointF(p.x() + b.width(), p.y()))  
        self.path.append(QPointF(p.x() + b.width(), p.y() + b.height()))         
        self.path.append(QPointF(p.x(), p.y() + b.height()))
      
        self.fab.updateOutline()  
        self.addPoints()
                                                                     
    def addPoints(self):  ## gets called alot
        self.removePoints() 
          
        self.topLeft  = PointItem(self.path[0], "topLeft", self)
        self.topRight = PointItem(self.path[1], "topRight", self)
        self.botRight = PointItem(self.path[2], "botRight", self)
        self.botLeft  = PointItem(self.path[3], "botLeft", self)
        
        self.points = []
        
        self.points.append(self.topLeft)  
        self.points.append(self.topRight)  
        self.points.append(self.botRight )         
        self.points.append(self.botLeft)
        
        for p in self.points:    
            if self.fab.ishidden:
                p.hide()                              
            self.scene.addItem(p)
                                                                                                                                                              
    def updatePoints(self, i, x, y):  ## offset for x,y of ellipse    
        if i == 0:
            self.topLeft.setRect(x-V*.5, y-V*.5, V,V) 
        elif i == 1:      
            self.topRight.setRect(x-V*.5, y-V*.5, V,V)         
        elif i == 3: 
            self.botLeft.setRect(x-V*.5, y-V*.5, V,V) 
        else:                          
            self.botRight.setRect(x-V*.5, y-V*.5, V,V)
            
    def removePoints(self):  ## the path stays
        for p in self.points:  
            self.scene.removeItem(p) 
            
### --------------------------------------------------------                                                   
    def flip(self):          
        self.fab.deleteOutline()  
                
        x, t, b = self.path[0].x(), self.path[0].y(), self.path[3].y()
        y = b + (b - t)
        self.path[0] = QPointF(x,y)  
        
        x1, t, b = self.path[1].x(), self.path[1].y(), self.path[2].y()
        y1 = b + (b - t)
        self.path[1] = QPointF(x1, y1) 
           
        self.addPoints()    
        self.updatePoints(0, x, y)     
        self.updatePoints(1, x1, y1)
        
        QTimer.singleShot(100, self.fab.updateShadow)
                                                                                                                   
### -------------------------------------------------------- 
class ShadowFab(QWidget):  ## handles shadow, outline, menu
### --------------------------------------------------------    
    def __init__(self, parent):
        super().__init__(parent)
              
        self.cas    = parent
        self.pixmap = parent.pixmap
        # self.scene  = parent.scene  ## hold for now
          
        view = QGraphicsView(self)
        self.scene = QGraphicsScene()
        view.setScene(self.scene)
     
        self.scene.setSceneRect(0,0,DispWidth,DispHeight) 
     
        self.setStyleSheet("QWidget {\n"
            "background-color: rgb(250,250,250);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "color: rgb(125,125,125);\n"
            "}")

        self.file = ''    
        self.ishidden = False

        self.alpha  = 50.0
        self.scalor = 100.0
        
        self.cpy  = None
        self.menu = None
       
        self.outline = None  
        self.opacity = None
        
        self.save = 0,0
        
### --------------------------------------------------------   
    def initShadow(self, file, w, h, parent):  ## replace all colors with grey 
        self.file = file
        img = cv2.imread(self.file, cv2.IMREAD_UNCHANGED)       
        rows, cols, _ = img.shape
    
        wuf = img.copy()  
        for i in range(rows):
            for j in range(cols):
                pixel = img[i,j]
                if pixel[-1] != 0:  ## not transparent      
                    wuf[i,j] = (20,20,20,255)
                                        
        img = cv2.resize(np.array(wuf), (w, h), interpolation = cv2.INTER_CUBIC)
        img = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT)
                
        self.addShadow(img, parent)
                                  
### --------------------------------------------------------    
    def addShadow(self, img, parent):  ## initial shadow                         
        height, width, ch = img.shape
        bytesPerLine = ch * width  ## 4 bits of information -- alpha channel 
        
        self.pixmap = parent.pixmap
        
        image = QImage(img.data, width, height, bytesPerLine, QImage.Format_ARGB32)   
        image.smoothScaled(width, height)  
        
        pixmap = QPixmap.fromImage(image)
              
        self.shadow = Shadows(self) 
        self.shadow.setPixmap(pixmap)
      
        self.cpy = img   ## save it for later  
        self.shadow.imgSize = width, height  ## ditto, fixes a funny little bug
                    
        self.shadow.setX(self.pixmap.x()-50)  ## same as pixmap, add offset
        self.shadow.setY(self.pixmap.y())      
        self.shadow.setOpacity(.50)
                         
        self.scene.addItem(self.shadow)
        
        QTimer.singleShot(100, self.shadow.initPoints)
                          
### --------------------------------------------------------
    def updateShadow(self):  ## everything after initial
        self.deleteOutline()       
        img = self.setPerspective() 
        
        self.addUpdatedShadow(img,  ## needed to rebuild new shadow
            self.shadow.path, 
            self.shadow.points, 
            self.shadow.imgSize,
            self.shadow.opacity())  ## note!!                       
        self.updateOutline()
   
    def setPerspective(self):  ## update gray copy based on path xy's         
        p = []  
        path = self.shadow.path      
        w, h = self.shadow.imgSize[0], self.shadow.imgSize[1]
                        
        for i in range(4):  ## make cv2 happy - get current location of points from path
            x,y = int(path[i].x()), int(path[i].y()) 
            p.append([x,y])
              
        dst = np.float32([p[0], p[1], p[3], p[2]])        
        src = np.float32([[0,0], [w,0], [0, h], [w,h]])
         
        M = cv2.getPerspectiveTransform(src, dst)  ## compute the Matrix
        img = cv2.warpPerspective(self.cpy, M, (DispWidth+300, DispHeight+300))
      
        height, width, ch = img.shape
        bytesPerLine = ch * width  ## 4 bits of information
         
        img = cv2.resize(img, (width, height), interpolation = cv2.INTER_CUBIC)  ## helps smooth out edges
        img = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT) 
              
        img = QImage(img.data, width, height, bytesPerLine, QImage.Format_ARGB32)
        img.smoothScaled(width, height)  
        
        return img
                      
    def addUpdatedShadow(self, img, path, points, size, opacity):  
        pixmap = QPixmap.fromImage(img)                   
        self.scene.removeItem(self.shadow)
        
        self.shadow = Shadows(self)      
        self.shadow.setPixmap(pixmap)    
        ## save these back to new shadow
        self.shadow.path     = path    ## latest path x,y's
        self.shadow.points   = points  ## reference to points, 'topLeft'...
        self.shadow.imgSize  = size    ## original w, h 
        
        self.shadow.setOpacity(opacity)        
        self.scene.addItem(self.shadow)     
      
### --------------------------------------------------------    
    def addMenu(self):
        self.closeMenu()
        self.menu = ShadowMenu(self)
        p = self.shadow.path[0]
        x, y = int(p.x()),  int(p.y())
        self.menu.move(QPoint(x+150,y+100))
        self.resetSliders()
        
    def closeMenu(self):
        if self.menu != None:
            self.menu.close()
            self.menu = None
              
    def newMenu(self):
        self.closeMenu()
        self.deleteOutline()
        self.shadow.removePoints()  
        self.scene.removeItem(self.shadow)
        self.initShadow(self.file, self.shadow.imgSize[0], self.shadow.imgSize[1], self.cas)
        self.alpha, self.scalor, self.ishidden = 50.0, 100.0, False
           
    def resetSliders(self):
        self.menu.opacitySlider.setValue(int(self.alpha))
        self.menu.scaleSlider.setValue(int(self.scalor))

### --------------------------------------------------------                
    def updateOutline(self): 
        self.deleteOutline()
        self.outline = QGraphicsPolygonItem(self.addOutline()) 
        self.outline.setPen(QPen(QColor("lime"), 2, Qt.PenStyle.DotLine))
        self.outline.setZValue(25) 
        if self.ishidden:
            self.outline.hide()    
        self.scene.addItem(self.outline)
    
    def addOutline(self):  
        outline = QPolygonF()   
        for p in self.shadow.path:  
            outline.append(QPointF(p))
        return outline 
    
    def deleteOutline(self): 
        if self.outline != None:
            self.scene.removeItem(self.outline)
            self.outline = None
            
### --------------------------------------------------------
    def flip(self):
        if self.file == '':
            return      
        self.shadow.flip()

    def hideAll(self):
        if self.file == '':
            return 
        if self.ishidden == False:
            if self.outline != None:
                self.outline.hide()
            self.hidePoints()  
            self.ishidden = True
        elif self.ishidden == True: 
            self.ishidden = False    
            self.updateOutline()
            self.hidePoints(False) 
                                                          
    def hidePoints(self, hide=True): 
        for p in self.shadow.points:       
            p.hide() if hide == True else p.show()         
       
    def scaleShadow(self, val): 
        self.deleteOutline()     
         
        centerX, centerY = self.centerXY()
        per = (val - self.scalor) / self.scalor 
               
        self.shadow.setTransformOriginPoint(centerX, centerY)
        self.shadow.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            
        for i in range(0, len(self.shadow.path)):  ## if you don't get 4 points...  
            dist = distance(self.shadow.path[i].x(), centerX, 
                            self.shadow.path[i].y(), centerY)
            
            inc, xdist, ydist = 0, dist, dist      
        
            xdist = dist + (dist * per)              
            ydist = xdist
           
            deltaX = self.shadow.path[i].x() - centerX
            deltaY = self.shadow.path[i].y() - centerY

            angle = math.degrees(math.atan2(deltaX, deltaY))
            angle = angle + math.ceil( angle / 360) * 360

            plotX = centerX + xdist * math.sin(math.radians(angle + inc))
            plotY = centerY + ydist * math.cos(math.radians(angle + inc))
           
            self.shadow.path[i] = QPointF(plotX, plotY)
            self.shadow.updatePoints(i, plotX, plotY)
             
        self.scalor = val
        self.updateShadow()
        
    def centerXY(self): 
        self.shadow.addPoints()         
        x = self.shadow.path[2].x() - self.shadow.path[0].x() 
        x = self.shadow.path[0].x() + ( x / 2 )
        y = self.shadow.path[3].y() - self.shadow.path[1].y() 
        y = self.shadow.path[1].y() + ( y / 2 )
        return x, y
                                      
def distance(x1, x2, y1, y2):
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt((dx * dx ) + (dy * dy))      
                                                                                                                                                      
### --------------------------------------------------------      
class Caster(QWidget):                                                                                                                                        
### -------------------------------------------------------- 
    def __init__(self):
        super().__init__()
           
        self.font = QFont()
        self.setFont(QFont('Helvetica', 13))
           
        self.pixmap = None
                 
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        x = int(((ctr.x() * 2 ) - Width)/2)
        self.setGeometry(x,100,Width,Height)
     
        self.setFixedSize(Width,Height)     
        self.setWindowTitle("cast shadow emulator 4.0") 
    
        self.fab = ShadowFab(self)
        self.buttons = self.setButtons()
     
        vbox = QVBoxLayout()        
        vbox.addWidget(self.fab, Qt.AlignmentFlag.AlignTop| 
            Qt.AlignmentFlag.AlignVCenter)    
        vbox.addWidget(self.buttons, Qt.AlignmentFlag.AlignBottom)   
        
        self.setLayout(vbox)
        self.show()   
 
### --------------------------------------------------------        
    def openFiles(self):  ## open only .png files
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self,  ## dialog never shows
            "Choose an image file to open", "", "Images Files( *.png)")
        if file and file.lower().endswith('.png'):
            self.fab.scene.clear() 
            self.fab.closeMenu()
            self.addPixmap(file)
        else:       
            return  
 
    def addPixmap(self, file):                          
        img = QImage(file)  ## the scene is cleared each new image file  
        self.file = file
        
        if img.width() > Fixed or img.height() > Fixed:  ## size it to fit       
            img = img.scaled(Fixed, Fixed,  ## keep it small
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
      
        self.pixmap = QGraphicsPixmapItem()     
        self.pixmap.setPixmap(QPixmap(img))    
        self.pixmap.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable,True)
        
        self.x = (DispWidth-img.width())/2  ## center it
        self.y = (DispHeight-img.height())/2
        
        self.pixmap.setX(self.x)  
        self.pixmap.setY(self.y)     
        self.pixmap.setZValue(20) 
                
        self.fab.scene.addItem(self.pixmap)
        ## ShadowFab to be called from pixitem - creates its shadow
        self.fab.initShadow(file, img.width(), img.height(), self)
                           
### --------------------------------------------------------    
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedSize(Btns,55)
        
        self.filesBtn = QPushButton("Files")      
        self.filesBtn.clicked.connect(self.openFiles)
                
        self.showBtn = QPushButton("Hide Points")
        self.showBtn.clicked.connect(self.fab.hideAll)
        
        self.flipBtn = QPushButton("Flip It")
        self.flipBtn.clicked.connect(self.fab.flip)
        
        self.backBtn = QPushButton("Background")
        self.backBtn.clicked.connect(self.backGround)
    
        self.quitBtn = QPushButton("Quit")
        self.quitBtn.clicked.connect(self.aclose)
        
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.filesBtn)
        hbox.addWidget(self.showBtn)
        hbox.addWidget(self.flipBtn)
        hbox.addWidget(self.backBtn)
        hbox.addWidget(self.quitBtn)
            
        self.buttonGroup.setLayout(hbox)
        self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.buttonGroup.setLineWidth(1)
  
        return self.buttonGroup
                                    
    def backGround(self):  ## open .png or .jpg
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self,
            "Choose an image file to open", "", "Images Files( *.jpg *.png)")
        if file and file.lower().endswith('.png') or file.lower().endswith('.jpg'):
            self.addBackground(file)
                    
    def addBackground(self, img):  ## img == file name 
        img = QImage(img)                 
        img = img.scaled(DispWidth,DispHeight, 
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
     
        self.background = QGraphicsPixmapItem()     
        self.background.setPixmap(QPixmap(img))    
         
        self.background.setZValue(0) 
        self.fab.scene.addItem(self.background)
        
    def keyPressEvent(self, e):
        if e.key() in ExitKeys:
            self.aclose()
            
    def aclose(self):
        self.fab.closeMenu()
        self.close()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    cas = Caster()
    sys.exit(app.exec())
    


