
import os.path
import math

from PyQt6.QtCore       import Qt, QPoint, QPointF,QRectF
from PyQt6.QtGui        import QColor, QPen, QPainter
from PyQt6.QtWidgets    import QSlider, QWidget, QGroupBox, QDial, QLabel, \
                                QSlider, QHBoxLayout, QVBoxLayout, QPushButton
                            
from dotsBkgWorks       import BkgWorks
from dotsSideGig        import getVuCtr

ShiftKeys = (Qt.Key.Key_Up, Qt.Key.Key_Down) 
      
### ------------------- dotsShadowWidget -------------------                                                                                                                                                            
class BkgWidget(QWidget):  
### -------------------------------------------------------- 
    def __init__(self, parent, maker, switch=''):
        super().__init__()
             
        self.switch = switch
                           
        if self.switch == '':         
            self.bkgItem  = parent     
            self.bkgMaker = maker
            self.canvas   = self.bkgItem.canvas
     
            self.bkgWorks = BkgWorks(self.bkgItem)
            self.bkgScrollWrks = self.bkgWorks.bkgScrollWrks  
            
            self.bkgItem.widgetOn = True 
             
        self.canvas = parent
            
        self.type = 'widget'
        self.setAccessibleName('widget')
    
        self.save = QPointF()
        self.WidgetW, self.WidgetH = 370.0, 300.0
                  
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
    
        if self.switch == '':
            self.label.setText(self.bkgItem.fileName)
            self.bkgItem.canvas.dots.statusBar.showMessage(self.bkgItem.fileName)  
        
        self.setFixedHeight(int(self.WidgetH)) 
        self.setStyleSheet('background-color: rgba(0,0,0,0)')  ## gives you rounded corners
        self.setContentsMargins(-5, 0, 0, 0) 
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)    
                                                                                                   
        self.show()
        
        if self.switch in('on', 'all'):
            x, y = getVuCtr(self.canvas)  
            self.label.setText('FileName  goes Here')
            if self.switch == 'on':
                self.move(x-425, y-5)
            else:
                self.move(x-400,y-150)
                
### --------------------------------------------------------
    def setKeys(self, key):  ## updated thru bkgItem - did use grabkey - not good idea
        self.key = key 
        if key in ('left','right'):  ## sends left, right if using shift up/down
            points = .01 
            if self.key == 'right': 
                key = 'up'
            elif self.key == 'left': 
                key = 'down' 
        else:
            points = .05  
            
        if self.bkgItem.rate > 12.45 and self.switch == '':
            if key in ('up'): 
                self.setBkgRateValue(int((self.bkgItem.rate + points) *100))
            elif key in ('down'): 
                self.setBkgRateValue(int((self.bkgItem.rate - points) *100))
               
    def paintEvent(self, e): 
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)        
        rect = QRectF(2, 2, self.WidgetW-4, self.WidgetH-4)
        painter.setPen(QPen(QColor(0,80,255), 5, Qt.PenStyle.SolidLine,  ## border
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)) 
        painter.setBrush(QColor(175,175,175))  ## grayish
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
            self.move(self.pos() + QPoint(int(dif.x()), int(dif.y())) )
            self.save = e.globalPosition()
            
    def mouseDoubleClickEvent(self, e):
        if self.switch == '':
            self.bkgItem.widgetOn = False
            self.bkgMaker.closeWidget()
            e.accept()
 
### --------------------------------------------------------                                             
    def setBkgRateValue(self, val): 
        if self.bkgItem != None and self.bkgItem.type == 'bkg':                         
            self.bkgItem.rate = val/100  
            self.rateSlider.setValue(val)    
            self.rateValue.setText(f'{val/100:.2f}')   
            self.bkgScrollWrks.setTrackerRate(self.bkgItem)
                       
    def setBkgShowtimeValue(self, val):
        if self.bkgItem != None and self.bkgItem.type == 'bkg':  
            self.bkgItem.showtime = val   
            self.showtimeSlider.setValue(val)   
            self.showtimeValue.setText(f'{val:2}')
            self.bkgScrollWrks.setShowTimeTrackers(self.bkgItem)
            
    def setBkgFactorValue(self, val):
        if self.bkgItem != None and self.bkgItem.type == 'bkg':  
            self.bkgItem.factor = val/100
            self.factorDial.setValue(val)
            self.factorValue.setText(f'{val/100:.2f}')
            self.bkgScrollWrks.setTrackerFactor(self.bkgItem)
     
### --------------------------------------------------------
    def sliderGroup(self):
        groupBox = QGroupBox('ScreenRate  Showtime  Factor ')
        groupBox.setFixedWidth(205) 
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
            
        self.factorValue = QLabel('1.00',  alignment=Qt.AlignmentFlag.AlignHCenter)
        self.factorValue.setFixedWidth(40)
        self.factorDial = QDial()
        self.factorDial.setFixedWidth(55)
        self.factorDial.setMinimum(50)
        self.factorDial.setMaximum(150)
        self.factorDial.setValue(100)
        self.factorDial.setWrapping(False)
        self.factorDial.setNotchesVisible(True)
        self.factorDial.setNotchTarget(5)
        self.factorDial.setSingleStep(10)
        if self.switch == '':
            self.factorDial.valueChanged.connect(self.setBkgFactorValue)
          
        self.rateValue = QLabel('',  alignment=Qt.AlignmentFlag.AlignRight)
        self.rateValue.setFixedWidth(35)
        self.rateSlider = QSlider(Qt.Orientation.Vertical)
        self.rateSlider.setMinimum(1250)
        self.rateSlider.setMaximum(3500)
        self.rateSlider.setSingleStep(1)
        self.rateSlider.setValue(0)
        self.rateSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.rateSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.rateSlider.setTickInterval(250) 
        if self.switch == '': 
            self.rateSlider.valueChanged.connect(self.setBkgRateValue)   
        
        self.showtimeValue = QLabel('', alignment=Qt.AlignmentFlag.AlignRight)
        self.showtimeValue.setFixedWidth(25)
        self.showtimeSlider = QSlider(Qt.Orientation.Vertical)
        self.showtimeSlider.setMinimum(5)
        self.showtimeSlider.setMaximum(30)
        self.showtimeSlider.setSingleStep(1)
        self.showtimeSlider.setValue(5)
        self.showtimeSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.showtimeSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.showtimeSlider.setTickInterval(5)  
        if self.switch == '':
            self.showtimeSlider.valueChanged.connect(self.setBkgShowtimeValue)
                  
        button = QPushButton('Update', self) 
        button.setFixedWidth(65)
        if self.switch == '':
            button.clicked.connect(self.bkgScrollWrks.updateDictionary)
                                          
        sbox = QHBoxLayout()  ## sliders and dial  
        sbox.addSpacing(20)       
        sbox.addWidget(self.rateSlider) 
        sbox.addSpacing(20)                
        sbox.addWidget(self.showtimeSlider) 
        sbox.addSpacing(-5)   
        
        dbox = QVBoxLayout()  ## stack dial and value     
        dbox.addSpacing(5)    
        dbox.addWidget(self.factorDial, alignment=Qt.AlignmentFlag.AlignLeft)  
        dbox.addWidget(self.factorValue, alignment=Qt.AlignmentFlag.AlignHCenter)
        dbox.addSpacing(15)      
     
        sbox.addSpacing(5)
        sbox.addLayout(dbox,Qt.AlignmentFlag.AlignHCenter)    
 
        hbox = QHBoxLayout()  ## slider values and update button
        hbox.addSpacing(5)       
        hbox.addWidget(self.rateValue, Qt.AlignmentFlag.AlignLeft)     
        hbox.addSpacing(20) 
        hbox.addWidget(self.showtimeValue, Qt.AlignmentFlag.AlignRight) 
        hbox.addSpacing(5) 
        hbox.addWidget(button, Qt.AlignmentFlag.AlignRight)
        hbox.addSpacing(10)
            
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
        helpBtn   = QPushButton('Help')
        centerBtn = QPushButton('Center')
        quitBtn   = QPushButton('Close')
              
        if self.switch == '':
            resetBtn.clicked.connect(lambda: self.bkgMaker.bkgtrackers.resetTracker(self.bkgItem))
            helpBtn.clicked.connect(self.bkgItem.openMenu)
            runBtn.clicked.connect(lambda: self.bkgMaker.showtime(self.bkgItem))  ## run a scroller  
            self.lockBtn.clicked.connect(self.bkgScrollWrks.toggleBkgLocks)   
            flopBtn.clicked.connect(lambda: self.bkgMaker.flopIt(self.bkgItem))  
            matteBtn.clicked.connect(self.bkgWorks.openMatte)
            centerBtn.clicked.connect(self.bkgWorks.centerBkg)   
            deleteBtn.clicked.connect(lambda: self.bkgMaker.deleteBkg(self.bkgItem))  
            quitBtn.clicked.connect(self.bkgWorks.closeWidget) 
        else: 
            quitBtn.clicked.connect(lambda: self.canvas.setKeys('N'))
        
        vbox = QVBoxLayout(self)
        
        vbox.addWidget(helpBtn)
        vbox.addWidget(resetBtn)
        vbox.addWidget(runBtn)
        vbox.addWidget(flopBtn)
        vbox.addWidget(matteBtn)
        vbox.addWidget(deleteBtn)
        vbox.addWidget(self.lockBtn)
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
        
        if self.switch == '':
            self.mirrorBtn.clicked.connect(self.bkgWorks.setMirroring)
            self.leftBtn.clicked.connect(self.bkgScrollWrks.setLeft)
            self.rightBtn.clicked.connect(self.bkgScrollWrks.setRight)
        
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
  

    
