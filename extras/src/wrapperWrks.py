
import time

from PyQt6.QtCore       import Qt, QPoint, QPointF
from PyQt6.QtGui        import QImage, QPixmap, QPen, QColor                 
from PyQt6.QtWidgets    import QLabel, QGraphicsPixmapItem, QGroupBox,  QHBoxLayout, \
                                QPushButton, QSlider, QGroupBox, QSlider, QLabel, \
                                QHBoxLayout,  QVBoxLayout, QGraphicsLineItem, \
                                QGraphicsEllipseItem
                                
ViewW, ViewH = 1080, 720
BtnsW, Max = ViewW, 200   
### --------------------------------------------------------
class BasicBkg(QGraphicsPixmapItem):  
### --------------------------------------------------------
    def __init__(self, parent, file):
        super().__init__()

        self.parent = parent   
        self.fileName = file
         
        self.initX = 0
        self.dragAnchor = QPoint()
   
    def mousePressEvent(self, e): 
        self.initX = self.pos().x()
        self.dragAnchor = self.mapToScene(e.pos())
        e.accept()
   
    def mouseMoveEvent(self, e):
        if self.parent.guidesOn:
            return
        self.updateXY(self.mapToScene(e.pos()))
        self.setPos(self.x, 0)
        e.accept() 
    
    def updateXY(self, pos):
        dragX = pos.x() - self.dragAnchor.x() 
        self.x = self.initX + dragX
   
### --------------------------------------------------------
class BkgItem(BasicBkg):  
### --------------------------------------------------------
    def __init__(self, parent, file, side=''):
        super().__init__(parent, file)
        
        self.parent = parent
        
        img = QImage(file)       
        img = img.scaledToHeight(ViewH,  
            Qt.TransformationMode.SmoothTransformation)

        self.imgFile = img   
        self.side = side
        
        self.x = 0 
        self.y = 0
     
        self.setPixmap(QPixmap.fromImage(self.imgFile))   
        
        if self.side == 'bkg':
            self.setPos(-1,0)
        elif self.side == 'blended':
            self.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsMovable)
        else:
            self.setLeft() if self.side == 'left' else self.setRight()

    def setLeft(self):
        self.start = int((ViewW/2)- self.imgFile.width())  
        self.setPos(self.start, 0)
      
    def setRight(self):
        self.start = int(ViewW/2) 
        self.setPos(self.start, 0)
   
### --------------------------------------------------------
class Handle(QGraphicsEllipseItem):  ## google query
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__(-10, -5, 20, 20, parent)  ## setting claude
        
        self.setBrush(QColor('coral'))
        self.setPen(QColor('coral'))

        self.setFlags(self.GraphicsItemFlag.ItemIsMovable | 
            self.GraphicsItemFlag.ItemSendsScenePositionChanges)

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemPositionChange:
            value.setY(ViewH // 2)  ## claude
            clamped = self.parentItem().clampedX(value)  # set clamped 
            value.setX(clamped)
            self.parentItem().updateCropGuide(value)
        return super().itemChange(change, value)  # now value is clamped
                                                                                
### --------------------------------------------------------
class Guide(QGraphicsLineItem):
### --------------------------------------------------------
    def __init__(self, parent, x1, y1, x2, y2, code):
        super().__init__()
             
        self.parent = parent
        self.code = code
        self.handle = None
        
        self.initX = 0
        self.dragAnchor = QPoint()
        
        self.setLine(x1, y1, x2, y2)

        if code == 'vu2':
            pen = QPen(QColor("yellow"))
            pen.setWidth(2)   
             
        elif code == 'ctr':
            pen = QPen(QColor("dodgerblue"))
            pen.setWidth(3) 
            
        elif code == 'end':
            pen = QPen(QColor("cyan"))
            pen.setWidth(2)   
            
        else:  ## crop
            self.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsMovable)
            pen = QPen(QColor("coral"))
            pen.setWidth(5)
            
        pen.setStyle(Qt.PenStyle.SolidLine) 
        self.setPen(pen)    
           
        self.setZValue(400)      
     
        if code == 'crop':   
            self.handle = Handle(self)
            self.handle.setPos(x1, ViewH//2)
              
### -------------------------------------------------------- 
    def mousePressEvent(self, e): 
        if self.code == 'crop':
            self.initX = self.pos().x()
            self.dragAnchor = self.mapToScene(e.pos())
            e.accept()
        
    def mouseMoveEvent(self, e):
        if self.code == 'crop':
            p = self.mapToScene(e.pos())
            self.updateXY(p)
            self.setPos(self.x, 0)
            self.parent.setNewSlice(p.x())
            e.accept()
   
    def updateXY(self, pos):
        dragX = pos.x() - self.dragAnchor.x() 
        self.x = self.initX + dragX
        
    def clampedX(self, pos): 
        if self.code == 'crop':
            ns = int(ViewW//2 ) - abs(int(pos.x()))- self.parent.blendWidth//2 
            if ns < 0:
                limit = int(ViewW//2) - self.parent.blendWidth//2  ## claude
                return limit  
            return pos.x()

    def updateCropGuide(self, pos):  ## claude
        if self.code == 'crop':
            self.setLine(pos.x(), 0, pos.x(), ViewH)
            self.parent.setNewSlice(pos.x())
                             
### ------------------------ Works -------------------------                                                                                                                                                                                                                                                                           
class Works:  
### --------------------------------------------------------       
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.scene  = parent.scene
  
### --------------------------------------------------------
    def addGuides(self): 
        if self.parent.blended != None:
            save = self.parent.newSlice
            self.deleteGuides()  
            vu2 = ViewW//2  ## screen not blended
            self.parent.newSlice = save 
            
            for code in ['vu2','ctr','end','crop']:
                match code:
                    case 'vu2':
                        self.guide = Guide(self.parent, vu2, 0, vu2, ViewH, code)
                    case'ctr':   
                        h = self.parent.blendWidth//2
                        self.guide = Guide(self.parent, vu2-h, 0, vu2-h, ViewH, code) 
                    case'end':
                        w = self.parent.blendWidth
                        self.guide = Guide(self.parent, vu2-w, 0, vu2-w, ViewH, code) 
                    case'crop': 
                        n = self.parent.newSlice 
                        self.guide = Guide(self.parent, vu2-n, 0, vu2-n, ViewH, code) 
                try:
                    self.parent.scene.addItem(self.guide)
                except:
                    self.msgbox('Error: adding Guides') 
                    return False   
                                     
            self.parent.guidesOn = True
            time.sleep(.02)
            return True
    
    def deleteGuides(self):
        for p in self.parent.scene.items():
            if isinstance(p, QGraphicsLineItem):
                self.scene.removeItem(p)
                del p
        self.parent.guidesOn = False
        time.sleep(.02)

    def enableSliders(self, bool=False): 
        self.parent.sliders.setEnabled(bool)
        self.blendSlider.setEnabled(bool)
        self.rightAlphaSlider.setValue(50)
        self.leftAlphaSlider.setValue(50)
        self.blendSlider.setValue(0)   
        self.blendSlider.setSliderPosition(0)
              
    def updateGuides(self):
        vu2 = ViewW//2
        for p in self.parent.scene.items():
            if isinstance(p, QGraphicsLineItem):
                if p.code == 'ctr':   
                    h = self.parent.blendWidth//2
                    p.setLine(float(vu2-h), 0, float(vu2-h),  ViewH)
                elif p.code == 'end':
                    w = self.parent.blendWidth
                    p.setLine(float(vu2-w), 0, float(vu2-w),  ViewH)
                elif p.code == 'crop': 
                    n = self.parent.newSlice 
                    p.setLine(float(vu2-n), 0, float(vu2-n),  ViewH)
       
### --------------------------------------------------------
    ''' Thought that I might use of the right/left sliders but
        what I was trying to do didn't work and decided to leave
        them incase something turns up that could make use of the two. '''
### --------------------------------------------------------
    def setSliders(self):
        groupBox = QGroupBox()
        groupBox.setFixedSize(85,ViewH+73)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        groupBox.setStyleSheet("QGroupBox {\n"
            "background-color: rgb(220,220,220);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "}")
        
### ----------------------- rightAlpha ---------------------
        self.rightAlphaValue = QLabel("1.0")
        self.rightAlphaSlider = QSlider(Qt.Orientation.Vertical,                   
            minimum=0, maximum=100, singleStep=1, value=50)
        self.rightAlphaSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.rightAlphaSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.rightAlphaSlider.setTickInterval(10)  
        self.rightAlphaSlider.setFixedSize(50,275)
        self.rightAlphaSlider.valueChanged.connect(self.parent.setRightAlpha)
        self.rightAlphaSlider.setStyleSheet("QSlider {\n"
            "background-color: rgb(240,240,240);\n"
            "}")
       
        abox = QVBoxLayout() 
        abox.addWidget(QLabel("rightAlpha", alignment=Qt.AlignmentFlag.AlignCenter))    
        self.rightAlphalabel = QLabel("0.0")  
        abox.addSpacing(-5)
        abox.addWidget(self.rightAlphalabel,alignment=Qt.AlignmentFlag.AlignCenter)             
        abox.addWidget(self.rightAlphaSlider)
        abox.addWidget(self.rightAlphaValue, alignment=Qt.AlignmentFlag.AlignCenter| \
            Qt.AlignmentFlag.AlignBottom) 
    
### ----------------------- leftAlpha ---------------------- 
        self.leftAlphaValue = QLabel("1.0")
        self.leftAlphaSlider = QSlider(Qt.Orientation.Vertical,                   
            minimum=0, maximum=100, singleStep=1, value=50)
        self.leftAlphaSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.leftAlphaSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.leftAlphaSlider.setTickInterval(10)  
        self.leftAlphaSlider.setFixedSize(50,275)
        self.leftAlphaSlider.valueChanged.connect(self.parent.setLeftAlpha)
        self.leftAlphaSlider.setStyleSheet("QSlider {\n"
            "background-color: rgb(240,240,240);\n"
            "}")
      
        gbox = QVBoxLayout() 
        gbox.addWidget(QLabel("leftAlpha", alignment=Qt.AlignmentFlag.AlignCenter))
        self.leftAlphalabel = QLabel("0.0")  
        gbox.addSpacing(-5)
        gbox.addWidget(self.leftAlphalabel,alignment=Qt.AlignmentFlag.AlignCenter)  
        gbox.addWidget(self.leftAlphaSlider)
        gbox.addSpacing(-5)
        gbox.addWidget(self.leftAlphaValue, alignment=Qt.AlignmentFlag.AlignCenter| \
            Qt.AlignmentFlag.AlignBottom)  
     
        self.setBtn = QPushButton("Set") 
        # self.setBtn.clicked.connect(self.parent.bye)     
       
        vbox = QVBoxLayout()  
        vbox.addLayout(abox)
        vbox.addSpacing(14)
        vbox.addLayout(gbox)
        vbox.addWidget(self.setBtn)
        
        groupBox.setLayout(vbox)
        
        return groupBox      
                                         
### --------------------------------------------------------    
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedSize(BtnsW,55)
        self.buttonGroup.setStyleSheet("QLabel {\n"
            "background-color: rgb(220,220,220);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "}")
        
        filesBtn  = QPushButton("Files")      
        alignBtn = QPushButton("Align")
        newBtn   = QPushButton('Guides') 
        self.swapBtn = QPushButton('Swap')
        delBtn   = QPushButton('Delete Blended')     
        saveBtn  = QPushButton('Save')
        clearBtn = QPushButton("Clear")
        quitBtn  = QPushButton("Quit")
        
        filesBtn.clicked.connect(self.parent.openFiles)
        alignBtn.clicked.connect(self.parent.align)
        newBtn.clicked.connect(self.parent.toggleGuides)
        self.swapBtn.clicked.connect(self.parent.swap)
        delBtn.clicked.connect(self.parent.deleteBlended)
        saveBtn.clicked.connect(self.parent.saveDialog)
        clearBtn.clicked.connect(self.parent.clear)
        quitBtn.clicked.connect(self.parent.bye)
        
        hbox = QHBoxLayout(self.parent)
        
        hbox.addWidget(filesBtn)
        hbox.addWidget(alignBtn)
        hbox.addWidget(newBtn)   
        hbox.addWidget(self.swapBtn)
        hbox.addWidget(delBtn)       
        hbox.addWidget(saveBtn)
        hbox.addWidget(clearBtn)   
        hbox.addWidget(quitBtn)
            
        self.buttonGroup.setLayout(hbox)
  
        return self.buttonGroup
    
### -------------------------- blend -----------------------          
    def setBlendSlider(self):
        groupBox = QGroupBox()
        groupBox.setFixedSize(835,70)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        groupBox.setStyleSheet("QGroupBox {\n"
            "background-color: rgb(220,220,220);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "}")
      
        self.blendSlider = QSlider(Qt.Orientation.Horizontal,                   
            minimum=-0, maximum=200, singleStep=1, value=0)
        self.blendSlider.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.blendSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.blendSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.blendSlider.setTickInterval(10)  
        self.blendSlider.setPageStep(50)
        self.blendSlider.setFixedSize(600,40)
        self.blendSlider.valueChanged.connect(self.parent.setBlendVal)
                          
        style = """ QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #e4e4e4, stop:1 #4f4f4f);
            border: 1px solid rgb(115,115,115);
            width: 11px;
            margin: -7px 0;
            border-radius: 3px;
            }
            QSlider {
                background: rgb(245,245,245);
            } 
            QSlider::horizontal {
                margin-left: -25px;
                margin-right: -20px;
            }
            QSlider::tick-mark {
                color: black;
                background-color: black;
                width: 1px;
            } """
                                       
        self.blendSlider.setStyleSheet(style)                        

        bbox = QHBoxLayout() 
        bbox.addSpacing(10)
        self.blendlabel = QLabel("")  
        bbox.addWidget(self.blendlabel,alignment=Qt.AlignmentFlag.AlignCenter) 
        bbox.addSpacing(15)
        bbox.addWidget(self.blendSlider)
        bbox.addSpacing(20)
        groupBox.setLayout(bbox)
        
        return groupBox

### --------------------- that's all -----------------------




