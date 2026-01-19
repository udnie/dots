

from PyQt6.QtCore       import Qt, QRectF
from PyQt6.QtGui        import QColor, QPen, QPainter, QFont                 
from PyQt6.QtWidgets    import QWidget, QHBoxLayout, QGroupBox, QLabel,QSlider,\
                                QPushButton, QVBoxLayout
               
### ------------------ videoClipsWidget.py -----------------
''' global varibles and settings '''
### --------------------------------------------------------

Keys  = {
    'A': (1.33, 700,  525,  960,  720),  ##  4:3 apple horizontal    
    'F': (1.50, 790,  525, 1080,  720),  ##  3:2 horizontal   
    'H': (1.77, 930,  525, 1280,  720),  ## 16:9 horizontal
    'S': (1.00, 525,  525,  720,  720),  ##  1:1 square   
    'U': (0.75, 525,  700,  720,  960),  ##  3:4 digital-camera/iphone vertical  
    'T': (0.66, 525,  790,  720, 1080),  ##  2:3 vertical   
    'V': (0.56, 525,  930,  720, 1280),  ## 9:16 vertical
}

ViewW,  ViewH  =  790,  525  ## starting video size
MaxWid, MaxHgt = 1800, 1065

VertW = 525  ## minimum vertical width on open
VertH = 100  ## vertical starting height
HorzH = 225  ## horizontal starting height 

MinWid  = 300  ## minimum widget width
MinHgt  = 400  ## minimum widget height
AspKeys = list(Keys.keys())

VideoMenuKeys = AspKeys + ['L','O','X','C','M',']','[','Shift-S','Aspect','Settings','Clips']
WID, HGT, PAD = 40, 140, 30 ## pixels added to videowidget size when resizing videoPlayerOne's width and height

### --------------------------------------------------------        
class Settings(QWidget):  ## settings for clipsMaker and autoAspect
### -------------------------------------------------------- 
    def __init__(self, parent, switch=''): 
        super().__init__()

        self.parent = parent
        self.clips  = self.parent.clips
        self.switch = switch

        self.WidgetW, self.WidgetH = 505.0, 300.0
                 
        vbox = QVBoxLayout()
        vbox.addSpacing(20) 
 
        label = QLabel('ClipsMaker Settings', alignment=Qt.AlignmentFlag.AlignHCenter)
        label.setFont(QFont("Arial", 14))
        vbox.addWidget(label)
        
        vbox.addWidget(self.sliderGroup())
        vbox.addSpacing(50) 
      
        hbox = QHBoxLayout()    
        hbox.addLayout(vbox)
        hbox.addWidget(self.buttonGroup(), alignment=Qt.AlignmentFlag.AlignVCenter)
        hbox.addSpacing(10)   
      
        self.setLayout(hbox)
    
        self.setFixedHeight(int(self.WidgetH))  
        self.setStyleSheet('background-color: transparent')
      
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
              
        p = self.parent.pos()
        x = int(p.x() + (self.parent.width()/2)) - int(self.WidgetW/2)
        y = int(p.y() + (self.parent.height()/2)) - int(self.WidgetH/2)   
        
        self.move(x, y)
                                                                            
        self.show()

### --------------------------------------------------------
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)   
        rect = QRectF(2, 2, self.WidgetW-4, self.WidgetH-4)                   
        painter.setPen(QPen(QColor(0, 80, 255), 5, Qt.PenStyle.SolidLine,            
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(225, 100, 30, 255))
        painter.drawRoundedRect(rect, 15, 15)
  
    def setFpsVal(self, val):
        self.clips.Fps = val
        self.fpsValue.setText(f'{val:5}')
        
    def setMaxVal(self, val):
        v = int(val/25); val = v * 25
        self.clips.Max = val
        self.maxValue.setText(f'{val:5}')
        
    def setWaitVal(self, val):
        self.clips.Wpr = val
        self.waitValue.setText(f'{val:5}')
        
    def setRnfVal(self, val):
        self.clips.Rnf = val
        self.rnfValue.setText(f'{val:5}')
        
### --------------------------------------------------------      
    def sliderGroup(self):
        groupBox = QGroupBox()   
        groupBox.setFixedHeight(150)         
        groupBox.setFixedWidth(int(300))
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
    
        self.fpslabel = QLabel('FPS')   
        self.fpslabel.setFixedWidth(40)
        self.fpsValue = QLabel(str(self.clips.Fps), alignment=Qt.AlignmentFlag.AlignRight)  
        
        self.fpsSlider =  QSlider(Qt.Orientation.Horizontal)    
        self.fpsSlider.setMinimum(5)
        self.fpsSlider.setMaximum(30)  ## <<-------- max number of frames per second
        self.fpsSlider.setSingleStep(1)
        self.fpsSlider.setTickInterval(5) 
        self.fpsSlider.setValue(self.clips.Fps)
        self.fpsSlider.setFixedWidth(180)
        self.fpsSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.fpsSlider.valueChanged.connect(self.setFpsVal)
        self.fpsSlider.setStyleSheet(""" QSlider::handle:horizontal {background: rgb(200,200,200); 
            border: 2px solid rgb(220,220,220); border-radius: 2px;} """)
            
        self.maxlabel = QLabel('MAX') 
        self.maxlabel.setFixedWidth(40)  
        self.maxValue = QLabel(str(self.clips.Max), alignment=Qt.AlignmentFlag.AlignRight) 
        
        self.maxSlider = QSlider(Qt.Orientation.Horizontal
                                 )  
        self.maxSlider.setMinimum(25)
        self.maxSlider.setMaximum(650)  ## <<----------- max number to read and write
        self.maxSlider.setSingleStep(25)
        self.maxSlider.setTickInterval(50)  
        self.maxSlider.setValue(self.clips.Max)
        self.maxSlider.setFixedWidth(180)
        self.maxSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.maxSlider.valueChanged.connect(self.setMaxVal)
        self.maxSlider.setStyleSheet(""" QSlider::handle:horizontal {background: rgb(200,200,200); 
            border: 2px solid rgb(220,220,220); border-radius: 2px;} """)
 
        self.waitlabel = QLabel('WPR') 
        self.waitlabel.setFixedWidth(40)
        self.waitValue = QLabel(str(self.clips.Wpr), alignment=Qt.AlignmentFlag.AlignRight) 
        
        self.waitSlider = QSlider(Qt.Orientation.Horizontal)   
        self.waitSlider.setMinimum(1)
        self.waitSlider.setMaximum(5)   ## <<-------- waittime - probably won't need to adjust
        self.waitSlider.setSingleStep(1)  
        self.waitSlider.setTickInterval(1) 
        self.waitSlider.setValue(int(self.clips.Wpr))
        self.waitSlider.setFixedWidth(180)
        self.waitSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.waitSlider.valueChanged.connect(self.setWaitVal)
        self.waitSlider.setStyleSheet(""" QSlider::handle:horizontal {background: rgb(200,200,200); 
            border: 2px solid rgb(220,220,220); border-radius: 2px;} """)
        
        self.rnflabel = QLabel("RNF") 
        self.rnflabel.setFixedWidth(40)
        self.rnfValue = QLabel(str(self.clips.Rnf), alignment=Qt.AlignmentFlag.AlignRight) 
        self.rnfSlider = QSlider(Qt.Orientation.Horizontal)   
        self.rnfSlider.setMinimum(0)  ## unfortunate - should be one 
        self.rnfSlider.setMaximum(30)   ## <<-------- number of frames to skip
        self.rnfSlider.setSingleStep(5)          
        self.rnfSlider.setTickInterval(5)    
        self.rnfSlider.setValue(int(self.clips.Rnf))
        self.rnfSlider.setFixedWidth(180)
        self.rnfSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.rnfSlider.valueChanged.connect(self.setRnfVal)
        self.rnfSlider.setStyleSheet(""" QSlider::handle:horizontal {background: rgb(200,200,200); 
            border: 2px solid rgb(220,220,220); border-radius: 2px;} """)
         
        fhbox = QHBoxLayout()  
        fhbox.addWidget(self.fpslabel)
        fhbox.addWidget(self.fpsSlider) 
        fhbox.addWidget(self.fpsValue)
         
        mhbox = QHBoxLayout()
        mhbox.addWidget(self.maxlabel)    
        mhbox.addWidget(self.maxSlider) 
        mhbox.addWidget(self.maxValue)
       
        whbox = QHBoxLayout()
        whbox.addWidget(self.waitlabel)    
        whbox.addWidget(self.waitSlider) 
        whbox.addWidget(self.waitValue)
         
        nhbox = QHBoxLayout()
        nhbox.addWidget(self.rnflabel)    
        nhbox.addWidget(self.rnfSlider) 
        nhbox.addWidget(self.rnfValue)
        
        vbox = QVBoxLayout()
        vbox.addSpacing(5)       
        vbox.addLayout(fhbox) 
        vbox.addSpacing(5)  
        vbox.addLayout(mhbox) 
        vbox.addSpacing(5)  
        vbox.addLayout(whbox) 
        vbox.addSpacing(5)  
        vbox.addLayout(nhbox) 
        
        groupBox.setLayout(vbox)
        return groupBox     
    
### -------------------------------------------------------- 
    def buttonGroup(self):
        groupBox = QGroupBox()
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        groupBox.setFixedWidth(150)
   
        groupBox.setFixedHeight(260)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
      
        self.aspBtn = QPushButton('AutoAspect')   ## buttons true/false set in clipsmaker
        if self.clips.AutoAspect: 
            self.aspBtn.setText('AutoAspectOn')
        
        self.clpsBtn = QPushButton('MakeClips') 
        if self.clips.MakeClips:
            self.clpsBtn.setText('MakeClipsOn')
            
        self.skipBtn = QPushButton("Nth'Frame") 
        if self.clips.SkipFrames:
            self.skipBtn.setText("Nth'FrameOn")
            
        self.firstBtn = QPushButton('FirstFrame') 
        if self.clips.FirstFrame:
            self.firstBtn.setText('FirstFrameOn')
            
        self.filterBtn = QPushButton('Filter') 
        if self.clips.FilterOn:
            self.filterBtn.setText('FilterOn')
                        
        self.playBtn = QPushButton('PlayVideo')
        if self.clips.PlayVideo:
            self.playBtn.setText('PlayVideoOn')
        
        self.nameBtn = QPushButton('FileName')
        if self.clips.AddFileName:
            self.nameBtn.setText('FileNameOn')
        
        self.quitBtn = QPushButton('Close')
        
        if self.switch == '':
            self.aspBtn.clicked.connect(lambda: self.clips.setWidgetButtons("asp"))
            self.clpsBtn.clicked.connect(lambda: self.clips.setWidgetButtons("clips"))
            self.firstBtn.clicked.connect(lambda: self.clips.setWidgetButtons("first"))
            self.skipBtn.clicked.connect(lambda: self.clips.setWidgetButtons("skip"))
            self.filterBtn.clicked.connect(lambda: self.clips.setWidgetButtons("filter"))
            self.playBtn.clicked.connect(lambda: self.clips.setWidgetButtons("play"))
            self.nameBtn.clicked.connect(lambda: self.clips.setWidgetButtons("name"))
            self.quitBtn.clicked.connect(self.clips.closeSettings)
        else:
             self.quitBtn.clicked.connect(self.parent.shared.closeVideoSlideMenus)
  
        hbox = QVBoxLayout(self)
              
        hbox.addWidget(self.aspBtn)
        hbox.addSpacing(5)  
        hbox.addWidget(self.clpsBtn)
        hbox.addSpacing(5)  
        hbox.addWidget(self.firstBtn)
        hbox.addSpacing(5)
        hbox.addWidget(self.skipBtn)
        hbox.addSpacing(5)  
        hbox.addWidget(self.filterBtn)
        hbox.addSpacing(5)  
        hbox.addWidget(self.nameBtn)
        hbox.addSpacing(5)     
        hbox.addWidget(self.playBtn)
        hbox.addSpacing(5)   
        hbox.addWidget(self.quitBtn)
        hbox.addSpacing(10) 
  
        groupBox.setLayout(hbox)
        return groupBox

### ---------------------- that's all ---------------------- 

    
    
