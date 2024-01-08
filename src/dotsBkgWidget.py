
import os.path

from PyQt6.QtCore       import Qt, QPoint, QPointF,QRectF, pyqtSlot 
from PyQt6.QtGui        import QColor, QPen, QPainter
from PyQt6.QtWidgets    import QSlider, QWidget, QGroupBox, QDial, QLabel, \
                                QSlider, QHBoxLayout, QVBoxLayout, QPushButton

from dotsShared         import common                                
from dotsBkgWorks       import BkgWorks
from dotsBkgFlatMatte   import Matte
                      
### ------------------- dotsShadowWidget -------------------                                                                                                                                                            
class BkgWidget(QWidget):  
### -------------------------------------------------------- 
    def __init__(self, parent, maker):
        super().__init__()
                                        
        self.bkgItem  = parent     
        self.bkgMaker = maker
        self.canvas   = self.bkgItem.canvas
        self.view     = self.bkgItem.canvas.view
        
        self.bkgWorks = BkgWorks(self.bkgItem)
           
        self.type = 'widget'
        self.save = QPointF()
                
        self.setAccessibleName('widget')
        self.WidgetW, self.WidgetH = 360.0, 305.0
                    
        vbox = QVBoxLayout()  
          
        hbox = QHBoxLayout()
        hbox.addSpacing(0)   
        hbox.addWidget(self.sliderGroup(), Qt.AlignmentFlag.AlignTop)
        hbox.addSpacing(0) 
        hbox.addWidget(self.buttonGroup(), Qt.AlignmentFlag.AlignTop)
        
        sbox = QHBoxLayout()
        sbox.addWidget(self.scrollButtons(), Qt.AlignmentFlag.AlignBottom)
        vbox.addLayout(hbox)    
        vbox.addLayout(sbox) 
        
        self.setLayout(vbox)
        
        self.label.setText(os.path.basename(self.bkgItem.fileName))
        self.label.setStyleSheet("QLabel{font-size: 14pt;}")
        
        self.setFixedHeight(int(self.WidgetH)) 
        self.setStyleSheet('background-color: rgba(0,0,0,0)')  ## gives you rounded corners
        self.setContentsMargins(-5, 0, 0, 0) 
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)    
           
        self.view.keysSignal[str].connect(self.setKeys)                                                                                         
        self.show()
                   
### --------------------------------------------------------
    @pyqtSlot(str)
    def setKeys(self, key):  ## managing storyboard and pathMaker          
        if key == 'up':  ## scale up  
            self.setBkgRate(int(self.bkgItem.rate *100) + 5)
        elif key == 'down':  ## scale down
            self.setBkgRate(int(self.bkgItem.rate *100) - 5)
                     
    def paintEvent(self, e): 
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)        
        rect = QRectF(2, 2, self.WidgetW-4, self.WidgetH-4)
        painter.setPen(QPen(QColor(104,255,204), 5, Qt.PenStyle.SolidLine,  ## border
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)) 
        painter.setBrush(QColor(175,175,175))  ## grayish
        painter.drawRoundedRect(rect, 15, 15)
              
    def mousePressEvent(self, e):
        self.save = e.globalPosition()  ## works the best, needs to change for pyqt6
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
    def centerBkg(self):
        if self.bkgItem != None and self.bkgItem.type == 'bkg':  
            width = self.bkgItem.imgFile.width()
            height = self.bkgItem.imgFile.height()
            self.bkgItem.x = (common['ViewW']- width)/2
            self.bkgItem.y = (common['ViewH']- height)/2
            self.bkgItem.setPos(self.bkgItem.x, self.bkgItem.y) 
            
    def setMatte(self):
        self.bkgMaker.closeWidget()
        self.bkgMaker.matte = Matte(self.bkgItem) 
                                             
    def setBkgRate(self, val):
        if self.bkgItem != None and self.bkgItem.type == 'bkg':                         
            self.bkgItem.rate = val/100  
            self.rateSlider.setValue(val)    
            self.rateValue.setText('{0:.2f}'.format(val/100))   
            self.bkgWorks.setRateTrackers()
                       
    def setBkgShowtime(self, val):
        if self.bkgItem != None and self.bkgItem.type == 'bkg':  
            self.bkgItem.showtime = val   
            self.showtimeSlider.setValue(val)   
            self.showtimeValue.setText('{:2d}'.format(val))
            self.bkgWorks.setShowTimeTrackers()
            
    def setBkgFactor(self, val):
        if self.bkgItem != None and self.bkgItem.type == 'bkg':  
            self.bkgItem.factor = val/100
            self.factorDial.setValue(val)
            self.factorValue.setText('{0:.2f}'.format(val/100))
            self.bkgWorks.setFactorTrackers()
     
### --------------------------------------------------------
    def sliderGroup(self):
        groupBox = QGroupBox(' Duration  Showtime  Factor')
        groupBox.setFixedWidth(185)   
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
            
        self.factorValue = QLabel('1.00', alignment=Qt.AlignmentFlag.AlignCenter)
        self.factorValue.setFixedWidth(40)
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
          
        self.rateValue = QLabel('')
        self.rateValue.setFixedWidth(50)
        self.rateSlider = QSlider(Qt.Orientation.Vertical)
        self.rateSlider.setMinimum(1250)
        self.rateSlider.setMaximum(2500)
        self.rateSlider.setSingleStep(1)
        self.rateSlider.setValue(0)
        self.rateSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.rateSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.rateSlider.setTickInterval(250)  
        self.rateSlider.valueChanged.connect(self.setBkgRate)   
        
        self.showtimeValue = QLabel('')
        self.showtimeValue.setFixedWidth(50)
        self.showtimeSlider = QSlider(Qt.Orientation.Vertical)
        self.showtimeSlider.setMinimum(5)
        self.showtimeSlider.setMaximum(30)
        self.showtimeSlider.setSingleStep(1)
        self.showtimeSlider.setValue(5)
        self.showtimeSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.showtimeSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.showtimeSlider.setTickInterval(5)  
        self.showtimeSlider.valueChanged.connect(self.setBkgShowtime)
                                                  
        sbox = QHBoxLayout()  ## controls 
        
        sbox.addSpacing(10)       
        sbox.addWidget(self.rateSlider) 
        sbox.addSpacing(20)                
        sbox.addWidget(self.showtimeSlider) 
        sbox.addSpacing(5)         
        sbox.addWidget(self.factorDial) 
       
        hbox = QHBoxLayout()  ## values
       
        hbox.addSpacing(5) 
        hbox.addWidget(self.rateValue, Qt.AlignmentFlag.AlignRight)     
        hbox.addSpacing(5) 
        hbox.addWidget(self.showtimeValue)  
        hbox.setAlignment(Qt.AlignmentFlag.AlignBottom)
        hbox.addSpacing(-10) 
        hbox.addWidget(self.factorValue) 
   
        fbox = QHBoxLayout()  
        self.label = QLabel('file name goes here', alignment=Qt.AlignmentFlag.AlignCenter)
        fbox.addWidget(self.label)
         
        vbox = QVBoxLayout()  
        
        vbox.addSpacing(-5)
        vbox.addLayout(sbox)
        vbox.addLayout(hbox)  
        vbox.addSpacing(-5) 
        vbox.addLayout(fbox) 
        vbox.addSpacing(-5) 
                
        groupBox.setLayout(vbox)
        return groupBox                  

### -------------------------------------------------------- 
    def buttonGroup(self):
        groupBox = QGroupBox('BackGrounds  ')
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        groupBox.setFixedWidth(115)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
      
        resetBtn  = QPushButton('Reset')               
        runBtn    = QPushButton('Run')
        self.lockBtn  = QPushButton('Locked')
        flopBtn    = QPushButton('Flop')
        matteBtn  = QPushButton('Matte')
        deleteBtn = QPushButton('Delete')
        centerBtn = QPushButton('Center')
        quitBtn   = QPushButton('Close')
              
        resetBtn.clicked.connect(self.bkgWorks.reset)
        runBtn.clicked.connect(self.bkgMaker.showtime)    
        self.lockBtn.clicked.connect(self.bkgWorks.toggleBkgLocks)   
        flopBtn.clicked.connect(self.bkgMaker.flopIt)
        matteBtn.clicked.connect(self.setMatte)
        centerBtn.clicked.connect(self.centerBkg)    
        deleteBtn.clicked.connect(self.bkgItem.delete)
        quitBtn.clicked.connect(self.bkgMaker.closeWidget)
    
        vbox = QVBoxLayout(self)
        vbox.addWidget(resetBtn)
        vbox.addWidget(runBtn)
        vbox.addWidget(self.lockBtn)
        vbox.addWidget(flopBtn)
        vbox.addWidget(matteBtn)
        vbox.addWidget(deleteBtn)
        vbox.addWidget(centerBtn)
        vbox.addWidget(quitBtn)
                
        groupBox.setLayout(vbox)
        return groupBox
  
### --------------------------------------------------------                       
    def scrollButtons(self):
        groupBox = QLabel()
        groupBox.setAlignment(Qt.AlignmentFlag.AlignBaseline) 
        
        groupBox.setFixedHeight(40)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
      
        self.mirrorBtn = QPushButton('Continuous')
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
  

    # cursor: QCursor = QCursor()  ## ----->>  leaving this in as it works as well
    # QGuiApplication.setOverrideCursor(cursor)
    # p = self.mapFromGlobal(cursor.pos())  
    # cursor.setPos(p.x()+420, int(p.y()+850.0))  ## worked for 720 
    # QGuiApplication.changeOverrideCursor(cursor)      


