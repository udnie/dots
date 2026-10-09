
from PyQt6.QtCore       import Qt                  
from PyQt6.QtWidgets    import QLabel, QHBoxLayout, QPushButton, QSlider, \
                                QHBoxLayout, QVBoxLayout, QGroupBox
   
from wrapperWorks       import Works, ViewH, ViewW

BtnsW, Max = ViewW, 200  
 
MinLimit = 3
MaxLimit = 97

### ----------------------- Sliders ------------------------                                                                                                                                                                                                                                                                           
class Sliders: ## and buttons
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()
             
        self.parent = parent
        self.works = Works(parent)
        
### --------------------------------------------------------
    def setFilterBtns(self):
        self.filter8Btn.setText("Filter 8")
        self.filter9Btn.setText("Filter 9")
        # self.filter10Btn.setText("Filter 10")

    def enableSliders(self, bool=False): 
        self.topEndSlider.setEnabled(bool)
        self.bottomSlider.setEnabled(bool)
        self.EdgesSlider.setEnabled(bool)
        self.blendImgSlider.setEnabled(bool)
        self.zeroSliders()
        
    def zeroSliders(self):
        self.topEndSlider.setValue(0)
        self.bottomSlider.setValue(0)
        self.EdgesSlider.setValue(0)
        self.blendImgSlider.setValue(0)   
        self.blendImgSlider.setSliderPosition(0)
          
    def resetSliders(self):
        self.parent.setTopEndValue(MinLimit)
        self.parent.setBottomValue(MinLimit)
        self.parent.setEdgeValue(0)
        
    def resetblendImgSlider(self):
        self.parent.setBlendVal(0)
        self.blendImgSlider.setValue(0) 
        self.blendImgSlider.setSliderPosition(0)
        self.blendlabel.setText('')
 
### --------------------------------------------------------
    def backgoundClamp(self):  ## very good google update
        val = self.topEndSlider.value() 
        # 1. Mathematically clamp the value (much cleaner than if/elif)
        clamped_val = max(MinLimit, min(val, MaxLimit))   
        # 2. If the user dragged out of bounds, visually snap the slider back safely
        if val != clamped_val:
            self.topEndSlider.blockSignals(True)
            self.topEndSlider.setValue(clamped_val)
            self.topEndSlider.blockSignals(False)      
        # 3. CRITICAL: Always send the result to the main engine!
        # (It is no longer trapped inside an 'else' block)
        self.parent.setTopEndValue(clamped_val)
        
    def foregoundClamp(self):  
        val = self.bottomSlider.value() 
        clamped_val = max(MinLimit, min(val, MaxLimit))   
        if val != clamped_val:
            self.bottomSlider.blockSignals(True)
            self.bottomSlider.setValue(clamped_val)
            self.bottomSlider.blockSignals(False)      
        self.parent.setBottomValue(clamped_val)
        
    def edgeWorkClamp(self):  
        val = self.EdgesSlider.value() 
        clamped_val = max(MinLimit, min(val, MaxLimit))   
        if val != clamped_val:
            self.EdgesSlider.blockSignals(True)
            self.EdgesSlider.setValue(clamped_val)
            self.EdgesSlider.blockSignals(False)      
        self.parent.setEdgeValue(clamped_val)

### --------------------------------------------------------
    ''' Thought that I might use of the right/left sliders but what
        I was trying to do didn't work and decided to leave them 
        incase something turned up that could make use of the two. '''
### --------------------------------------------------------
    def setSliders(self):  ## also buttons
        groupBox = QGroupBox()
        groupBox.setFixedSize(95, ViewH+73)
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)    
        groupBox.setStyleSheet("QGroupBox {\n"
            "background: rgb(220,220,220);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "}")

        style = """ QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #e4e4e4, stop:1 #4f4f4f);
            border: 1px solid rgb(115,115,115);
            width: 11px;
            margin: -7px 0;
            border-radius: 3px;
            }
            QSlider {
                background: rgb(245,245,245);
            } 
            QSlider::tick-mark {
                color: black;
                background-color: black;
                width: 1px;
            } """

### ------------------------- topEnd ---------------------
        self.topEndSlider = QSlider(Qt.Orientation.Vertical)
        self.topEndSlider.setFixedSize(50,180)  
        self.topEndSlider.setRange(0,100)
        self.topEndSlider.setValue(0)
                               
        self.topEndSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.topEndSlider.setTickInterval(10)  
        self.topEndSlider.valueChanged.connect(self.backgoundClamp)
        self.topEndSlider.setStyleSheet(style)
        
        abox = QVBoxLayout() 
        abox.addWidget(QLabel("TopEnd", alignment=Qt.AlignmentFlag.AlignCenter)) 
        abox.addSpacing(5)   
        abox.addWidget(self.topEndSlider, alignment=Qt.AlignmentFlag.AlignHCenter)  
        abox.addSpacing(5) 
        self.topEndLabel = QLabel("0.0")  
        abox.addWidget(self.topEndLabel,alignment=Qt.AlignmentFlag.AlignCenter)             

### --------------------- bottom -------------------- 
        self.bottomSlider = QSlider(Qt.Orientation.Vertical)
        self.bottomSlider.setFixedSize(50,180)    
        self.bottomSlider.setRange(0,100)                  
        self.bottomSlider.setValue(0)
        
        self.bottomSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.bottomSlider.setTickInterval(10)      
        self.bottomSlider.valueChanged.connect(self.foregoundClamp)
        self.bottomSlider.setStyleSheet(style)
           
        gbox = QVBoxLayout() 
        gbox.addWidget(QLabel("Bottom", alignment=Qt.AlignmentFlag.AlignCenter))
        gbox.addSpacing(5)
        gbox.addWidget(self.bottomSlider,alignment=Qt.AlignmentFlag.AlignHCenter)  
        gbox.addSpacing(5)
        self.bottomLabel = QLabel("0.0")  
        gbox.addWidget(self.bottomLabel,alignment=Qt.AlignmentFlag.AlignCenter)  
 
### ----------------------- EdgesSlider -------------------- 
        self.EdgesSlider = QSlider(Qt.Orientation.Vertical)
        self.EdgesSlider.setFixedSize(50,180)    
        self.EdgesSlider.setRange(0,100)                  
        self.EdgesSlider.setValue(0)
        
        self.EdgesSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.EdgesSlider.setTickInterval(10)      
        self.EdgesSlider.valueChanged.connect(self.edgeWorkClamp)
        self.EdgesSlider.setStyleSheet(style)
           
        mbox = QVBoxLayout() 
        mbox.addWidget(QLabel("Edges", alignment=Qt.AlignmentFlag.AlignCenter))
        mbox.addSpacing(5)
        mbox.addWidget(self.EdgesSlider,alignment=Qt.AlignmentFlag.AlignHCenter)  
        mbox.addSpacing(5)
        self.edgesLabel = QLabel("0.0")  
        mbox.addWidget(self.edgesLabel,alignment=Qt.AlignmentFlag.AlignCenter) 
 
        self.setBtn = QPushButton("Reset") 
        self.setBtn.clicked.connect(self.resetSliders)     
       
        vbox = QVBoxLayout()  
        vbox.addLayout(abox)
        vbox.addLayout(mbox)
        vbox.addLayout(gbox)
        vbox.addWidget(self.setBtn)
        
        groupBox.setLayout(vbox)
        
        return groupBox      
           
### -------------------------- blend -----------------------          
    def setblendImgSlider(self):
        groupBox = QGroupBox()
        groupBox.setFixedSize(BtnsW-75,70)
        
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        groupBox.setStyleSheet("QGroupBox {\n"
            "background-color: rgb(220,220,220);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "}")
     
        self.blendImgSlider = QSlider(Qt.Orientation.Horizontal)
        self.blendImgSlider.setRange(0,200)                  
        self.blendImgSlider.setValue(0)
        
        self.blendImgSlider.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.blendImgSlider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.blendImgSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        
        self.blendImgSlider.setTickInterval(10)  
        self.blendImgSlider.setPageStep(50)
        self.blendImgSlider.setFixedSize(600,40)
        
        self.blendImgSlider.valueChanged.connect(self.parent.setBlendVal)
                          
        style = """ QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #e4e4e4, stop:1 #4f4f4f);
            border: 1px solid rgb(115,115,115);
            width: 11px;
            margin: -7px 0;
            border-radius: 3px;
            }
            QSlider {
                background: rgb(245,245,245);
            } 
            QSlider::horizontal {
                margin-left: -25px;
                margin-right: -20px;
            }
            QSlider::tick-mark {
                color: black;
                background-color: black;
                width: 1px;
            } """
                                       
        self.blendImgSlider.setStyleSheet(style)                        

        bbox = QHBoxLayout() 
        bbox.addSpacing(5)
        self.blendlabel = QLabel("")  
        bbox.addWidget(self.blendlabel,alignment=Qt.AlignmentFlag.AlignCenter) 
        bbox.addSpacing(10)
        bbox.addWidget(self.blendImgSlider)
        bbox.addSpacing(15)
        groupBox.setLayout(bbox)
        
        return groupBox    
                                      
### --------------------------------------------------------    
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedSize(BtnsW,55)
        
        self.buttonGroup.setAlignment(Qt.AlignmentFlag.AlignCenter)    
        self.buttonGroup.setStyleSheet("QLabel {\n"
            "background-color: rgb(220,220,220);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "}")
         
        filesBtn  = QPushButton("Files")      
        alignBtn = QPushButton("Align")
        newBtn   = QPushButton('Guides') 
        self.filter8Btn = QPushButton('Filter 8')
        self.filter9Btn = QPushButton('Filter 9') 
        # self.filter10Btn = QPushButton('Filter 10') 
        delBtn   = QPushButton('Delete Blended')     
        saveBtn  = QPushButton('Save')
        clearBtn = QPushButton("Clear")
        quitBtn  = QPushButton("Quit")
        
        filesBtn.clicked.connect(self.works.openFiles)
        alignBtn.clicked.connect(self.parent.align)
        newBtn.clicked.connect(self.parent.guides.toggleGuides)
        self.filter8Btn.clicked.connect(lambda: self.works.swap(8))
        self.filter9Btn.clicked.connect(lambda: self.works.swap(9))
        # self.filter10Btn.clicked.connect(lambda: self.works.swap(10))
        delBtn.clicked.connect(self.parent.deleteBlended)
        saveBtn.clicked.connect(self.works.saveDialog)
        clearBtn.clicked.connect(self.parent.clear)
        quitBtn.clicked.connect(self.parent.bye)
        
        hbox = QHBoxLayout(self.parent)
        
        hbox.addWidget(filesBtn)
        hbox.addWidget(alignBtn)
        hbox.addWidget(newBtn)   
        hbox.addWidget(self.filter8Btn)
        hbox.addWidget(self.filter9Btn)
        # hbox.addWidget(self.filter10Btn)
        hbox.addWidget(delBtn)       
        hbox.addWidget(saveBtn)
        hbox.addWidget(clearBtn)   
        hbox.addWidget(quitBtn)
          
        self.buttonGroup.setLayout(hbox)
        
        return self.buttonGroup     

### --------------------- that's all -----------------------




