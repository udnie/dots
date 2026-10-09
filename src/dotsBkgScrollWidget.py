
from PyQt6.QtCore       import Qt, QPoint, QRectF, QPointF
from PyQt6.QtGui        import QColor, QPen, QPainter, QFont
from PyQt6.QtWidgets    import QSlider, QWidget, QGroupBox,QLabel, \
                                QSlider, QHBoxLayout,  QVBoxLayout, \
                                QPushButton
                            
from dotsSideGig        import getVuCtr

### ----------------- dotsBkgScrollWidget ------------------       
class ScrollWidget(QWidget):  
### --------------------------------------------------------   
    def __init__(self, parent, settings='', switch=''):
        super().__init__()
              
        self.setUI(parent, settings, switch)
        self.show()
            
### --------------------------------------------------------              
    def paintEvent(self, e): 
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)        
        rect = QRectF(2, 2, self.WidgetW-4, self.WidgetH-4)
        painter.setPen(QPen(QColor(0,85,225), 5, Qt.PenStyle.SolidLine, 
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)) 
        painter.setBrush(QColor(192,192,192,255)) 
        painter.drawRoundedRect(rect, 15, 15)
              
    def mousePressEvent(self, e):
        self.save = e.globalPosition()  ## works the best, needs to change for PyQt6
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
        switch = self.switch
        self.works.closeWidget(switch)
        e.accept()
     
### --------------------------------------------------------                   
    def Showtime(self, val): 
        if self.switch == '':
            self.ShowtimeValue.setText(f'{val:<2}') 
            self.settings['ShowTime'] = val
            self.parent.bkgScrollWrks.updWrks(self.settings)
 
    def RunWay(self,val):
        if self.switch == '':
            self.RunwayValue.setText(f'{val:<2}')
            self.settings['RunWay'] = val
            self.parent.bkgScrollWrks.updWrks(self.settings)
  
    def OffSet(self, val):
        if self.switch == '':
            self.OffsetValue.setText(f'{val/100:.2f}') 
            self.settings['OffSet'] = val
            self.parent.bkgScrollWrks.updWrks(self.settings)
                 
### --------------------------------------------------------
    def setUI(self, parent, settings, switch):           
        self.switch = switch
                         
        self.parent = parent
        self.settings = settings
       
        self.type = 'widget' 
        self.setAccessibleName('widget')
        
        self.save = QPointF()
        self.WidgetW, self.WidgetH = 365.0, 270.0
                       
        vbox = QVBoxLayout()   
        label = QLabel('Scrolling Background Settings', alignment=Qt.AlignmentFlag.AlignHCenter)
        label.setFont(QFont("Arial", 15))
        vbox.addWidget(label)
              
        hbox = QHBoxLayout()
        hbox.addWidget(self.sliderGroup(), Qt.AlignmentFlag.AlignBottom)
        sbox = QHBoxLayout()
        sbox.addWidget(self.scrollButtons(self.parent), Qt.AlignmentFlag.AlignBottom)
        vbox.addLayout(hbox)    
        vbox.addLayout(sbox) 
        
        self.setLayout(vbox)
        
        if switch == '':
            self.setSliderDefaults()
        
        self.setFixedHeight(int(self.WidgetH))  
        self.setStyleSheet('background-color: rgba(0,0,0,0)')
        self.setContentsMargins(0,0, 5,0) 
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
                                                                
        x, y = getVuCtr(self.parent.canvas) 
        if self.switch in ('all','on'):
            self.move(x-420,y-320)
        elif switch == 'new':
            self.move(x+155, y-120)
        else:
            self.move(int(x-self.WidgetW/2), int(y-self.WidgetH/2))
               
    def setSliderDefaults(self):
        self.ShowtimeSlider.setValue(self.settings['ShowTime'])
        self.RunwaySlider.setValue(self.settings['RunWay'])
        self.OffsetSlider.setValue(int(self.settings['OffSet']))
                                        
### -------------------------------------------------------- 
    def sliderGroup(self):
        groupBox = QGroupBox()   
        groupBox.setFixedHeight(145)         
   
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        groupBox.setStyleSheet('background: rgb(240, 240, 240)')
   
        self.ShowtimeValue = QLabel('1', alignment=Qt.AlignmentFlag.AlignRight| \
            Qt.AlignmentFlag.AlignVCenter)
        self.ShowtimeValue.setFixedWidth(40)    
        self.ShowtimeLabel = QLabel('ShowTime:', alignment=Qt.AlignmentFlag.AlignVCenter)
        self.ShowtimeLabel.setFixedWidth(70)  
        
        self.ShowtimeSlider = QSlider(Qt.Orientation.Horizontal)
        self.ShowtimeSlider.setMinimum(1)
        self.ShowtimeSlider.setMaximum(30)
        self.ShowtimeSlider.setSingleStep(1)
        self.ShowtimeSlider.setValue(1)
        self.ShowtimeSlider.setFixedWidth(165)
        self.ShowtimeSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.ShowtimeSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.ShowtimeSlider.setTickInterval(5)  
        self.ShowtimeSlider.valueChanged.connect(self.Showtime)
   
        self.RunwayValue = QLabel('0', alignment=Qt.AlignmentFlag.AlignRight| \
            Qt.AlignmentFlag.AlignVCenter)
        self.RunwayValue.setFixedWidth(40)
        self.RunwayLabel = QLabel('RunWay:', alignment=Qt.AlignmentFlag.AlignVCenter)
        self.RunwayLabel.setFixedWidth(70)  
        
        self.RunwaySlider = QSlider(Qt.Orientation.Horizontal)
        self.RunwaySlider.setMinimum(1)
        self.RunwaySlider.setMaximum(200)
        self.RunwaySlider.setSingleStep(1)
        self.RunwaySlider.setValue(100)
        self.RunwaySlider.setFixedWidth(165)
        self.RunwaySlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.RunwaySlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.RunwaySlider.setTickInterval(10)  
        self.RunwaySlider.valueChanged.connect(self.RunWay)   
       
        self.OffsetValue = QLabel('1.00', alignment=Qt.AlignmentFlag.AlignRight| \
            Qt.AlignmentFlag.AlignVCenter)
        self.OffsetValue.setFixedWidth(40)
        self.OffsetLabel = QLabel('OffSet:', alignment=Qt.AlignmentFlag.AlignVCenter)
        self.OffsetLabel.setFixedWidth(70)  
        
        self.OffsetSlider = QSlider(Qt.Orientation.Horizontal)
        self.OffsetSlider.setMinimum(100)
        self.OffsetSlider.setMaximum(200)
        self.OffsetSlider.setSingleStep(1)
        self.OffsetSlider.setValue(0)
        self.OffsetSlider.setFixedWidth(165)
        self.OffsetSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.OffsetSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.OffsetSlider.setTickInterval(10)  
        self.OffsetSlider.valueChanged.connect(self.OffSet)
   
        sbox = QVBoxLayout()  
        
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.ShowtimeLabel)
        hbox1.addWidget(self.ShowtimeSlider) 
        hbox1.addWidget(self.ShowtimeValue)
   
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.RunwayLabel)
        hbox2.addWidget(self.RunwaySlider) 
        hbox2.addWidget(self.RunwayValue)
   
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.OffsetLabel)
        hbox3.addWidget(self.OffsetSlider) 
        hbox3.addWidget(self.OffsetValue)
        
        sbox.addLayout(hbox1) 
        sbox.addLayout(hbox2) 
        sbox.addLayout(hbox3) 
         
        vbox = QVBoxLayout()  
        vbox.addLayout(sbox)
                   
        groupBox.setLayout(vbox)
        return groupBox
     
### --------------------------------------------------------                       
    def scrollButtons(self, parent):
        groupBox = QLabel()
        groupBox.setAlignment(Qt.AlignmentFlag.AlignBaseline) 
        
        groupBox.setFixedHeight(40)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')

        updateBtn = QPushButton('Update')               
        closeBtn  = QPushButton('Close')
        
        if self.switch == '': 
            updateBtn.clicked.connect(parent.bkgScrollWrks.update)
            closeBtn.clicked.connect(parent.bkgScrollWrks.closeScrollWidget)
        else: 
            closeBtn.clicked.connect(lambda: self.parent.canvas.setKeys('N'))
          
        hbox = QHBoxLayout(self)   
        hbox.addWidget(updateBtn)                  
        hbox.addWidget(closeBtn)

        groupBox.setLayout(hbox)
        
        return groupBox
                                                                                                                            
### ---------------------- that's all ----------------------



