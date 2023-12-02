
from PyQt6.QtCore       import Qt, QPoint, QPointF,QRectF
from PyQt6.QtGui        import QColor, QPen, QPainter
from PyQt6.QtWidgets    import QSlider, QWidget, QGroupBox, QDial, QLabel, \
                                QSlider, QHBoxLayout, QVBoxLayout, QPushButton
                                
from dotsBkgWorks       import BkgWorks
                      
### ------------------- dotsShadowWidget -------------------                                                                                                                                                            
class BkgWidget(QWidget):  
### -------------------------------------------------------- 
    def __init__(self, parent, maker):
        super().__init__()
                                        
        self.bkgItem  = parent     
        self.bkgMaker = maker
        self.canvas   = self.bkgItem.canvas
        
        self.bkgWorks = BkgWorks(self.bkgItem)
           
        self.type = 'widget'
        self.save = QPointF()
                
        self.setAccessibleName('widget')
        self.WidgetW, self.WidgetH = 355.0, 305.0
                    
        vbox = QVBoxLayout()  
          
        hbox = QHBoxLayout()
        hbox.addWidget(self.dialGroup(), Qt.AlignmentFlag.AlignTop)
        hbox.addSpacing(-5)
        hbox.addWidget(self.sliderGroup(), Qt.AlignmentFlag.AlignTop)
        hbox.addSpacing(-5) 
        hbox.addWidget(self.buttonGroup(), Qt.AlignmentFlag.AlignTop)
        
        sbox = QHBoxLayout()
        sbox.addWidget(self.scrollButtons(), Qt.AlignmentFlag.AlignBottom)
        vbox.addLayout(hbox)    
        vbox.addLayout(sbox) 
        
        self.setLayout(vbox)
        
        self.setFixedHeight(int(self.WidgetH)) 
        self.setStyleSheet('background-color: rgba(0,0,0,0)')  ## gives you rounded corners
        self.setContentsMargins(-5, 0, 0, 0) 
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)             
                                                                
        self.show()
                   
### --------------------------------------------------------                    
    def paintEvent(self, e): 
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)        
        rect = QRectF(2, 2, self.WidgetW-4, self.WidgetH-4)
        painter.setPen(QPen(QColor(104,255,204), 5, Qt.PenStyle.SolidLine,  ## border
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)) 
        painter.setBrush(QColor(175,175,175))  ## grayish
        painter.drawRoundedRect(rect, 15, 15)
              
    def mousePressEvent(self, e):
        self.save = e.globalPosition()  ## works the best, needs to change for PyQt6
        e.accept()

    def mouseMoveEvent(self, e):
        self.moveThis(e)
        e.accept()
        
    def mouseReleaseEvent(self, e):
        self.moveThis(e)
        e.accept()
            
    def moveThis(self, e):
        dif = e.globalPosition() - self.save         
        self.move(self.pos() + QPoint(int(dif.x()), int(dif.y())) )
        self.save = e.globalPosition()
            
    def mouseDoubleClickEvent(self, e):
        self.bkgMaker.closeWidget()
        e.accept()
 
### --------------------------------------------------------   
    def resetSliders(self, bkgItem):
        if self.bkgItem != None and bkgItem.fileName != 'flat':
                    
            self.opacitySlider.setValue(int(bkgItem.opacity*100))
            self.opacityValue.setText('{0:.2f}'.format(bkgItem.opacity))
            
            self.scaleSlider.setValue(int(bkgItem.scale*100))
            self.scaleValue.setText('{0:.2f}'.format(bkgItem.scale))
            
            self.rotaryDial.setValue(int(bkgItem.rotation))
            self.rotateValue.setText('{:3d}'.format(bkgItem.rotation))
            
            self.factorDial.setValue(int(bkgItem.factor*100))
            self.factorValue.setText('{0:.2f}'.format(bkgItem.factor))
            
            self.bkgWorks.setMirrorBtnText()
            self.bkgWorks.setBtns()
            self.setLocks()
  
    def setLocks(self):
        if self.bkgItem:  ## shouldn't need this but - could have just started to clear
            if self.bkgItem.locked == False:
                self.lockBtn.setText('UnLocked')
            else:
                self.lockBtn.setText('Locked')
                                   
    def setBkgFactor(self, val):
        if self.bkgItem != None and self.bkgItem.fileName != 'flat':
            self.bkgItem.factor = val/100
            self.factorValue.setText('{0:.2f}'.format(val/100))
            self.bkgWorks.setFactor()
              
    def setBkgRotate(self, val):
        if self.bkgItem != None and self.bkgItem.fileName != 'flat':
            self.bkgItem.setOrigin()  
            if val< 0: val = 0
            self.bkgItem.rotation = val   
            self.bkgItem.setRotation(self.bkgItem.rotation)
            self.rotateValue.setText('{:3d}'.format(val))
            
    def setBkgScale(self, val):
        if self.bkgItem != None and self.bkgItem.fileName != 'flat':       
            self.bkgItem.setOrigin()
            op = (val/100)
            self.bkgItem.scale = op
            self.bkgItem.setScale(self.bkgItem.scale)
            self.scaleValue.setText('{0:.2f}'.format(op))
   
    def setBkgOpacity(self, val):
        if self.bkgItem != None and self.bkgItem.fileName != 'flat':
            op = (val/100)
            self.bkgItem.opacity = op    
            self.bkgItem.setOpacity(self.bkgItem.opacity)
            self.opacityValue.setText('{0:.2f}'.format(op))
                                                                                                                   
### -------------------------------------------------------- 
    def dialGroup(self):
        groupBox = QGroupBox('Rotate')
        
        groupBox.setFixedWidth(75)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
   
        self.rotateValue = QLabel('0', alignment=Qt.AlignmentFlag.AlignCenter)
        self.rotateValue.setFixedWidth(50)
        self.rotaryDial = QDial()
        self.rotaryDial.setFixedWidth(50)
        self.rotaryDial.setMinimum(0)
        self.rotaryDial.setMaximum(360)
        self.rotaryDial.setValue(0)
        self.rotaryDial.setWrapping(False)
        self.rotaryDial.setNotchesVisible(True)
        self.rotaryDial.setNotchTarget(23.0)
        self.rotaryDial.setSingleStep(1)
        self.rotaryDial.valueChanged.connect(self.setBkgRotate)
     
        self.factorValue = QLabel('1.00', alignment=Qt.AlignmentFlag.AlignCenter)
        self.factorValue.setFixedWidth(50)
        self.factorDial = QDial()
        self.factorDial.setFixedWidth(50)
        self.factorDial.setMinimum(50)
        self.factorDial.setMaximum(150)
        self.factorDial.setValue(100)
        self.factorDial.setWrapping(False)
        self.factorDial.setNotchesVisible(True)
        self.factorDial.setNotchTarget(5)
        self.factorDial.setSingleStep(10)
        self.factorDial.valueChanged.connect(self.setBkgFactor)
        
        rbox = QVBoxLayout()    
        rbox.addWidget(self.rotaryDial, Qt.AlignmentFlag.AlignLeft) 
        rbox.addWidget(self.rotateValue, Qt.AlignmentFlag.AlignCenter) 
            
        rbox.addWidget(self.factorDial, Qt.AlignmentFlag.AlignLeft)    
        rbox.addWidget(self.factorValue, Qt.AlignmentFlag.AlignCenter)
        
        rbox.addSpacing(5)
        fact = QLabel('  Factor')
        fact.setFixedWidth(50)
        rbox.addWidget(fact, Qt.AlignmentFlag.AlignHCenter)
               
        groupBox.setLayout(rbox)
        return groupBox

### -------------------------------------------------------- 
    def sliderGroup(self):
        groupBox = QGroupBox('Scale  Opacity  ')
        
        groupBox.setFixedWidth(105)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')

        self.scaleValue = QLabel('1.00')
        self.scaleValue.setFixedWidth(50)
        self.scaleSlider = QSlider(Qt.Orientation.Vertical)
        self.scaleSlider.setMinimum(25)
        self.scaleSlider.setMaximum(225)
        self.scaleSlider.setSingleStep(1)
        self.scaleSlider.setValue(100)
        self.scaleSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scaleSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.scaleSlider.setTickInterval(25)  
        self.scaleSlider.valueChanged.connect(self.setBkgScale)   
        
        self.opacityValue = QLabel('1.00')
        self.opacityValue.setFixedWidth(50)
        self.opacitySlider = QSlider(Qt.Orientation.Vertical)
        self.opacitySlider.setMinimum(0)
        self.opacitySlider.setMaximum(100)
        self.opacitySlider.setSingleStep(1)
        self.opacitySlider.setValue(100)
        self.opacitySlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.opacitySlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.opacitySlider.setTickInterval(16)  
        self.opacitySlider.valueChanged.connect(self.setBkgOpacity)
                       
        sbox = QHBoxLayout()  ## sliders      
        sbox.addWidget(self.scaleSlider, Qt.AlignmentFlag.AlignRight)                
        sbox.addWidget(self.opacitySlider, Qt.AlignmentFlag.AlignRight)
        
        vabox = QHBoxLayout()  ## values
        vabox.addWidget(self.scaleValue, Qt.AlignmentFlag.AlignRight)     
        vabox.addWidget(self.opacityValue, Qt.AlignmentFlag.AlignRight) 
        vabox.setAlignment(Qt.AlignmentFlag.AlignBottom)
         
        vbox = QVBoxLayout() 
        vbox.addLayout(sbox)
        vbox.addLayout(vabox)
                
        groupBox.setLayout(vbox)
        return groupBox
    
### -------------------------------------------------------- 
    def buttonGroup(self):
        groupBox = QGroupBox('BackGrounds  ')
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        groupBox.setFixedWidth(110)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
      
        resetBtn   = QPushButton('Reset')               
        setBtn    = QPushButton('Run')
        self.lockBtn = QPushButton('Locked')
        flopBtn    = QPushButton('Flop')
        matteBtn  = QPushButton('Matte')
        deleteBtn = QPushButton('Delete')
        centerBtn = QPushButton('Center')
        quitBtn   = QPushButton('Close')
        
        resetBtn.clicked.connect(self.bkgWorks.reset)
        setBtn.clicked.connect(self.bkgMaker.showtime)     
        self.lockBtn.clicked.connect(self.bkgWorks.toggleBkgLock)   
        flopBtn.clicked.connect(self.bkgMaker.flopIt)
        matteBtn.clicked.connect(self.bkgWorks.setMatte)
        centerBtn.clicked.connect( self.bkgWorks.centerBkg)    
        deleteBtn.clicked.connect(self.bkgItem.delete)
        quitBtn.clicked.connect(self.bkgMaker.closeWidget)
    
        vbox = QVBoxLayout(self)
        vbox.addWidget(resetBtn)
        vbox.addWidget(setBtn)
        vbox.addWidget(self.lockBtn)
        vbox.addWidget(flopBtn)
        vbox.addWidget(matteBtn)
        vbox.addWidget(deleteBtn)
        vbox.addWidget(centerBtn)
        vbox.addWidget(quitBtn)
                
        groupBox.setLayout(vbox)
        return groupBox
                         
    def scrollButtons(self):
        groupBox = QLabel()
        groupBox.setAlignment(Qt.AlignmentFlag.AlignBaseline) 
        
        groupBox.setFixedHeight(40)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
      
        self.mirrorBtn = QPushButton('Mirroring Off')
        self.leftBtn   = QPushButton('Right to Left')               
        self.rightBtn  = QPushButton('Left to Right')
        
        self.mirrorBtn.clicked.connect(self.bkgWorks.setMirroring)
        self.leftBtn.clicked.connect(self.bkgWorks.setLeft)
        self.rightBtn.clicked.connect(self.bkgWorks.setRight)
        
        hbox = QHBoxLayout(self)
        hbox.addSpacing(-5)       
        hbox.addWidget(self.mirrorBtn)
        hbox.addSpacing(-5)  
        hbox.addWidget(self.rightBtn)
        hbox.addSpacing(-5) 
        hbox.addWidget(self.leftBtn)
        hbox.addSpacing(-5) 
        
        groupBox.setLayout(hbox)
        return groupBox
                                                                      
### ------------------- dotsDotsWidget ---------------------
  



