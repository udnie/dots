
import sys
import time

from PyQt6.QtCore       import Qt, QPointF, QEvent
from PyQt6.QtGui        import QColor, QGuiApplication, QPen, QPainterPath, QCursor                             
from PyQt6.QtWidgets    import QSlider, QWidget, QApplication, QGraphicsView, QGroupBox, \
                               QGraphicsScene, QLabel, QGraphicsPathItem, QGraphicsEllipseItem, \
                               QSlider, QHBoxLayout,  QVBoxLayout, QPushButton 
                       
from spriteMakerWorks       import Works
from spriteMakerLoupe       import Loupe, ViewW, ViewH
from spriteMakerPoints      import PointItem, SaveTxy, getColorStr, distance, constrainXY
    
Btns = 820
Width, Height = 860, 835

### ------------------- dotsSpriteMaker -------------------- 
''' If you're planning to use a .png file for your sprite you'll 
    need to save your output to some other file name otherwise 
    it will be written over. Using a file with a .jpg extension 
    won't have this problem.  '''  
### --------------------------------------------------------                                                                                                                                                                                                                                                                       
class SpriteMaker(QWidget):  
### --------------------------------------------------------        
    def __init__(self):
        super().__init__()
        
        self.setUI()
        self.show()  
         
### --------------------------------------------------------             
    def init(self):
        self.file = ''
        self.key = ''    

        self.pts  = []
        self.npts = 0 
        self.last = QPointF()
 
        self.outline = None 
        self.pixItem  = None
        self.pathColorDot = None
          
        self.outlineSet = False 
        self.slidersSet = False
        self.pathClosed = False
        
        self.helpFlag  = False
        self.helpMenu  = None
       
        self.color  = "lime"                  
        self.rotate = 0.0
        self.scale  = 1.0 
        
        self.btnStyle = None 
        self.loupeWidget = None
                     
### --------------------- event filter ----------------------                
    def eventFilter(self, source, e):          
        if self.outlineSet:  ## used to draw outline      
            if e.type() == QEvent.Type.MouseButtonPress and \
                e.button() == Qt.MouseButton.LeftButton:
                    self.npts = 0  
                    self.addPoints(e.position())
                    self.last = constrainXY(e.position(), 1) 
                                               
            elif e.type() == QEvent.Type.MouseMove and \
                e.buttons() == Qt.MouseButton.LeftButton:
                    self.addPoints(e.position())
                    
            elif e.type() == QEvent.Type.MouseButtonRelease and \
                e.button() == Qt.MouseButton.LeftButton:
                    pt = constrainXY(e.position(), 1)     
                    if self.last != pt:  ## else too many points
                        self.last = pt   
                        self.pts.append(pt)
                    self.updateOutline()     
                              
        elif e.type() == QEvent.Type.MouseButtonDblClick and self.loupeWidget != None:
            self.loupe.closeLoupe()                       
        return QWidget.eventFilter(self, source, e)
    
    def mousePressEvent(self, e):  
        if e.button() == Qt.MouseButton.RightButton:
            if not self.outlineSet: 
                self.works.closeHelpMenu() if self.helpFlag else \
                    self.works.openHelpMenu() 
        else:
            self.works.closeHelpMenu()
        e.accept() 

### --------------------------------------------------------                                                             
    def keyPressEvent(self, e):
        key = e.key()  
        if key in (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape):
            self.bye()   
        elif key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete): 
            self.setKey('del')  ## delete a point   
        elif key == Qt.Key.Key_Alt:
            self.setKey('opt')  ## add a point  
        elif key in (Qt.Key.Key_Space, Qt.Key.Key_Shift):  ## lock magnifier
            self.loupe.holdIt() 
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_Right):
            self.shared('last')
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_Left):
            self.shared('next')  
        else:
            try:
                key = chr(key) 
            except:
                return
            self.shared(key)
                  
    def shared(self, key):  ## from helpMenu and keyboard
        match key:
            case 'X' |'Q': 
                self.bye()   
            case 'F':
                self.works.openFiles() 
            case 'O': 
                self.addOutLine()
            case 'P': 
                self.changePathColor()    
            case 'E': 
                self.works.edit()   
            case 'B':
                self.works.background()
            case 'H':
                self.works.openHelpMenu()
            case 'C':
                self.clear()           
            case 'delete':  ## can vary
                self.setKey('del')  ## delete a point        
            case 'option':
                self.setKey('opt')  ## add a point       
            case 'shift':  ## lock magnifier
                self.loupe.holdIt()    
            case 'next' | 'last':
                if self.loupeWidget != None:
                    self.loupe.nextPoint(key) 
            case 'S':
                self.saveTxy.saveSprite()
        
    def setKey(self, key): 
        self.key = key
       
    def keyReleaseEvent(self,e):  
        self.key = ''
                                                         
### --------------------------------------------------------
    def addPoints(self, pt): 
        if self.npts == 0:
            self.pts.append(pt)
        self.npts += 1
        if self.npts % 5 == 0: 
            self.pointCheck(pt)  ## look for overlaping points     

    def pointCheck(self, pt):  ## make sure points don't go off the screen
        pt = constrainXY(pt, 1)  
        if distance(pt.x(), self.last.x(), pt.y(), self.last.y()) > 15.0:
            self.last = pt     
            self.pts.append(pt)
            self.updateOutline()
        elif distance(pt.x(), self.last.x(), pt.y(), self.last.y()) < 2.5:
            return
   
    def setPathColorDot(self):  ## set path color
        if self.pathColorDot: self.scene.removeItem(dot)
        dot = QGraphicsEllipseItem()
        V = 15.0
        dot.setBrush(QColor(self.color))      
        dot.setRect(700, 700, V, V)  ## right hand corner
        dot.setZValue(300)
        self.scene.addItem(dot)
                                                                               
    def addOutLine(self):
        if self.pathClosed:
            return
        if len(self.pts) == 0 and self.slidersSet and not self.outlineSet:
            self.outlineSet = True
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.setPathColorDot()      
            self.addBtn.setStyleSheet('background-color: rgba(0,125,255,80);')
            self.addBtn.setText("Close Outline")
            
        elif self.outlineSet and not self.pathClosed:      
            self.addBtn.setStyleSheet('background-color: rgba(220,220,220,220);')
            self.closeOutLine()
            self.addBtn.setText("Outline")
            
    def closeOutLine(self):
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))     
        self.outlineSet = False 
        self.pathClosed = True
        self.updateOutline()  ## close it         
        self.redrawPoints(True)  ## True - constrain XY at close
        self.works.editingOn = True     
        self.addBtn.setEnabled(False)
        
    def finalizePixmap(self):  ## the set button in sliders
        if self.pixItem != None:
            self.loupe.removeFrame()
            self.works.replacePixitem() 
            self.sliders.setEnabled(False)
            self.slidersSet = True
            self.addBtn.setEnabled(True)
   
    def changePathColor(self):
        self.loupe.removeFrame()
        self.color = getColorStr()
        self.setPathColorDot()
        self.updateOutline()
        if self.loupeWidget != None:
            self.loupe.loupeit(self.loupe.idx)
            self.removePointItems()
            self.works.editingOn = False

    def updateOutline(self):  ## make a path from pathMaker pts
        self.deleteOutline()
        w = 1.5  
        if self.outlineSet:
            w = 2.5   
        self.outline = QGraphicsPathItem(self.setPaintPath(self.pathClosed))
        self.outline.setPen(QPen(QColor(self.color), w, Qt.PenStyle.SolidLine))
        self.outline.setZValue(100) 
        self.scene.addItem(self.outline)
        self.setPathColorDot()
            
    def deleteOutline(self): 
        if len(self.pts) > 0 and self.outline != None:
            self.scene.removeItem(self.outline)
            self.outline = None
                           
    def setPaintPath(self, bool=False): 
        path = QPainterPath()
        for pt in self.pts: 
            if not path.elementCount():
                path.moveTo(QPointF(pt))
            path.lineTo(QPointF(pt)) 
        if bool: 
            path.closeSubpath()
        return path
                                      
### --------------------------------------------------------  
    def addPointItems(self, final=False):  ## final check using constraints
        idx = 200  ## Zvalues
        for i in range(0, len(self.pts)):  
            if final: self.pts[i] = constrainXY(self.pts[i],1)
            self.scene.addItem(PointItem(self.pts[i], i, idx, self))
            idx += 1
       
    def redrawPoints(self, final=False): 
        if self.works.editingOn:
            self.removePointItems()
        self.addPointItems(final)
    
    def removePointItems(self): 
        for p in self.scene.items():
            if p.zValue() >= 200 and p.type == 'pt':  ## should only be points
                self.scene.removeItem(p)
                                                                                                                                                                                             
### --------------------------------------------------------          
    def setOrigin(self):  
        if self.pixItem:
            b = self.pixItem.boundingRect()
            op = QPointF(b.width()/2, b.height()/2)
            self.pixItem.setTransformOriginPoint(op)
                       
    def center(self):
        x = (ViewW - self.pixItem.width())/2
        y = (ViewH - self.pixItem.height())/2
        self.pixItem.setPos(x, y)
  
    def clear(self):
        self.scene.clear()
        self.init() 
        self.works.init()
        self.loupe.closeWidget()
        self.loupe.init()
          
### -------------------------------------------------------- 
    def enableSliders(self, bool=False): 
        self.rotationSlider.setValue(0)
        self.scaleSlider.setValue(100)
        self.sliders.setEnabled(bool)
                  
    def resetSliders(self):
        self.rotationSlider.setValue(int(self.rotate))
        self.scaleSlider.setValue(int(self.scale*100))  
        
    def setRotation(self, val):
        self.setOrigin()
        if val < 0:
            val= 0
        self.rotate = val
        self.pixItem.setRotation(val)
                                                      
    def Rotation(self, val):
        if self.pixItem != None:
            op = (val)
            self.setRotation(op)
            self.rotationValue.setText(f"{op:.2f}") 
     
    def setScale(self, val):
        self.setOrigin()
        self.scale = val
        self.pixItem.setScale(val)
                                
    def Scale(self, val):
        if self.pixItem:
            op = (val/100)
            self.setScale(op)
            self.scaleValue.setText(f"{op:.2f}") 

    def bye(self):  
        QGuiApplication.restoreOverrideCursor() 
        self.works.closeHelpMenu()
        self.loupe.closeWidget()  
        self.close()

### -------------------------------------------------------- 
    def setUI(self):
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
                      
        ctr = QGuiApplication.primaryScreen().availableGeometry().center()
        x = int(((ctr.x() * 2 ) - Width)/2)
        self.setGeometry(x, 200,Width,Height)
        
        self.setFixedSize(Width,Height)     
        self.setWindowTitle("spriteMaker")
        
        self.scene.setSceneRect(0,0,ViewW,ViewH-2) 
     
        self.setStyleSheet("QGraphicsView {\n"
            "background-color: rgb(250,250,250);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "color: rgb(125,125,125);\n"
            "}")

        self.init()     
                
        self.works = Works(self)
        self.loupe = Loupe(self)
        self.saveTxy = SaveTxy(self)
       
        self.buttons = self.setButtons()
        self.sliders = self.setSliders()
                        
        hbox = QHBoxLayout()            
        hbox.addWidget(self.view) 
        hbox.addWidget(self.sliders) 
                 
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.buttons, Qt.AlignmentFlag.AlignHCenter)
               
        self.setLayout(vbox)
          
        self.view.viewport().installEventFilter(self)  
        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)   
         
        self.enableSliders()  ## default false
        self.addBtn.setDisabled(True)   
    
        self.setMouseTracking(True)
        self.grabKeyboard() 
     
### -------------------------------------------------------- 
    def setSliders(self):
        groupBox = QGroupBox()
        groupBox.setFixedSize(80, ViewH+5)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        groupBox.setStyleSheet("QGroupBox {\n"
            "background-color: rgb(220,220,220);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "}")
        
        self.scaleValue = QLabel("1.00")
        self.scaleSlider = QSlider(Qt.Orientation.Vertical,                   
            minimum=50, maximum=250, singleStep=1, value=100)
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
        
        self.buttonGroup.setStyleSheet("QLabel {\n"
            "background-color: rgb(230,230,230);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "}")
            
        self.setStyleSheet("QPushButton { min-width: 10px; }")
            
        filesBtn = QPushButton("Files")      
        filesBtn.clicked.connect(self.works.openFiles)
                
        self.addBtn = QPushButton("Outline")
        self.addBtn.clicked.connect(self.addOutLine)
  
        changeBtn = QPushButton("Path Color")
        changeBtn.clicked.connect(self.changePathColor)

        backgroundsBtn = QPushButton("Background")
        backgroundsBtn.clicked.connect(self.works.background)

        editBtn = QPushButton("Edit")
        editBtn.clicked.connect(self.works.edit)
        
        helpBtn = QPushButton("Help")
        helpBtn.clicked.connect(self.works.openHelpMenu)
        
        clearBtn = QPushButton("Clear")
        clearBtn.clicked.connect(self.clear)
         
        saveBtn = QPushButton("Save")
        saveBtn.clicked.connect(self.saveTxy.saveSprite)
    
        quitBtn= QPushButton("Quit")
        quitBtn.clicked.connect(self.bye)
        
        hbox = QHBoxLayout(self)
        
        hbox.addWidget(filesBtn)
        hbox.addWidget(self.addBtn)
        hbox.addWidget(changeBtn)
        hbox.addWidget(backgroundsBtn)
        hbox.addWidget(helpBtn)
        hbox.addWidget(editBtn)
        hbox.addWidget(clearBtn)   
        hbox.addWidget(saveBtn)
        hbox.addWidget(quitBtn)
            
        self.buttonGroup.setLayout(hbox)
        
        self.btnStyle = helpBtn.styleSheet() ## works
   
        return self.buttonGroup
              
### -------------------------------------------------------- 
if __name__ == '__main__':
    app = QApplication(sys.argv) 
    boo = SpriteMaker()
    sys.exit(app.exec())

### ------------------- dotsSpriteMaker --------------------


