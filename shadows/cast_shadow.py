
import sys

import cv2
import numpy as np

from PyQt5.QtCore    import Qt, QPointF, QTimer
from PyQt5.QtGui     import QColor, QImage, QPixmap, QFont, QGuiApplication, QPolygonF, QPen, \
                            QTransform
from PyQt5.QtWidgets import QMessageBox, QSlider, QWidget, QApplication, QGraphicsView, \
                            QGraphicsScene, QGraphicsPixmapItem, QLabel, QGraphicsPolygonItem, \
                            QSlider, QHBoxLayout,  QVBoxLayout, QGridLayout, QPushButton, \
                            QGraphicsEllipseItem, QFileDialog, QFrame

ExitKeys = (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape)
DispWidth, DispHeight = 425, 425
Width, Height = 920, 470 
Fixed = 250  ## size
Xoff, Yoff, Opacity = 0, 0, 50  ## no scale, no rgb
V = 10.0  ## the diameter of a pointItem
PathStr = ["topLeft","topRight","botRight","botLeft"]

### --------------------------------------------------------
class PointItem(QGraphicsEllipseItem):
### --------------------------------------------------------
    def __init__(self, pt, ptStr, parent):
        super().__init__()

        self.display = parent
        self.scene  = parent.scene
        self.pixmap = parent.pixmap
         
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
        x, y = e.pos().x(), e.pos().y()
        i = PathStr.index(self.ptStr)  
        self.display.path[i] = QPointF(x,y)  
        self.display.clearXY()  ## otherwise things get out of sync
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
            self.display.path[0] = QPointF(x,y) 
            self.display.path[1] = QPointF(x+w,y1)
            self.display.topRight.setRect(x+(w-V*.5), y1-V*.5, V,V)       
        elif self.ptStr == "botLeft":    
            w, y1 = self.current(3,2)            
            self.display.path[3] = QPointF(x,y) 
            self.display.path[2] = QPointF(x+w,y1)
            self.display.botRight.setRect(x+(w-V*.5), y1-V*.5, V,V)          
        else:  
            i = PathStr.index(self.ptStr)  ## move only 
            self.display.path[i] = QPointF(x,y)                  
        self.display.drawPath()
     
    def current(self,a,b):
        l = self.display.path[a].x()
        r = self.display.path[b].x()
        return r - l,  self.display.path[b].y()
     
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
        
    def init(self):
        self.pixmap = None 
        self.shadow = None
        self.cpy    = None 
        self.poly   = None
        
        self.topLeft  = None
        self.topRight = None
        self.botLeft  = None
        self.botRight = None
   
        self.saveY = 0
        self.saveX = 0
        self.alpha = .50
        
        self.file = ""
        self.path = [] 
     
        self.x = 0
        self.y = 0
        
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
        
        self.x = (DispWidth-img.width())/2  ## center it
        self.y = (DispHeight-img.height())/2
        
        self.pixmap.setX(self.x)  
        self.pixmap.setY(self.y)     
        self.pixmap.setZValue(20) 
        
        self.scene.addItem(self.pixmap)
        self.addShadow(img.width(), img.height())
         
### --------------------------------------------------------   
    def addShadow(self, w, h):
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
                
            self.cpy = img  ## save it for later    
            self.initialShadow(self.cpy)  
     
    ### --------------------------------------------------------    
    def initialShadow(self, img):  
        height, width, ch = img.shape
        bytesPerLine = ch * width  ## 4 bits of information -- alpha channel 
        
        img = QImage(img.data, width, height, bytesPerLine, QImage.Format_ARGB32) 
        img.smoothScaled(width, height)     
        
        pixmap = QPixmap.fromImage(img)
              
        self.shadow = QGraphicsPixmapItem()     
        self.shadow.setPixmap(pixmap)
                     
        self.shadow.setX(self.x)  ## same as pixmap
        self.shadow.setY(self.y)
        
        self.shadow.setOpacity(self.alpha)
        self.shadow.setZValue(10)    
                       
        self.scene.addItem(self.shadow)
        QTimer.singleShot(100, self.drawPolygon)
 
 ### --------------------------------------------------------
    def updateShadow(self): 
        self.addUpdatedShadow(self.setPerspective())   
        
    def setPerspective(self):                            
        p = []
        for i in range(4):  ## get current location of points from path
            x,y = int(self.path[i].x()), int(self.path[i].y()) 
            p.append([x,y])
            
        dst = np.float32([p[0], p[1], p[3], p[2]])        
        src = np.float32([[0,0],[Fixed,0],[0, Fixed],[Fixed,Fixed]])
         
        M = cv2.getPerspectiveTransform(src, dst)   
        ## give it room to move around 
        img = cv2.warpPerspective(self.cpy, M, (DispWidth+300, DispHeight+300))  
    
        height, width, _ = img.shape
        bytesPerLine = 4 * width  ## 4 bits of information
        
        img = cv2.resize(np.array(img), (width, height))  ## helps smooth out edges
        img = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT) 
        
        img = QImage(img.data, width, height, bytesPerLine, QImage.Format_ARGB32)
        img.smoothScaled(width, height)  
        
        return img    
     
    ### --------------------------------------------------------
    def addUpdatedShadow(self, img):
        pixmap = QPixmap.fromImage(img)
        self.scene.removeItem(self.shadow)
              
        self.shadow = QGraphicsPixmapItem()     
        self.shadow.setPixmap(pixmap)
 
        pos = self.topLeft.pos()   
        x,y = int(pos.x()), int(pos.y())
  
        self.shadow.setX(x)
        self.shadow.setY(y)
        
        self.shadow.setZValue(10)         
        self.shadow.setOpacity(self.alpha) 
             
        self.scene.addItem(self.shadow)
                
        self.cas.xoffSlider.setValue(x)
        self.cas.yoffSlider.setValue(y)      
        self.cas.opacitySlider.setValue(int(self.alpha*100))    
                      
### --------------------------------------------------------                                                                      
    def drawPolygon(self):  ## draw a four point polygon around shadow
        if self.path:
            return 
           
        self.path = []  
        self.poly = None
        
        b = self.shadow.boundingRect()  
        p = self.shadow.pos() 
    
        self.path.append(p)  
        self.path.append(QPointF(p.x() + b.width(), p.y()))  
        self.path.append(QPointF(p.x() + b.width(), p.y() + b.height()))         
        self.path.append(QPointF(p.x(), p.y() + b.height())) 

        self.drawPath()  
        self.addPoints()
        
        self.saveX = p.x()
        self.saveY = p.y()
        
    def showTime(self):
        if not self.shadow:
            return
        if self.poly != None:
            self.scene.removeItem(self.poly)
            self.removePointItems() 
            self.poly = None
        else:
            self.drawPath()  ## add polygon
            QTimer.singleShot(100, self.addPoints)
    
    def test(self):
        if not self.scene.itemAt(self.path[0], QTransform()):          
            self.path[0] = self.shadow.pos()
  
    def addBackground(self, img):  ## img == file name 
        img = QImage(img)                 
        img = img.scaled(DispWidth,DispHeight, 
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
     
        self.background = QGraphicsPixmapItem()     
        self.background.setPixmap(QPixmap(img))    
         
        self.background.setZValue(0) 
        self.scene.addItem(self.background) 
          
 ### --------------------------------------------------------                 
    def drawPath(self): 
        if self.poly:
            self.scene.removeItem(self.poly)
        self.poly = QGraphicsPolygonItem(self.drawPoly()) 
        self.poly.setPen(QPen(QColor("lime"), 2, Qt.PenStyle.DotLine))
        self.poly.setZValue(25) 
        self.scene.addItem(self.poly)
            
    def drawPoly(self):  
        poly = QPolygonF()   
        for p in self.path:  
            poly.append(QPointF(p))
        return poly       
    
    def addPoints(self):
        self.topLeft  = PointItem(self.path[0], "topLeft", self)
        self.topRight = PointItem(self.path[1], "topRight", self)
        self.botRight = PointItem(self.path[2], "botRight", self)
        self.botLeft  = PointItem(self.path[3], "botLeft", self)
                     
        self.scene.addItem(self.topLeft)
        self.scene.addItem(self.topRight)
        self.scene.addItem(self.botRight)
        self.scene.addItem(self.botLeft)
                                                 
    def removePointItems(self):   
        for i in range(4):  ## get currnet location of points from path
            p = QPointF(self.path[i].x(), self.path[i].y())  
            if p := self.scene.itemAt(p, QTransform()):  ## I am the Walrus, I am the Eggman
                if p.zValue() == 50:
                    self.scene.removeItem(p)

### --------------------------------------------------------     
    def xoffSet(self, val):  
        if self.file != "":
            self.shadow.setX(val)
            self.cas.xoffValue.setText("{:3d}".format(val))
            self.updateX(val) 
  
    def yoffSet(self, val):  
        if self.file != "":  
            self.shadow.setY(val)
            self.cas.yoffValue.setText("{:3d}".format(val))
            self.updateY(val) 
        
    def opacity(self, val):
        if self.file != "":
            self.alpha = (val/100)
            self.shadow.setOpacity(self.alpha)
            self.cas.opacityValue.setText("{:3d}".format(val)) 
  
### --------------------------------------------------------
    def updateX(self, val):
        if self.path:
            t = val - self.saveX
            for i in range(4):  
                x,y = self.path[i].x(), self.path[i].y()
                self.path[i] = QPointF(x+t,y)
                self.updatePoints(i,x+t,y)
            self.saveX = val
            if self.poly:
                self.drawPath() 
                             
    def updateY(self, val):
        if self.path:
            t = val - self.saveY
            for i in range(4):  
                x,y = self.path[i].x(), self.path[i].y()
                self.path[i] = QPointF(x,y+t)
                self.updatePoints(i,x,y+t)
            self.saveY = val 
            if self.poly:
                self.drawPath()  
            
    def updatePoints(self, i, x, y):      
        if i == 0:
            self.topLeft.setRect(x-V*.5, y-V*.5, V,V) 
        elif i == 1:      
            self.topRight.setRect(x-V*.5, y-V*.5, V,V)         
        elif i == 3: 
            self.botLeft.setRect(x-V*.5, y-V*.5, V,V) 
        else:                          
            self.botRight.setRect(x-V*.5, y-V*.5, V,V) 
                                            
    def flip(self):
        if not self.shadow:
            return
       
        test = False
        if self.scene.itemAt(self.path[0], QTransform()): 
            test = True
        self.clearXY()
        
        x, t, b = self.path[0].x(), self.path[0].y(), self.path[3].y()
        self.path[0] = QPointF(x, b + (b - t))   
        self.updatePoints(0, x, b + (b - t))
        
        x, t, b = self.path[1].x(), self.path[1].y(), self.path[2].y()   
        self.path[1] = QPointF(x, b + (b - t)) 
        self.updatePoints(1, x, b + (b - t))
 
        if test:
            self.drawPath()
        QTimer.singleShot(100, self.updateShadow)
              
    def resetSliders(self):  
        self.poly = None 
        self.cas.xoffSlider.setValue(int(self.x))  ## originally 0, now set by shadow
        self.cas.yoffSlider.setValue(int(self.y))       
        self.cas.opacitySlider.setValue(Opacity)
                               
    def clearXY(self):
        self.saveX, self.saveY = 0, 0
        
### --------------------------------------------------------      
class Caster(QWidget):  
    def __init__(self):
        super(Caster, self).__init__()

        self.font = QFont()
        self.setFont(QFont('Helvetica', 13))
        
        self.setFixedSize(Width,Height)
        self.setWindowTitle("a cast shadow emulator")
        
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        x = int(((ctr.x() * 2 ) - Width)/2)
     
        self.setGeometry(x,150,Width,Height)
     
        self.display = Display(self)
        self.sliders = self.setSliders() 
        self.buttons = self.setButtons()
       
        hbox = QHBoxLayout() 
        hbox.addWidget(self.display, Qt.AlignmentFlag.AlignBottom| 
            Qt.AlignmentFlag.AlignVCenter)
               
        vbox = QVBoxLayout()      
        vbox.addSpacing(-8)
        vbox.addWidget(self.sliders, Qt.AlignmentFlag.AlignTop)
        vbox.addSpacing(5)
        vbox.addWidget(self.buttons, Qt.AlignmentFlag.AlignBottom)
    
        hbox.addLayout(vbox)    
        self.setLayout(hbox)
        
        self.enableSliders()  ## false to start
        
        self.show()   
 
 ### --------------------------------------------------------                                         
    def enableSliders(self, bool=False): 
        self.sliderGroup.setEnabled(bool)
        
    def openFiles(self):  ## filter for *.png - may not be transparent
        Q = QFileDialog() 
        file, _ = Q.getOpenFileName(self,  ## these dialogs don't work
            "Choose an image file to open", "", "Images Files( *.png)")
        if file and file.lower().endswith('.png'):
            self.display.scene.clear()
            self.display.init()
            self.enableSliders(True)  
            self.display.addPixmap(file)
            self.display.resetSliders()    
        else:           
            return   
                              
    def setSliders(self):     
        self.sliderGroup = QLabel()
        self.sliderGroup.setFixedSize(430,345)
              
        xoffLabel = QLabel("XOffSet")
        xoffLabel.setFont(self.font)
        self.xoffValue = QLabel("1")
        self.xoffSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=-350, maximum=350, singleStep=1, value=1)
        self.xoffSlider.valueChanged.connect(self.display.xoffSet)
        self.xoffSlider.sliderReleased.connect(self.display.test)
             
        yoffLabel = QLabel("YOffSet")
        yoffLabel.setFont(self.font)
        self.yoffValue = QLabel("1")
        self.yoffSlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=-350, maximum=350, singleStep=1, value=1)
        self.yoffSlider.valueChanged.connect(self.display.yoffSet)
        self.yoffSlider.sliderReleased.connect(self.display.test)
                 
        opacityLabel = QLabel("Opacity")
        opacityLabel.setFont(self.font)
        self.opacityValue = QLabel("1.00")
        self.opacitySlider = QSlider(Qt.Orientation.Horizontal, 
            minimum=0, maximum=100, singleStep=1, value=1)
        self.opacitySlider.valueChanged.connect(self.display.opacity)
                
### --------------------------------------------------------                  
        widget = QWidget()
        grid = QGridLayout(widget) 
    
        grid.addWidget(xoffLabel, 2, 0)
        grid.addWidget(self.xoffValue, 2, 1)        
        grid.addWidget(self.xoffSlider, 3, 0)

        grid.addWidget(yoffLabel, 4, 0)
        grid.addWidget(self.yoffValue, 4, 1)    
        grid.addWidget(self.yoffSlider, 5, 0)
       
        grid.addWidget(opacityLabel, 10, 0)
        grid.addWidget(self.opacityValue, 10, 1) 
        grid.addWidget(self.opacitySlider, 11, 0)
                                    
        grid.setContentsMargins(20, -5, 0, -15)
             
        vbox = QVBoxLayout(self)                       
        vbox.addWidget(widget) 
        
        self.sliderGroup.setLayout(vbox)
        self.sliderGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.sliderGroup.setLineWidth(1)

        return self.sliderGroup
    
### --------------------------------------------------------    
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedSize(430,55)
        
        self.filesBtn = QPushButton("Files")      
        self.filesBtn.clicked.connect(self.openFiles)
                
        self.showBtn = QPushButton("Hide Points")
        self.showBtn.clicked.connect(self.display.showTime)
        
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
                              
    def backGround(self):
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
    


