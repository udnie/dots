
import sys
import cv2
import numpy as np

from PyQt5.QtCore    import Qt, QPointF, QTimer, QRectF
from PyQt5.QtGui     import QColor, QImage, QPixmap, QFont, QGuiApplication, QPolygonF, QPen, \
                            QPainterPath, QRegion, QTransform
from PyQt5.QtWidgets import QSlider, QWidget, QApplication, QGraphicsView,  QGroupBox, \
                            QGraphicsScene, QGraphicsPixmapItem, QLabel, QGraphicsPolygonItem, \
                            QSlider, QHBoxLayout,  QVBoxLayout, QGridLayout, QPushButton, \
                            QGraphicsEllipseItem, QFileDialog, QFrame

ExitKeys = (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape)
DispWidth, DispHeight = 900, 600
Width, Height = 1060, 710
Btns = 902
Fixed = 200  ## size
Xoff, Yoff, Opacity = 0, 0, 50  ## no scale, no rgb
V = 12.0  ## the diameter of a pointItem
PathStr = ["topLeft","topRight","botRight","botLeft"]

### --------------------------------------------------------
class PointItem(QGraphicsEllipseItem):
### --------------------------------------------------------
    def __init__(self, pt, ptStr, parent):
        super().__init__()

        self.shadow  = parent
        self.display = parent.display
         
        self.type  = "pt"
        self.ptStr = ptStr
        
        self.setZValue(50) 
          
        ## -V*.5 so it's centered on the path 
        self.x = pt.x()-V*.5
        self.y = pt.y()-V*.5
        
        self.setRect(self.x, self.y, V, V)  
        
        self.setPen(QPen(QColor("gray"), 1))
        if self.ptStr in ("topLeft","topRight"):
            self.setBrush(QColor("yellow"))
        else:
            self.setBrush(QColor("lime"))
          
        self.dragCnt = 0
        self.save = 0.0
                     
 ### --------------------------------------------------------
    def mousePressEvent(self, e): 
        self.save = e.pos()     
        # x, y = e.pos().x(), e.pos().y()
        # i = PathStr.index(self.ptStr)  
        # self.shadow.path[i] = QPointF(x,y)  
        e.accept() 
        
    def mouseMoveEvent(self, e):
        self.dragCnt += 1
        if self.dragCnt % 5 == 0:            
            self.moveIt(e.pos()) 
            self.display.updateShadow()                  
        e.accept()
                       
    def mouseReleaseEvent(self, e):
        self.moveIt(e.pos())
        self.display.updateShadow()
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
class Shadows(QGraphicsPixmapItem):
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
       
        self.display = parent
        self.scene   = parent.scene
        
        self.topLeft  = None
        self.topRight = None
        self.botLeft  = None
        self.botRight = None
       
        self.path = []  ## maintain path per session 
        self.points = []
        
        self.cpy  = None
        self.poly = None
              
        self.ishidden = False
        
        self.type  = "shadow"
        self.setZValue(10)   
  
        self.dragCnt = 0
        self.save = 0.0
        self.imgSize = 0,0
                                
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
          
### --------------------------------------------------------
    def mousePressEvent(self, e): 
        if e.button() == Qt.RightButton:
            print('gg')
        self.save = self.mapToScene(e.pos()) 
        # self.updatePoly()
        self.addPoints()
        e.accept() 
        
    def mouseMoveEvent(self, e):
        self.dragCnt += 1
        if self.dragCnt % 5 == 0:                     
            self.updatePath(self.mapToScene(e.pos()))   
            self.updatePoly()
        e.accept()
                       
    def mouseReleaseEvent(self, e):
        self.updatePath(self.mapToScene(e.pos())) 
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
        self.poly = None
        
        b = self.boundingRect()  
        p = self.pos() 
        
        self.path.append(p)  
        self.path.append(QPointF(p.x() + b.width(), p.y()))  
        self.path.append(QPointF(p.x() + b.width(), p.y() + b.height()))         
        self.path.append(QPointF(p.x(), p.y() + b.height()))
      
        self.updatePoly()  
        self.addPoints()
                                                                     
    def addPoints(self): 
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
            if self.ishidden:
                p.hide()                              
            self.scene.addItem(p)
     
    def hidePoints(self, hide=True): 
        for p in self.points:       
            p.hide() if hide else p.show()
                                                                                                                         
    def removePoints(self): 
        for p in self.points:  
            self.scene.removeItem(p)
                                
    def updatePoints(self, i, x, y):  ## offset for x,y of ellipse    
        if i == 0:
            self.topLeft.setRect(x-V*.5, y-V*.5, V,V) 
        elif i == 1:      
            self.topRight.setRect(x-V*.5, y-V*.5, V,V)         
        elif i == 3: 
            self.botLeft.setRect(x-V*.5, y-V*.5, V,V) 
        else:                          
            self.botRight.setRect(x-V*.5, y-V*.5, V,V)

### -------------------------------------------------------- 
    def updatePoly(self): 
        if self.ishidden:
            if self.poly != None:
                self.poly.hide()
            return
        self.deletePoly()
        self.poly = QGraphicsPolygonItem(self.addPoly()) 
        self.poly.setPen(QPen(QColor("lime"), 2, Qt.PenStyle.DotLine))
        self.poly.setZValue(25) 
        self.scene.addItem(self.poly)
     
    def addPoly(self):  
        poly = QPolygonF()   
        for p in self.path:  
            poly.append(QPointF(p))
        return poly 
    
    def deletePoly(self): 
        if self.poly != None:
            self.scene.removeItem(self.poly)
            self.poly = None
                       
### --------------------------------------------------------                                                   
    def flip(self): 
        # self.removePoints()  
                 
        x, t, b = self.path[0].x(), self.path[0].y(), self.path[3].y()
        y = b + (b - t)
        self.path[0] = QPointF(x,y)  
        
        x1, t, b = self.path[1].x(), self.path[1].y(), self.path[2].y()
        y1 = b + (b - t)
        self.path[1] = QPointF(x1, y1) 
        
        self.addPoints()
        
        self.updatePoints(0, x, y)     
        self.updatePoints(1, x1, y1)
        
        QTimer.singleShot(100, self.display.updateShadow)
                                                                              
    def hideAll(self):
        if self.ishidden == False:
            self.poly.hide()
            self.hidePoints() 
            self.ishidden = True
        else:        
            self.ishidden = False    
            self.updatePoly()
            self.hidePoints(False) 
        
class ShadowMenu(QWidget):
    def __init__(self):
        super().__init__()
                      
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
           
    def mousePressEvent(self, e):
        self.save = e.globalPos()

    def mouseMoveEvent(self, e):
        dif = QPointF(e.globalPos() - self.save)
        self.move(self.pos() + dif) 
        self.save = e.globalPos()

    def sliderGroup(self):
        groupBox = QGroupBox("Opacity")
        groupBox.setFixedWidth(55)
        
        slider = QSlider(Qt.Vertical)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        slider.setTickInterval(10)        
        slider.setSingleStep(1)

        vbox = QVBoxLayout()
        vbox.addWidget(slider)
        
        groupBox.setLayout(vbox)
        return groupBox

    def buttonGroup(self):
        groupBox = QGroupBox("Feel Lucky?")
        groupBox.setFixedWidth(75)
                     
        hideBtn = QPushButton("Hide")
        flipBtn = QPushButton("Flip")
        quitBtn = QPushButton("Close")
    
        hideBtn.clicked.connect(self.close)
        flipBtn.clicked.connect(self.close)
        quitBtn.clicked.connect(self.close)
    
        hbox = QVBoxLayout(self)
        hbox.addWidget(hideBtn)
        hbox.addWidget(flipBtn)
        hbox.addWidget(quitBtn)
                
        groupBox.setLayout(hbox)
        return groupBox
                                                                                                                                         
### -------------------------------------------------------- 
class Display(QWidget): 
### --------------------------------------------------------    
    def __init__(self, parent):
        super(Display, self).__init__(parent)
        
        self.setStyleSheet("QWidget {\n"
            "background-color: rgb(250,250,250);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "color: rgb(125,125,125);\n"
            "}")
      
        self.cas = parent
         
        view = QGraphicsView(self)
        self.scene = QGraphicsScene()
        view.setScene(self.scene)
     
        self.scene.setSceneRect(0,0,DispWidth,DispHeight)   
        
        self.init()
        
### --------------------------------------------------------       
    def init(self):
        self.pixmap = None 
        self.file = ''    
        self.x = 0
        self.y = 0
        self.alpha = .50    
        
### --------------------------------------------------------       
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
                
        self.scene.addItem(self.pixmap)
        self.initShadow(img.width(), img.height())
         
### --------------------------------------------------------   
    def initShadow(self, w, h):  ## replace all colors with grey
        if self.file != "":
            img = cv2.imread(self.file, cv2.IMREAD_UNCHANGED)       
            rows, cols, _ = img.shape
        
            wuf = img.copy()  
            for i in range(rows):
                for j in range(cols):
                    pixel = img[i,j]
                    if pixel[-1] != 0:  ## not transparent      
                       wuf[i,j] = (20,20,20,255)
                                         
            img = cv2.resize(np.array(wuf), (w, h))
            img = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT)
                   
            self.addShadow(img)
                                  
### --------------------------------------------------------    
    def addShadow(self, img):  ## initial shadow                         
        height, width, ch = img.shape
        bytesPerLine = ch * width  ## 4 bits of information -- alpha channel 
        
        image = QImage(img.data, width, height, bytesPerLine, QImage.Format_ARGB32)   
        image.smoothScaled(width, height)  
        
        pixmap = QPixmap.fromImage(image)
              
        self.shadow = Shadows(self) 
        self.shadow.setPixmap(pixmap)
      
        self.shadow.cpy = img   ## save it for later  
        self.shadow.imgSize = width, height  ## ditto, fixes a funny little bug
                    
        self.shadow.setX(self.x)  ## same as pixmap
        self.shadow.setY(self.y)      
        self.shadow.setOpacity(self.alpha)
                         
        self.scene.addItem(self.shadow)
        
        QTimer.singleShot(100, self.shadow.initPoints)
                          
### --------------------------------------------------------
    def updateShadow(self):  ## everything after initial
        self.shadow.deletePoly()
        self.setPerspective()
        self.shadow.updatePoly()
   
    def setPerspective(self):       
        path = self.shadow.path
        cpy  = self.shadow.cpy
        w, h = self.shadow.imgSize[0], self.shadow.imgSize[1]
                        
        p = []
        for i in range(4):  ## make cv2 happy - get current location of points from path
            x,y = int(path[i].x()), int(path[i].y()) 
            p.append([x,y])
              
        dst = np.float32([p[0], p[1], p[3], p[2]])        
        src = np.float32([[0,0], [w,0], [0, h], [w,h]])
         
        M = cv2.getPerspectiveTransform(src, dst)  ## compute the Matrix
        img = cv2.warpPerspective(cpy, M, (DispWidth+300, DispHeight+300))
      
        height, width, ch = img.shape
        bytesPerLine = ch * width  ## 4 bits of information
         
        img = cv2.resize(img, (width, height))  ## helps smooth out edges
        img = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT) 
              
        img = QImage(img.data, width, height, bytesPerLine, QImage.Format_ARGB32)
        img.smoothScaled(width, height)  
                      
        self.addUpdatedShadow(img,  ## needed to rebuild new shadow
            self.shadow.path, 
            self.shadow.cpy, 
            self.shadow.points, 
            self.shadow.ishidden, 
            self.shadow.imgSize
        )                    
        
    def addUpdatedShadow(self, img, path, cpy, points, hide, size):       
        pixmap = QPixmap.fromImage(img)
        self.scene.removeItem(self.shadow)
                 
        self.shadow = Shadows(self)      
        self.shadow.setPixmap(pixmap)
        
        ## save these back to new shadow
        self.shadow.cpy      = cpy     ## copy of original gray 
        self.shadow.path     = path    ## latest path x,y's
        self.shadow.points   = points  ## reference to points, 'topLeft'...
        self.shadow.ishidden = hide    ## ishidden T/F
        self.shadow.imgSize  = size    ## original w, h
     
        self.scene.addItem(self.shadow)
        
        self.shadow.setOpacity(self.alpha)        
        self.cas.opacitySlider.setValue(int(self.alpha*100))    
   
### --------------------------------------------------------                      
    def hideAll(self):
        if self.file == '':
            return
        self.shadow.hideAll() 
               
    def flip(self):
        if self.file == '':
            return      
        self.shadow.flip()
                                                                 
### --------------------------------------------------------     
    def addBackground(self, img):  ## img == file name 
        img = QImage(img)                 
        img = img.scaled(DispWidth,DispHeight, 
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
     
        self.background = QGraphicsPixmapItem()     
        self.background.setPixmap(QPixmap(img))    
         
        self.background.setZValue(0) 
        self.scene.addItem(self.background) 
             
    def opacity(self, val):
        if self.file != "":
            self.alpha = (val/100)
            self.shadow.setOpacity(self.alpha)
            self.cas.opacityValue.setText("{:3d}".format(val)) 
             
    def resetSliders(self):  
        self.shadow.poly = None      
        self.cas.opacitySlider.setValue(Opacity)
                                       
### --------------------------------------------------------      
class Caster(QWidget):  
    def __init__(self):
        super(Caster, self).__init__()

        self.font = QFont()
        self.setFont(QFont('Helvetica', 13))
        
        self.setFixedSize(Width,Height)
        self.setWindowTitle("cast shadow emulator 3.0")
        
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        x = int(((ctr.x() * 2 ) - Width)/2)
     
        self.setGeometry(x,100,Width,Height)
     
        self.display = Display(self)
        self.sliders = self.setSliders() 
        self.buttons = self.setButtons()
       
        hbox = QHBoxLayout()     
        vbox = QVBoxLayout()  
         
        vbox.addWidget(self.display, Qt.AlignmentFlag.AlignTop| 
            Qt.AlignmentFlag.AlignVCenter)    
        vbox.addWidget(self.buttons, Qt.AlignmentFlag.AlignBottom)   
        
        wbox = QVBoxLayout() 
        wbox.addWidget(self.sliders, Qt.AlignmentFlag.AlignTop)

        hbox.addLayout(vbox)  
        hbox.addLayout(wbox) 
        
        self.setLayout(hbox)
        self.enableSliders()  ## false to start
        
        self.show()   
 
 ### --------------------------------------------------------                                         
    def enableSliders(self, bool=False): 
        self.sliderGroup.setEnabled(bool)
                                      
    def setSliders(self):     
        self.sliderGroup = QLabel()
        self.sliderGroup.setFixedSize(90,400)
                               
        opacityLabel = QLabel("Opacity")
        opacityLabel.setFont(self.font)
        self.opacityValue = QLabel("1.00")
        self.opacitySlider = QSlider(Qt.Orientation.Vertical, 
            minimum=0, maximum=100, singleStep=1, value=1)
        self.opacitySlider.valueChanged.connect(self.display.opacity)
                
### --------------------------------------------------------                  
        widget = QWidget()
        grid = QGridLayout(widget) 
       
        grid.addWidget(opacityLabel, 10, 0, Qt.AlignmentFlag.AlignHCenter)
        grid.addWidget(self.opacitySlider, 11, 0, Qt.AlignmentFlag.AlignHCenter)
        grid.addWidget(self.opacityValue, 12, 0, Qt.AlignmentFlag.AlignHCenter)
                                    
        grid.setContentsMargins(0, 0, 0, 0)
             
        vbox = QVBoxLayout(self)                       
        vbox.addWidget(widget) 
        
        self.sliderGroup.setLayout(vbox)
        self.sliderGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.sliderGroup.setLineWidth(1)

        return self.sliderGroup
    
### --------------------------------------------------------    
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedSize(Btns,55)
        
        self.filesBtn = QPushButton("Files")      
        self.filesBtn.clicked.connect(self.openFiles)
                
        self.showBtn = QPushButton("Hide Points")
        self.showBtn.clicked.connect(self.display.hideAll)
        
        self.flipBtn = QPushButton("Flip It")
        self.flipBtn.clicked.connect(self.display.flip)
        
        self.backBtn = QPushButton("Background")
        self.backBtn.clicked.connect(self.backGround)
    
        self.quitBtn = QPushButton("Quit")
        self.quitBtn.clicked.connect(self.close)
        
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
    
    def openFiles(self):  ## open only .png files
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self,  ## dialog never shows
            "Choose an image file to open", "", "Images Files( *.png)")
        if file and file.lower().endswith('.png'):
            self.display.scene.clear()
            self.display.init()
            self.enableSliders(True)  
            self.display.addPixmap(file)
            self.display.resetSliders() 
        else:       
            return  
                                
    def backGround(self):  ## open .png or .jpg
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self,
            "Choose an image file to open", "", "Images Files( *.jpg *.png)")
        if file and file.lower().endswith('.png') or file.lower().endswith('.jpg'):
            self.display.addBackground(file)
                    
    def keyPressEvent(self, e):
        if e.key() in ExitKeys:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cas = Caster()
    sys.exit(app.exec())
    


