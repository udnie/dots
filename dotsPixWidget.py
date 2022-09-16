
from PyQt6.QtCore       import Qt, QPoint, QRectF
from PyQt6.QtGui        import QColor, QPen, QPainter
from PyQt6.QtWidgets    import QSlider, QWidget, QGroupBox, QDial, \
                               QLabel, QSlider, QHBoxLayout,  QVBoxLayout, QPushButton
                                                 
### -------------------- dotsPixWidget ---------------------
''' classes: pixWidget '''
### --------------------------------------------------------        
class PixWidget(QWidget):  
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()
                                        
        self.pix = parent
        
        self.type = 'widget'
        self.save = QPoint(0,0)
                
        self.setAccessibleName('widget')
                   
        hbox = QHBoxLayout()
        hbox.addWidget(self.sliderGroup(), Qt.AlignmentFlag.AlignBottom)
        hbox.addSpacing(5) 
        hbox.addWidget(self.buttonGroup(), Qt.AlignmentFlag.AlignBottom)
        self.setLayout(hbox)
        
        self.setFixedHeight(int(self.pix.WidgetH))  
        self.setStyleSheet("background-color: rgba(0,0,0,0)")
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
        rect = QRectF(2, 2, self.pix.WidgetW-4, self.pix.WidgetH-4)
        painter.setPen(QPen(QColor(0,125,255), 5, Qt.PenStyle.SolidLine, 
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)) 
        painter.setBrush(QColor(255,255,0,255))  ## yellow 
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
        self.pix.closeWidget()
        e.accept()
                        
### -------------------------------------------------------- 
    def sliderGroup(self):
        groupBox = QGroupBox("Rotate     Scale   Opacity   ")
        
        groupBox.setFixedWidth(170)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        groupBox.setStyleSheet("background: rgb(245, 245, 245)")
   
        self.rotateValue = QLabel("0", alignment=Qt.AlignmentFlag.AlignCenter)
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
        self.scaleSlider = QSlider(Qt.Orientation.Vertical)
        self.scaleSlider.setMinimum(25)
        self.scaleSlider.setMaximum(225)
        self.scaleSlider.setSingleStep(1)
        self.scaleSlider.setValue(100)
        self.scaleSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scaleSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.scaleSlider.setTickInterval(25)  
        self.scaleSlider.valueChanged.connect(self.Scale)   
        
        self.opacityValue = QLabel("1.00")
        self.opacitySlider = QSlider(Qt.Orientation.Vertical)
        self.opacitySlider.setMinimum(0)
        self.opacitySlider.setMaximum(100)
        self.opacitySlider.setSingleStep(1)
        self.opacitySlider.setValue(100)
        self.opacitySlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
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
                     
        shadowBtn = QPushButton("Shadow")
        flopBtn    = QPushButton("Flop")
        cloneBtn  = QPushButton("Clone")
        delBtn    = QPushButton("Delete")
        lockBtn   = QPushButton("Un/Lock")
        quitBtn   = QPushButton("Close")
    
        shadowBtn.clicked.connect(self.pix.addShadow)
        flopBtn.clicked.connect(self.pix.flopIt)
        cloneBtn.clicked.connect(self.pix.cloneThis)
        delBtn.clicked.connect(self.pix.deletePix)
        lockBtn.clicked.connect(self.pix.togglelock)
        quitBtn.clicked.connect(self.pix.closeWidget)
    
        vbox = QVBoxLayout(self)
        vbox.addWidget(shadowBtn)
        vbox.addWidget(flopBtn)
        vbox.addWidget(cloneBtn)
        vbox.addWidget(delBtn)
        vbox.addWidget(lockBtn)
        vbox.addWidget(quitBtn)
                
        groupBox.setLayout(vbox)
        return groupBox

    def Rotate(self, val): 
        self.pix.setOriginPt() 
        self.pix.setRotation(val) 
        self.pix.rotation = val    
        self.rotateValue.setText("{:3d}".format(val))
    
    def Opacity(self, val):
        op = (val/100)
        self.pix.setOpacity(op)
        self.pix.alpha2 = op
        self.opacityValue.setText("{0:.2f}".format(op)) 
        
    def Scale(self,val):
        self.pix.setOriginPt() 
        op = (val/100)
        self.pix.setScale(op)
        self.pix.scale = op
        self.scaleValue.setText("{0:.2f}".format(op))
                                                                                   
### -------------------- dotsPixWidget ---------------------

