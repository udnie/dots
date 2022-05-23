
import sys

from PyQt6.QtCore       import Qt, QPointF, QEvent
from PyQt6.QtGui        import QColor, QImage, QPixmap, QGuiApplication, QPen, \
                               QPainterPath, QCursor
from PyQt6.QtWidgets    import QSlider, QWidget, QApplication, QGraphicsView, QGroupBox, \
                               QGraphicsScene, QGraphicsPixmapItem, QLabel,  \
                               QSlider, QHBoxLayout,  QVBoxLayout, QPushButton, QGraphicsPathItem
                       

from dotsSideGig        import getColorStr, distance
from spriteWorks        import PointItem, Works

ExitKeys = (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape)
DispWidth, DispHeight = 720, 720
Width, Height = 860, 840
Btns = 820
Fixed = DispHeight  ## max pixmap size
   
### ------------------- dotsSpriteMaker --------------------                                                                                                                                                                                                                                                                           
class SpriteMaker(QWidget):  
### -------------------------------------------------------- 
    def __init__(self, parent=None):
        super().__init__()
              
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
                 
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        x = int(((ctr.x() * 2 ) - Width)/2)
        self.setGeometry(x,75,Width,Height)
        
        self.setFixedSize(Width,Height)     
        self.setWindowTitle("spriteMaker")
        
        self.scene.setSceneRect(0,0,DispWidth,DispHeight-2) 
     
        self.setStyleSheet("QGraphicsView {\n"
            "background-color: rgb(250,250,250);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "color: rgb(125,125,125);\n"
            "}")

        self.init()     
                
        self.works   = Works(self)
        self.buttons = self.setButtons()
        self.sliders = self.setSliders()
        
        self.enableSliders()  ## off 
        
        self.buttons.setStyleSheet("QLabel {\n"
            "background-color: rgb(230,230,230);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "}")
         
        self.sliders.setStyleSheet("QGroupBox {\n"
            "background-color: rgb(220,220,220);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "}")
  
        hbox = QHBoxLayout()            
        hbox.addWidget(self.view) 
        hbox.addWidget(self.sliders) 
                 
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.buttons, Qt.AlignmentFlag.AlignHCenter)
               
        self.setLayout(vbox)
     
        self.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)     
         
        self.addBtn.setDisabled(True)   
        self.closeBtn.setDisabled(True)
     
        self.show()  
         
### --------------------------------------------------------             
    def init(self):
        self.file = ''
        self.key = ''    

        self.pts  = []
        self.npts = 0 
        self.last = QPointF()
 
        self.outline = None 
      
        self.outlineSet = False 
        self.slidersSet = False
        self.pathClosed = False
       
        self.color  = "WHITE"                  
        self.pixmap = None
        self.rotate = 0.0
        self.scale  = 1.0        
                      
### --------------------- event filter ----------------------                
    def eventFilter(self, source, e):       
        if self.outlineSet:
            if e.type() == QEvent.Type.MouseButtonPress and \
                e.button() == Qt.MouseButton.LeftButton:
                    self.npts = 0  
                    self.addPoints(e.pos())
                    self.last = e.pos()

            elif e.type() == QEvent.Type.MouseMove and \
                e.buttons() == Qt.MouseButton.LeftButton:
                    self.addPoints(e.pos())
           
            elif e.type() == QEvent.Type.MouseButtonRelease and \
                e.button() == Qt.MouseButton.LeftButton:
                    self.pts.append(e.pos())
                    self.updateOutline()  
   
        return QWidget.eventFilter(self, source, e)
                                          
### --------------------------------------------------------     
    def addPoints(self, pt): 
        if self.npts == 0:
            self.pts.append(pt)
        self.npts += 1
        if self.npts % 5 == 0:
            if distance(pt.x(),self.last.x(), pt.y(), self.last.y()) > 15.0:
                self.last = pt     
                self.pts.append(pt)
                self.updateOutline()
                                 
    def addOutLine(self):
        if self.outlineSet == True:
            return
        elif len(self.pts) == 0 and self.slidersSet == True:
            self.outlineSet = True
            QGuiApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
            
    def finalizePixmap(self):  ## the set button in sliders
        if self.pixmap != None: 
            self.works.replacePixmap() 
            self.sliders.setEnabled(False)
            self.slidersSet = True
            self.addBtn.setEnabled(True)
            self.closeBtn.setEnabled(True)
          
    def closeOutLine(self):
         if self.outlineSet:
            QGuiApplication.restoreOverrideCursor()
            self.outlineSet = False 
            self.pathClosed = True
            self.updateOutline()  ## close it         
            self.redrawPoints() 
            self.works.editingOn = True     
            self.addBtn.setEnabled(False)
            self.closeBtn.setEnabled(False)
      
    def updateOutline(self):  ## make a path from pathMaker pts
        self.deleteOutline()
        self.outline = QGraphicsPathItem(self.setPaintPath(self.pathClosed))
        self.outline.setPen(QPen(QColor(self.color), 3, Qt.PenStyle.SolidLine))
        self.outline.setZValue(100) 
        self.scene.addItem(self.outline)
        if self.pathClosed and self.works.cropIt == True: 
            self.works.showCrop()
    
    def setPaintPath(self, bool=False): 
        path = QPainterPath()
        for pt in self.pts: 
            if not path.elementCount():
                path.moveTo(QPointF(pt))
            path.lineTo(QPointF(pt)) 
        if bool: 
            path.closeSubpath()
        return path

    def changePathColor(self):
        self.color = getColorStr()
        self.updateOutline()
        
    def deleteOutline(self): 
        if len(self.pts) > 0 and self.outline != None:
            self.scene.removeItem(self.outline)
            self.outline = None
            
### --------------------------------------------------------  
    def addPointItems(self): 
        idx = 200  ## Zvalues
        for i in range(0, len(self.pts)):  
            self.scene.addItem(PointItem(self.pts[i], i, idx, self))
            idx += 1
       
    def redrawPoints(self): 
        if self.works.editingOn:
            self.removePointItems()
        self.addPointItems()
    
    def removePointItems(self): 
        for p in self.scene.items():
            if p.zValue() >= 200:  ## should only be points
                self.scene.removeItem(p)
                                       
    def hidePoints(self, hide=True): 
        for p in self.pts:       
            p.hide() if hide == True else p.show()        
                                                                                                                                      
### --------------------------------------------------------         
    def addPixmap(self, file):                                          
        img = QImage(file)  ## the scene is cleared each new image file  
        self.file = file
        
        if img.width() > Fixed or img.height() > Fixed:  ## size it to fit       
            img = img.scaled(Fixed-50, Fixed-50,  
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
      
        self.pixmap = QGraphicsPixmapItem()     
        self.pixmap.setPixmap(QPixmap(img))    
        self.pixmap.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
        
        self.x = (DispWidth-img.width())/2  ## center it
        self.y = (DispHeight-img.height())/2
        
        self.pixmap.setX(self.x)  
        self.pixmap.setY(self.y)     
        self.pixmap.setZValue(-100) 
                
        self.scene.addItem(self.pixmap)
        
        self.outlineSet = False
        self.enableSliders(True)
        self.works.init()
                  
### --------------------------------------------------------          
    def setOrigin(self):  
        if self.pixmap != None:
            b = self.pixmap.boundingRect()
            op = QPointF(b.width()/2, b.height()/2)
            self.pixmap.setTransformOriginPoint(op)
            
    def enableSliders(self, bool=False): 
        self.rotationSlider.setValue(0)
        self.scaleSlider.setValue(100)
        self.sliders.setEnabled(bool)
           
    def center(self):
        x = (DispWidth - self.pixmap.width())/2
        y = (DispHeight - self.pixmap.height())/2
        self.pixmap.setPos(x, y)

    def setRotation(self, val):
        self.setOrigin()
        if val < 0:
            val= 0
        self.rotate = val
        self.pixmap.setRotation(val)

    def setScale(self, val):
        self.setOrigin()
        self.scale = val
        self.pixmap.setScale(val)
                                                 
    def resetSliders(self):
        self.rotationSlider.setValue(int(self.rotate))
        self.scaleSlider.setValue(int(self.scale*100))
        
    def Rotation(self, val):
        if self.pixmap != None:
            op = (val)
            self.setRotation(op)
            self.rotationValue.setText("{0:.2f}".format(op)) 
        
    def Scale(self, val):
        if self.pixmap != None:
            op = (val/100)
            self.setScale(op)
            self.scaleValue.setText("{0:.2f}".format(op))  
        
    def clear(self):
        self.scene.clear()
        self.init()    
        
### -------------------------------------------------------- 
    def setSliders(self):
        groupBox = QGroupBox()
        groupBox.setFixedSize(80,DispHeight)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.scaleValue = QLabel("1.00")
        self.scaleSlider = QSlider(Qt.Orientation.Vertical,                   
            minimum=50, maximum=150, singleStep=1, value=100)
        self.scaleSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scaleSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.scaleSlider.setTickInterval(10)  
        self.scaleSlider.setFixedSize(50,260)
        self.scaleSlider.valueChanged.connect(self.Scale)
        self.scaleSlider.setStyleSheet("QSlider {\n"
            "background-color: rgb(240,240,240);\n"
            "}")
                  
        self.rotationValue = QLabel("0")
        self.rotationSlider = QSlider(Qt.Orientation.Vertical,                   
            minimum=0, maximum=360, singleStep=1, value=0)
        self.rotationSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.rotationSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.rotationSlider.setTickInterval(45)  
        self.rotationSlider.setFixedSize(50,260)
        self.rotationSlider.valueChanged.connect(self.Rotation)
        self.rotationSlider.setStyleSheet("QSlider {\n"
            "background-color: rgb(240,240,240);\n"
            "}")
        
        sbox = QVBoxLayout()  ## scale
        sbox.addWidget(QLabel("Scale", alignment=Qt.AlignmentFlag.AlignCenter))
        sbox.addWidget(self.scaleSlider)
        sbox.addSpacing(15) 
        sbox.addWidget(self.scaleValue, alignment=Qt.AlignmentFlag.AlignCenter| \
            Qt.AlignmentFlag.AlignBottom) 
         
        rbox = QVBoxLayout()  ## rotation   
        rbox.addWidget(QLabel("Rotation", alignment=Qt.AlignmentFlag.AlignCenter))                  
        rbox.addWidget(self.rotationSlider)
        rbox.addSpacing(15) 
        rbox.addWidget(self.rotationValue, alignment=Qt.AlignmentFlag.AlignCenter| \
            Qt.AlignmentFlag.AlignBottom) 
        
        self.setBtn = QPushButton("Set")      
        self.setBtn.clicked.connect(self.finalizePixmap)
        
        vbox = QVBoxLayout()  
        vbox.addLayout(sbox)
        vbox.addSpacing(20) 
        vbox.addLayout(rbox)
        vbox.addSpacing(10) 
        vbox.addWidget(self.setBtn)
        
        groupBox.setLayout(vbox)
        
        return groupBox
                                                                                  
### --------------------------------------------------------    
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedSize(Btns,55)
        
        filesBtn = QPushButton("Files")      
        filesBtn.clicked.connect(self.works.openFiles)
                
        self.addBtn = QPushButton("Outline")
        self.addBtn.clicked.connect(self.addOutLine)
        
        self.closeBtn = QPushButton("Close")
        self.closeBtn.clicked.connect(self.closeOutLine)
        
        self.changeBtn = QPushButton("Path Color")
        self.changeBtn.clicked.connect(self.changePathColor)

        self.previewBtn = QPushButton("Preview")
        self.previewBtn.clicked.connect(self.works.preview)

        self.editBtn = QPushButton("Edit")
        self.editBtn.clicked.connect(self.works.edit)
        
        self.clearBtn = QPushButton("Clear")
        self.clearBtn.clicked.connect(self.clear)
         
        self.saveBtn = QPushButton("Save")
        self.saveBtn.clicked.connect(self.works.saveSprite)
    
        quitBtn = QPushButton("Quit")
        quitBtn.clicked.connect(self.aclose)
        
        hbox = QHBoxLayout(self)
        hbox.addWidget(filesBtn)
        hbox.addWidget(self.addBtn)
        hbox.addWidget(self.closeBtn)
        hbox.addWidget(self.changeBtn)
        hbox.addWidget(self.previewBtn)
        hbox.addWidget(self.editBtn)
        hbox.addWidget(self.clearBtn)   
        hbox.addWidget(self.saveBtn)
        hbox.addWidget(quitBtn)
            
        self.buttonGroup.setLayout(hbox)
  
        return self.buttonGroup
    
### --------------------------------------------------------                                                             
    def keyPressEvent(self, e):
        if e.key() in ExitKeys:
            self.aclose()
        elif e.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):  ## can vary
            self.setKey('del')
        elif e.key() == Qt.Key.Key_Alt:
            self.setKey('opt')
        elif e.key() == Qt.Key.Key_Shift: 
            self.works.toggleCrop()
                    
    def setKey(self, key): 
        self.key = key
       
    def keyReleaseEvent(self,e):  
        self.key = '' 
           
    def aclose(self):
        QGuiApplication.restoreOverrideCursor()
        self.close()
        
### -------------------------------------------------------- 
if __name__ == '__main__':
    app = QApplication(sys.argv) 
    boo = SpriteMaker()
    sys.exit(app.exec())

### ------------------- dotsSpriteMaker --------------------

