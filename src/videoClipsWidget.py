
from PyQt6.QtCore       import Qt, QRectF, QTimer
from PyQt6.QtGui        import QColor, QPen, QPainter, QFont                         
from PyQt6.QtWidgets    import QWidget, QHBoxLayout, QGroupBox, QLabel,QSlider,\
                                QPushButton, QVBoxLayout, QTableWidget,  QAbstractItemView, \
                                QTableWidgetItem

from functools          import partial

### ------------------ videoClipsWidget.py -----------------
''' Source for global varibles, help, settings and additional
    code to extract metadata used by getMetaData in 
    videoPlayerOne. '''
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

helpMenuKeys = {  ## help menu - right-mouse-click
    'A':    'Apple/Academy 4X3',  
    'F':    'Full Screen 3X2',
    'H':    'Horiztonal HD 16X9',
    'S':    'Square',
    'T':    'Vertical 2X3',
    'U':    'Apple 3X4 Vertical',                  
    'V':    'Vertical 9X16',
    'C':    'To Clear',
    'L':    'Loop On/Off',
    '>,  +,  ]':    'Scale Up',
    '<,  _,  [':    'Scale Down',
    'X, Q Escape':  'Quit/Exit',
    'Shift-S':      'Hide/Show Slider',
    'Aspect':       'Set Aspect (Button)',
    'Settings':     'Clip Settings',
    'Clips':        'Make a Clip',    
}

AspKeys = list(Keys.keys())
SharedKeys = AspKeys + ['L','O','X','C',']','[','Shift-S','Aspect','Settings','Clips']
WID, HGT, PAD = 40, 140, 30 ## pixels added to videowidget size when resizing videoPlayerOne's width and height

### --------------------------------------------------------     
class Help(QWidget):  
### -------------------------------------------------------- 
    def __init__(self, parent): 
        super().__init__()  
        
        self.parent = parent
    
        self.table = QTableWidget()
        self.table.setRowCount(len(helpMenuKeys)+1)
        self.table.setColumnCount(2)
     
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
      
        self.table.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) 
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.table.setHorizontalHeaderLabels(["Key", "Function"])
        stylesheet = "::section{Background-color: lightgray; font-size:14px;}"
        self.table.horizontalHeader().setStyleSheet(stylesheet)
        
        self.table.setStyleSheet('QTableWidget{\n'   
            'background-color: rgb(250,250,250);\n'                 
            'font-size: 13pt;\n' 
            'font-family: Arial;\n' 
            'border: 3px solid dodgerblue;\n'
            'gridline-color: rgb(190,190,190);}') 
                                                                                                             
        self.table.setColumnWidth(0, 110) 
        self.table.setColumnWidth(1, 156)

        menuWidth, menuHeight = 272, 541 
        self.table.setFixedSize(menuWidth, menuHeight)  
        
        self.table.verticalHeader().setVisible(False) 
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.table.itemClicked.connect(self.clicked)   
         
        row = 0     
        for k,  val in helpMenuKeys.items():   
            item = QTableWidgetItem(k)
            if k in ('Aspect','Clips','Settings'):
                item.setBackground(QColor(225, 225, 225))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item)
            
            item = QTableWidgetItem(val)
            if k in ('Aspect','Clips','Settings'):
                item.setBackground(QColor(225, 225, 225))  
            self.table.setItem(row, 1, item)      
            row += 1
                  
        item = QTableWidgetItem("Right-Click or Click Here to Close")
        item.setBackground(QColor('lightgray'))
        item.setFont(QFont("Arial", 14))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.table.setSpan(row, 0, 1, 2)  
        self.table.setItem(row, 0, item)   
        
        p, pwidth, pheight = self.parent.pos(), self.parent.width(), self.parent.height()
        
        x = int(p.x() + (pwidth/2)) - int(menuWidth/2)   
        y = int(p.y() + (pheight/2)) - int(menuHeight/2)   
        
        self.table.move(x,y)  
        self.table.show()
        
    def clicked(self):
        help = self.table.item(self.table.currentRow(), 0).text().strip()
        match help: 
            case ('X, Q Escape'):
                help = 'X'
            case ('>,  +,  ]'):
                help = ']'
            case ('<,  _,  ['): 
                help = '['     
        if help in SharedKeys: 
            try:
                QTimer.singleShot(25, partial(self.parent.sharedKeys, help))
            except:
                None
        self.parent.closeHelpMenu()
  
    def tableClose(self):
        self.parent.helpFlag == False
        self.table.close()   
          
### --------------------------------------------------------        
class Settings(QWidget):  ## settings for clipsMaker and autoAspect
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.clips  = self.parent.clips

        self.WidgetW, self.WidgetH = 505.0, 300.0
           
        hbox = QHBoxLayout() 
        hbox.addWidget(self.sliderGroup())  
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
        self.rnfSlider.setMinimum(0)
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
        vbox.addLayout(fhbox) 
        vbox.addSpacing(5)  
        vbox.addLayout(mhbox) 
        vbox.addSpacing(5)  
        vbox.addLayout(whbox) 
        vbox.addSpacing(5)  
        vbox.addLayout(nhbox) 
        
        groupBox.setLayout(vbox)
        return groupBox     
    
    def buttonGroup(self):
        groupBox = QGroupBox()
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        groupBox.setFixedWidth(150)
   
        groupBox.setFixedHeight(260)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
      
        self.aspBtn = QPushButton('AutoAspect')   ## buttons true/false set in clipsmaker
        if self.clips.AutoAspect == True: 
            self.aspBtn.setText('AutoAspectOn')
        
        self.clpsBtn = QPushButton('MakeClips') 
        if self.clips.MakeClips == True:
            self.clpsBtn.setText('MakeClipsOn')
            
        self.skipBtn = QPushButton("Nth'Frame") 
        if self.clips.SkipFrames == True:
            self.skipBtn.setText("Nth'FrameOn")
            
        self.firstBtn = QPushButton('FirstFrame') 
        if self.clips.FirstFrame == True:
            self.firstBtn.setText('FirstFrameOn')
            
        self.filterBtn = QPushButton('Filter') 
        if self.clips.FilterOn == True:
            self.filterBtn.setText('FilterOn')
                        
        self.playBtn = QPushButton('PlayVideo')
        if self.clips.PlayVideo == True:
            self.playBtn.setText('PlayVideoOn')
        
        self.nameBtn = QPushButton('FileName')
        if self.clips.AddFileName == True:
            self.nameBtn.setText('FileNameOn')
        
        self.quitBtn = QPushButton('Close')
        
        self.aspBtn.clicked.connect(lambda: self.clips.setWidgetButtons("asp"))
        self.clpsBtn.clicked.connect(lambda: self.clips.setWidgetButtons("clips"))
        self.firstBtn.clicked.connect(lambda: self.clips.setWidgetButtons("first"))
        self.skipBtn.clicked.connect(lambda: self.clips.setWidgetButtons("skip"))
        self.filterBtn.clicked.connect(lambda: self.clips.setWidgetButtons("filter"))
        self.playBtn.clicked.connect(lambda: self.clips.setWidgetButtons("play"))
        self.nameBtn.clicked.connect(lambda: self.clips.setWidgetButtons("name"))
        self.quitBtn.clicked.connect(self.clips.closeSettings)
        
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
       
### -------------------------------------------------------- 
### the other metadata readers, apple mdls and ffprobe  
### -------------------------------------------------------- 
    ''' uses mdls - mac only - reports non 9:16 vertical width and height correctly -- 
        drag and drop doesn't work in pyqt5 on desktop '''   
    # try:  
    #     result = subprocess.run(
    #         ['mdls', '-name', 'kMDItemPixelWidth', '-name', 'kMDItemPixelHeight', path],
    #         capture_output=True,
    #         text=True,
    #         check=True
    #         )
    #     output = result.stdout
    #     width, height = None, None
    #     for line in output.splitlines():
    #         if 'kMDItemPixelWidth' in line:
    #             width = int(line.split('=')[-1].strip())
    #         elif 'kMDItemPixelHeight' in line:
    #             height = int(line.split('=')[-1].strip())
    #         del line
    #     return width, height
    # except Exception:
    #     return 0, 0 
         
    ''' requires opencv-python - may not always report width/height correctly 
        for non 9:16 verticals - initial method - not mac specific '''
    # try:  
    #     import cv2  ## <<---------------------  
    #     try:
    #         cap = cv2.VideoCapture(path) 
    #     except:
    #         return 0,0
    #     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #     cap.release()
    #     return width, height
    # except:
    #     return 0, 0

    ''' uses ffprobe -- may not always report width/height correctly for non 9:16 verticals
        and blows up if run from mac desktop -- works well in vscode '''
    # try: 
    #     result = subprocess.run(
    #         ['ffprobe', '-v', 'error', '-select_streams',  'v:0', '-show_entries', 'stream=width,height','-of', 'csv=s=,:p=0', path],
    #         capture_output=True,
    #         text=True,
    #         check=True
    #     )
    #     res = result.stdout.strip()
    #     i = res.index(',')
    #     width, height = res[0:i], res[i+1:]
    #     return int(width), int(height) 
    # except Exception:
    #     return 0, 0
        
  
### ---------------------- that's all ---------------------- 

    
    
    
