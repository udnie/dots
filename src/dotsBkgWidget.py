
from PyQt6.QtCore       import Qt, QPoint, QPointF,QRectF
from PyQt6.QtGui        import QColor, QPen, QPainter
from PyQt6.QtWidgets    import QSlider, QWidget, QGroupBox, QDial, QLabel, \
                                QSlider, QHBoxLayout, QVBoxLayout, QPushButton
      
from dotsBkgMatte       import Matte
                      
### ------------------- dotsShadowWidget -------------------                                                                                                                                                            
class BkgWidget(QWidget):  
### -------------------------------------------------------- 
    def __init__(self, parent, maker):
        super().__init__()
                                        
        self.bkgItem  = parent     
        self.bkgMaker = maker
        self.canvas   = self.bkgItem.canvas
           
        self.type = 'widget'
        self.save = QPointF()
                
        self.setAccessibleName('widget')
        self.WidgetW, self.WidgetH = 330.0, 300.0
                    
        vbox = QVBoxLayout()  
          
        hbox = QHBoxLayout()
        hbox.addWidget(self.sliderGroup(), Qt.AlignmentFlag.AlignTop)
        hbox.addSpacing(5) 
        hbox.addWidget(self.buttonGroup(), Qt.AlignmentFlag.AlignTop)
        
        sbox = QHBoxLayout()
        sbox.addWidget(self.scrollButtons(), Qt.AlignmentFlag.AlignBottom)
        vbox.addLayout(hbox)    
        vbox.addLayout(sbox) 
        
        self.setLayout(vbox)
        
        self.setFixedHeight(int(self.WidgetH)) 
        self.setStyleSheet('background-color: rgba(0,0,0,0)')  ## gives you rounded corners
        self.setContentsMargins(0, 0, 0, 0) 
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)             
          
        self.toggleLock()
                                                     
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
        if self.bkgItem:
            if bkgItem.fileName != 'flat':
                self.opacitySlider.setValue(int(bkgItem.opacity*100))
                self.scaleSlider.setValue(int(bkgItem.scale*100))
                self.rotaryDial.setValue(int(bkgItem.rotation))
                self.setLocks()
            
    def setLocks(self):
        if self.bkgItem:  ## shouldn't need this but - could have just started to clear
            if self.bkgItem.locked == False:
                self.lockBtn.setText('UnLocked')
            else:
                self.lockBtn.setText('Locked')
            
    def toggleLock(self):
        if self.bkgItem:  
            if self.bkgItem.locked == False:
                self.bkgMaker.lockBkg()
            else:
                self.bkgMaker.unlockBkg()    
                    
    def setBkgRotate(self, val):
        if self.bkgItem:
            if self.bkgItem.locked == False and self.bkgItem.fileName != 'flat':
                self.bkgItem.setOrigin()  
                if val< 0: val = 0
                self.bkgItem.rotation = val   
                self.bkgItem.setRotation(self.bkgItem.rotation)
                self.rotateValue.setText('{:3d}'.format(val))
            
    def setBkgScale(self, val):
        if self.bkgItem:
            if self.bkgItem.locked == False and self.bkgItem.fileName != 'flat':
                self.bkgItem.setOrigin()
                op = (val/100)
                self.bkgItem.scale = op
                self.bkgItem.setScale(self.bkgItem.scale)
                self.scaleValue.setText('{0:.2f}'.format(op))
   
    def setBkgOpacity(self, val):
        if self.bkgItem:
            if self.bkgItem.locked == False: 
                op = (val/100)
                self.bkgItem.opacity = op    
                self.bkgItem.setOpacity(self.bkgItem.opacity)
                self.opacityValue.setText('{0:.2f}'.format(op))
            
    def centerBkg(self):
        if self.bkgItem:
            if self.bkgItem.fileName != 'flat':  
                width = self.bkgItem.imgFile.width()
                height = self.bkgItem.imgFile.height()
                self.bkgItem.x = (self.bkgItem.ViewW - width)/2
                self.bkgItem.y = (self.bkgItem.ViewH - height)/2
                self.bkgItem.setPos(self.bkgItem.x, self.bkgItem.y) 
                                        
    def setLeft(self):
        if self.bkgItem.scrollable:
            self.bkgMaker.closeWidget() 
            self.bkgItem.setDirection('left')
        else:
            self.bkgItem.notScrollable() 
        
    def setRight(self):
        if self.bkgItem.scrollable:
            self.bkgMaker.closeWidget()  
            self.bkgItem.setDirection('right')  
        else:
            self.bkgItem.notScrollable() 
            
    def setMatte(self):
        self.bkgMaker.closeWidget()
        self.bkgMaker.matte = Matte(self.bkgItem)
                                                               
### -------------------------------------------------------- 
    def sliderGroup(self):
        groupBox = QGroupBox('Rotate     Scale   Opacity   ')
        
        groupBox.setFixedWidth(170)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
   
        self.rotateValue = QLabel('0', alignment=Qt.AlignmentFlag.AlignCenter)
        self.rotaryDial = QDial()
        self.rotaryDial.setMinimum(0)
        self.rotaryDial.setMaximum(360)
        self.rotaryDial.setValue(0)
        self.rotaryDial.setFixedWidth(60)
        self.rotaryDial.setWrapping(False)
        self.rotaryDial.setNotchesVisible(True)
        self.rotaryDial.setNotchTarget(23.0)
        self.rotaryDial.setSingleStep(1)
        self.rotaryDial.valueChanged.connect(self.setBkgRotate)
     
        self.scaleValue = QLabel('1.00')
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
        sbox.addSpacing(-10)         
        sbox.addWidget(self.rotaryDial)  
        sbox.addSpacing(10)       
        sbox.addWidget(self.scaleSlider) 
        sbox.addSpacing(10)                
        sbox.addWidget(self.opacitySlider) 
        
        vabox = QHBoxLayout()  ## values
        vabox.addSpacing(0) 
        vabox.addWidget(self.rotateValue)        
        vabox.addSpacing(10) 
        vabox.addWidget(self.scaleValue)     
        vabox.addSpacing(10) 
        vabox.addWidget(self.opacityValue)  
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
        
        groupBox.setFixedWidth(103)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
      
        saveBtn   = QPushButton('Save')               
        setBtn    = QPushButton('Set')
        self.lockBtn = QPushButton('Locked')
        flopBtn    = QPushButton('Flop')
        matteBtn  = QPushButton('Matte')
        deleteBtn = QPushButton('Delete')
        centerBtn = QPushButton('Center')
        quitBtn   = QPushButton('Close')
        
        saveBtn.clicked.connect(self.bkgMaker.saveBkg)
        setBtn.clicked.connect(self.bkgMaker.setBkg)     
        self.lockBtn.clicked.connect(self.toggleLock)   
        flopBtn.clicked.connect(self.bkgMaker.flopIt)
        matteBtn.clicked.connect(self.setMatte)
        centerBtn.clicked.connect( self.centerBkg)    
        deleteBtn.clicked.connect(self.bkgItem.delete)
        quitBtn.clicked.connect(self.bkgMaker.closeWidget)
    
        vbox = QVBoxLayout(self)
        vbox.addWidget(saveBtn)
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
      
        leftBtn  = QPushButton('Scroll to Left')               
        rightBtn = QPushButton('Scroll to Right')
        
        leftBtn.clicked.connect(self.setLeft)
        rightBtn.clicked.connect(self.setRight)
        
        hbox = QHBoxLayout(self)
        hbox.addWidget(leftBtn)
        hbox.addSpacing(20)
        hbox.addWidget(rightBtn)
        
        groupBox.setLayout(hbox)
        return groupBox
                                                                      
### ------------------- dotsDotsWidget ---------------------
  

