
import os

from PyQt6.QtCore       import Qt, QPointF, QPoint, QRectF
from PyQt6.QtGui        import QColor, QPen, QPainter
from PyQt6.QtWidgets    import QSlider, QWidget, QGroupBox, QLabel, QDial, \
                                QSlider, QHBoxLayout,  QVBoxLayout, QPushButton
                                                
from dotsSideGig        import getVuCtr   
     
### ------------------- dotsShadowWidget -------------------                                                                                                                                                        
class ShadowWidget(QWidget): 
### -------------------------------------------------------- 
    def __init__(self, parent, shadow, switch=''):
        super().__init__()
                  
        self.switch = switch          
              
        if self.switch == '':                     
            self.maker  = parent       
            self.canvas = self.maker.canvas                   
            self.works  = self.maker.works
     
        self.canvas = parent
     
        self.type = 'widget'
        self.setAccessibleName('widget')
         
        self.save = QPointF()
        self.WidgetW, self.WidgetH = 330.0, 245.0
                
        hbox = QHBoxLayout()
        hbox.addWidget(self.sliderGroup())
        hbox.addSpacing(5) 
        hbox.addWidget(self.buttonGroup())
        self.setLayout(hbox)
        
        if self.switch == '':
            file = os.path.basename(self.maker.pixitem.fileName)
        else:
            file = 'Shadow Widget'
            
        self.label.setText(file)
        
        self.setFixedHeight(int(self.WidgetH))
        self.setStyleSheet('background-color: rgba(0,0,0,0)')
        self.setContentsMargins(0,15,0,-15)
             
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
                                
        self.show()
        
        if self.switch in('on', 'all'):
            x, y = getVuCtr(self.canvas)  
            self.label.setText('FileName goes Here')
            if self.switch == 'on':
                self.move(x+75, y-303)
            else:
                self.move(x-360,y-160)
        
### --------------------------------------------------------                                   
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)   
        rect = QRectF(2, 2, self.WidgetW-4, self.WidgetH-4)                   
        painter.setPen(QPen(QColor(0,80,255), 5, Qt.PenStyle.SolidLine,            
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(0,150,245,255))
        painter.drawRoundedRect(rect, 15, 15)
              
    def mousePressEvent(self, e):
        self.save = e.globalPosition()
        e.accept()

    def mouseMoveEvent(self, e):
        if self.switch != 'on':
            self.moveThis(e)
            e.accept()
        
    def mouseReleaseEvent(self, e):
        self.moveThis(e)
        e.accept()
                      
    def moveThis(self, e):
        if self.switch != 'on':
            dif = e.globalPosition() - self.save      
            self.move(self.pos() + QPoint(int(dif.x()), int(dif.y())))
            self.save = e.globalPosition()
        
    def mouseDoubleClickEvent(self, e):
        self.works.closeWidget()
        e.accept()
        
### --------------------------------------------------------
    def Rotate(self, val): 
        if self.maker.linked == False:
            self.maker.shadow.setOriginPt()
            self.works.rotateShadow(val)
            self.rotateValue.setText(f'{val:3}') 
             
    def Scale(self, val):  
        if self.maker.linked == False:
            self.maker.shadow.setOriginPt()
            op = (val/100)
            self.works.scaleShadow(op) 
            self.scaleValue.setText(f'{op:.2f}')
                    
    def Opacity(self, val):
        op = (val/100)
        self.maker.shadow.setOpacity(op)
        self.maker.alpha = op
        self.opacityValue.setText(f'{op:.2f}')        
              
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
        self.rotaryDial.setNotchTarget(15.0)
        if self.switch == '':
            self.rotaryDial.valueChanged.connect(self.Rotate)
    
        self.scaleValue = QLabel('1.00', alignment=Qt.AlignmentFlag.AlignRight)
        self.scaleSlider = QSlider(Qt.Orientation.Vertical)   
        self.scaleSlider.setMinimum(25)
        self.scaleSlider.setMaximum(250)
        self.scaleSlider.setSingleStep(10)
        self.scaleSlider.setValue(100)
        self.scaleSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scaleSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.scaleSlider.setTickInterval(50)  
        if self.switch == '':
            self.scaleSlider.valueChanged.connect(self.Scale)   
        
        self.opacityValue = QLabel('.50', alignment=Qt.AlignmentFlag.AlignRight)
        self.opacitySlider = QSlider(Qt.Orientation.Vertical)   
        self.opacitySlider.setMinimum(0)
        self.opacitySlider.setMaximum(100)
        self.opacitySlider.setSingleStep(1)
        self.opacitySlider.setValue(50) 
        self.opacitySlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.opacitySlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.opacitySlider.setTickInterval(16)  
        if self.switch == '':
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
        
        fbox = QHBoxLayout()  
        self.label = QLabel('file name goes here', alignment=Qt.AlignmentFlag.AlignCenter)
        fbox.addWidget(self.label) 
  
        vbox.addLayout(fbox)
  
        groupBox.setLayout(vbox)
        return groupBox
    
### --------------------------------------------------------   
    def buttonGroup(self):
        groupBox = QGroupBox(' Shadows')
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        groupBox.setFixedWidth(103)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
                     
        hideBtn = QPushButton('Outline')
        helpBtn   = QPushButton('Help')
        flipBtn  = QPushButton('Flip')
        flopBtn  = QPushButton('Flop')
        self.linkBtn = QPushButton('Link')
        newBtn  = QPushButton('New')
        delBtn  = QPushButton('Delete')
        quitBtn = QPushButton('Close')
    
        if self.switch == '':
            hideBtn.clicked.connect(self.works.toggleOutline)  
            helpBtn.clicked.connect(self.maker.openMenu)
            flipBtn.clicked.connect(self.works.flip)
            flopBtn.clicked.connect(self.maker.flop)
            self.linkBtn.clicked.connect(self.maker.toggleWidgetLink)
            newBtn.clicked.connect(self.maker.newShadow)
            delBtn.clicked.connect(self.works.deleteShadow)
            quitBtn.clicked.connect(self.works.closeWidget)
        else: 
            quitBtn.clicked.connect(lambda: self.canvas.setKeys('N'))
    
        hbox = QVBoxLayout(self)
        
        hbox.addWidget(helpBtn)
        hbox.addWidget(flipBtn)
        hbox.addWidget(flopBtn)
        hbox.addWidget(self.linkBtn)
        hbox.addWidget(newBtn)
        hbox.addWidget(delBtn)
        hbox.addWidget(hideBtn)
        hbox.addWidget(quitBtn)
                
        groupBox.setLayout(hbox)
        return groupBox
                                                                                                                                                                                                                   
### ------------------- dotsShadowWidget -------------------


