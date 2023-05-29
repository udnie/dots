
from PyQt6.QtCore       import Qt, QPoint, QPointF,QRectF
from PyQt6.QtGui        import QColor, QPen, QPainter, QPixmap
from PyQt6.QtWidgets    import QSlider, QWidget, QGroupBox, QDial, QLabel, \
                                QGraphicsPixmapItem ,QSlider, QHBoxLayout,  \
                                QVBoxLayout, QPushButton, QGraphicsItem
    
from dotsShared         import common
                    
### ------------------- dotsDotsWidget ---------------------
''' classes:  Flat, BkgWidget '''                                                                                                              
### --------------------------------------------------------
class Flat(QGraphicsPixmapItem):
### --------------------------------------------------------   
    def __init__(self, color, canvas, z=common['bkgZ']):
        super().__init__()

        self.canvas   = canvas
        self.scene    = canvas.scene
        self.bkgMaker = self.canvas.bkgMaker
        
        self.type = 'bkg'
        self.color = color
        
        self.fileName = 'flat'
        self.locked = False
        
        self.tag = ''
        self.id = 0   

        p = QPixmap(common['ViewW'],common['ViewH'])
        p.fill(self.color)
        
        self.setPixmap(p)
        self.setZValue(z)
   
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        
### --------------------------------------------------------
    def mousePressEvent(self, e):      
        if not self.canvas.pathMakerOn:
            if e.button() == Qt.MouseButton.RightButton:    
                self.bkgMaker.addWidget(self)        
            elif self.canvas.key == 'del':     
                self.delete()
            elif self.canvas.key == '/':  ## to back
                self.bkgMaker.back(self)
            elif self.canvas.key in ('enter','return'):  
                self.bkgMaker.front(self)                             
        e.accept()
      
    def mouseReleaseEvent(self, e):
        if not self.canvas.pathMakerOn:
            self.canvas.key = ''       
        e.accept()
     
    def delete(self):  ## also called by widget
        self.bkgMaker.deleteBkg(self)
      
### --------------------------------------------------------        
class BkgWidget(QWidget):  
### -------------------------------------------------------- 
    def __init__(self, parent, maker):
        super().__init__()
                                        
        self.bkgItem  = parent     
        self.bkgMaker = maker
        
        self.type = 'widget'
        self.save = QPointF(0,0)
                
        self.setAccessibleName('widget')
        self.WidgetW, self.WidgetH = 330.0, 215.0
                   
        hbox = QHBoxLayout()
        hbox.addWidget(self.sliderGroup(), Qt.AlignmentFlag.AlignBottom)
        hbox.addSpacing(5) 
        hbox.addWidget(self.buttonGroup(), Qt.AlignmentFlag.AlignBottom)
        self.setLayout(hbox)
        
        self.setFixedHeight(int(self.WidgetH))  
        self.setStyleSheet('background-color: rgba(0,0,0,0)')
        self.setContentsMargins(0,15,0,-15) 
        
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
        if bkgItem and bkgItem.fileName != 'flat':
            self.opacitySlider.setValue(int(bkgItem.opacity*100))
            self.scaleSlider.setValue(int(bkgItem.scale*100))
            self.rotaryDial.setValue(int(bkgItem.rotation))
            self.setLocks()
            
    def setLocks(self):
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
        if self.bkgItem and self.bkgItem.locked == False and self.bkgItem.fileName != 'flat':
            self.bkgItem.setOrigin()  
            if val< 0: val = 0
            self.bkgItem.rotation = val   
            self.bkgItem.setRotation(self.bkgItem.rotation)
            self.rotateValue.setText('{:3d}'.format(val))
            
    def setBkgScale(self, val):
        if self.bkgItem and self.bkgItem.locked == False and self.bkgItem.fileName != 'flat':
            self.bkgItem.setOrigin()
            op = (val/100)
            self.bkgItem.scale = op
            self.bkgItem.setScale(self.bkgItem.scale)
            self.scaleValue.setText('{0:.2f}'.format(op))
   
    def setBkgOpacity(self, val):
        if self.bkgItem and self.bkgItem.locked == False: 
            op = (val/100)
            self.bkgItem.opacity = op    
            self.bkgItem.setOpacity(self.bkgItem.opacity)
            self.opacityValue.setText('{0:.2f}'.format(op))
            
    def centerBkg(self):
        if self.bkgItem and self.bkgItem.fileName != 'flat':  
            width = self.bkgItem.imgFile.width()
            height = self.bkgItem.imgFile.height()
            self.bkgItem.x = (self.bkgItem.ViewW - width)/2
            self.bkgItem.y = (self.bkgItem.ViewH - height)/2
            self.bkgItem.setPos(self.bkgItem.x, self.bkgItem.y) 
                                
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
        colorBtn  = QPushButton('Color')
        flopBtn    = QPushButton('Flop')
        deleteBtn = QPushButton('Delete')
        centerBtn = QPushButton('Center')
        quitBtn   = QPushButton('Close')
        
        saveBtn.clicked.connect(self.bkgMaker.saveBkg)
        setBtn.clicked.connect(self.bkgMaker.setBkg)     
        self.lockBtn.clicked.connect(self.toggleLock)   
        colorBtn.clicked.connect(self.bkgMaker.bkgColor)
        flopBtn.clicked.connect(self.bkgMaker.flopIt)
        centerBtn.clicked.connect( self.centerBkg)    
        deleteBtn.clicked.connect(self.bkgItem.delete)
        quitBtn.clicked.connect(self.bkgMaker.closeWidget)
    
        vbox = QVBoxLayout(self)
        vbox.addWidget(saveBtn)
        vbox.addWidget(setBtn)
        vbox.addWidget(self.lockBtn)
        vbox.addWidget(colorBtn)
        vbox.addWidget(flopBtn)
        vbox.addWidget(deleteBtn)
        vbox.addWidget(centerBtn)
        vbox.addWidget(quitBtn)
                
        groupBox.setLayout(vbox)
        return groupBox
                         
### ------------------- dotsDotsWidget ---------------------
  

