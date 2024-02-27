
import os.path
from posix import lchown

from PyQt6.QtCore       import Qt, QPoint, QRectF, QPointF
from PyQt6.QtGui        import QColor, QPen, QPainter, QPen
from PyQt6.QtWidgets    import QSlider, QWidget, QGroupBox, QDial, QLabel, \
                               QHBoxLayout, QVBoxLayout, QPushButton, QVBoxLayout

### -------------------- dotsPathWidget---------------------       
class PathWidget(QWidget): 
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()
                                        
        self.pathMaker = parent
        self.pathWays  = self.pathMaker.pathWays 
             
        self.type  = 'widget'
        self.save  = QPointF()
        self.label = QLabel('', alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setAccessibleName('widget')
        self.WidgetW, self.WidgetH = 330.0, 250.0
        
        self.rotate = 0
        self.scale  = 1.0
                    
        hbox = QHBoxLayout()
        hbox.addWidget(self.sliderGroup())
        hbox.addSpacing(5) 
        hbox.addWidget(self.buttonGroup())
        self.setLayout(hbox)
              
        self.setFixedHeight(int(self.WidgetH))
        self.setStyleSheet('background-color: rgba(0,0,0,0)')
        self.setContentsMargins(0,15,0,-15)
             
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
        
        self.resetSliders()
                                         
        self.show()
                
### -------------------------------------------------------- 
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)   
        rect = QRectF(2, 2, self.WidgetW-4, self.WidgetH-4)                   
        painter.setPen(QPen(QColor(0,65,255), 5, Qt.PenStyle.SolidLine,            
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(144,238,144))
        painter.drawRoundedRect(rect, 15, 15)
              
    def mousePressEvent(self, e):
        self.save = e.globalPosition()
        e.accept()

    def mouseMoveEvent(self, e):
        self.moveThis(e)
        e.accept()
        
    def mouseReleaseEvent(self, e):
        self.moveThis(e)
        e.accept()
                      
    def moveThis(self, e):
        dif = e.globalPosition() - self.save      
        self.move(self.pos() + QPoint(int(dif.x()), int(dif.y())))
        self.save = e.globalPosition()
        
    def mouseDoubleClickEvent(self, e):
        self.pathMaker.pathWorks.closeWidget()
        e.accept()
  
 ### --------------------------------------------------------    
    def resetSliders(self):
        self.rotate = 0
        self.scale  = 1.0 
        
        self.rotaryDial.setValue(0)
        self.rotateValue.setText('{:3d}'.format(0))
        
        self.scaleSlider.setValue(int(100))
        self.scaleValue.setText('{0:.2f}'.format(1.0))
        
        self.secondsSlider.setValue(self.pathMaker.seconds)
           
    def Seconds(self, val):  
        self.pathMaker.seconds = val    
        self.secondsValue.setText('{:2d}'.format(val))
   
    def Rotate(self, val): 
        self.rotatePath(val)
        self.rotateValue.setText('{:3d}'.format(val))
   
    def rotatePath(self, val): 
        inc = (val - self.rotate)
        self.rotateScale(0, -inc)
        self.rotate = val
            
    def Scale(self, val):
        op = (val/100)
        self.scalePath(op)
        self.scaleValue.setText('{0:.2f}'.format(op))
                               
    def scalePath(self, val): 
        per = (val - self.scale) / self.scale    
        self.rotateScale(per, 0)
        self.scale = val
 
    def rotateScale(self, per, inc):  ## handles both rotation and scaling 
        if len(self.pathMaker.pts) > 0: 
            self.pathMaker.pathWorks.scaleRotate('A', per, inc)  ## used by other classes as well
              
### -------------------------------------------------------- 
    def sliderGroup(self):
        groupBox = QGroupBox('Rotate    Scale  Seconds' )
        
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
        self.rotaryDial.setNotchTarget(15.0)
        self.rotaryDial.valueChanged.connect(self.Rotate)
    
        self.scaleValue = QLabel('1.00', alignment=Qt.AlignmentFlag.AlignCenter)
        self.scaleSlider = QSlider(Qt.Orientation.Vertical)   
        self.scaleSlider.setMinimum(25)
        self.scaleSlider.setMaximum(225)
        self.scaleSlider.setSingleStep(1)
        self.scaleSlider.setValue(100)
        self.scaleSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scaleSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.scaleSlider.setTickInterval(25)  
        self.scaleSlider.valueChanged.connect(self.Scale)   
     
        self.secondsValue = QLabel(str(self.pathMaker.seconds), alignment=Qt.AlignmentFlag.AlignCenter)
        self.secondsSlider = QSlider(Qt.Orientation.Vertical)
        self.secondsSlider.setMinimum(10)
        self.secondsSlider.setMaximum(60)
        self.secondsSlider.setSingleStep(1)
        self.secondsSlider.setValue(self.pathMaker.seconds)
        self.secondsSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.secondsSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.secondsSlider.setTickInterval(10)  
        self.secondsSlider.valueChanged.connect(self.Seconds) 
                         
        sbox = QHBoxLayout()  ## sliders  
        sbox.addSpacing(-10)    
        sbox.addWidget(self.rotaryDial)  
        sbox.addSpacing(10)       
        sbox.addWidget(self.scaleSlider)
        sbox.addSpacing(10)                
        sbox.addWidget(self.secondsSlider)  
        
        vabox = QHBoxLayout()  ## values
        vabox.addSpacing(0) 
        vabox.addWidget(self.rotateValue)        
        vabox.addSpacing(0) 
        vabox.addWidget(self.scaleValue)  
        vabox.addSpacing(10) 
        vabox.addWidget(self.secondsValue)      
        vabox.setAlignment(Qt.AlignmentFlag.AlignBottom)
                 
        vbox = QVBoxLayout()  
        vbox.addLayout(sbox)
        vbox.addLayout(vabox)
        
        lbox = QHBoxLayout()  
        lbox.addWidget(self.label)
        
        vbox.addSpacing(5) 
        vbox.addLayout(lbox) 
        vbox.addSpacing(-5) 
        
        groupBox.setLayout(vbox)
        return groupBox

### -------------------------------------------------------- 
    def buttonGroup(self):
        groupBox = QGroupBox('PathMaker ')
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        groupBox.setFixedWidth(103)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
                     
        waysBtn = QPushButton('WayPts')                 
        saveBtn = QPushButton('Save')
        editBtn = QPushButton('Edit')
        centerBtn = QPushButton('Center')
        self.newBtn = QPushButton('New')
        filesBtn = QPushButton('Path Files')     
        delBtn  = QPushButton('Delete')
        quitBtn = QPushButton('Close')
    
        waysBtn.clicked.connect(self.pathWays.addWayPtTags)
        saveBtn.clicked.connect(self.pathMaker.pathWays.savePath)
        editBtn.clicked.connect(self.pathMaker.edits.editPoints)
        centerBtn.clicked.connect(self.pathMaker.pathWays.centerPath)
        self.newBtn.clicked.connect(self.pathMaker.edits.toggleNewPath)
        filesBtn.clicked.connect(self.pathMaker.pathChooser)
        delBtn.clicked.connect(self.pathMaker.delete)
        quitBtn.clicked.connect(self.pathMaker.pathWorks.closeWidget)
    
        hbox = QVBoxLayout(self)
        hbox.addWidget(saveBtn)    
        hbox.addWidget(waysBtn)
        hbox.addWidget(editBtn)
        hbox.addWidget(centerBtn)
        hbox.addWidget(self.newBtn)
        hbox.addWidget(filesBtn)      
        hbox.addWidget(delBtn)
        hbox.addWidget(quitBtn)
                
        groupBox.setLayout(hbox)
        return groupBox
                                                                                                                                                                                                                                   
### ------------------- dotsPathWidget ---------------------


                               
                                  