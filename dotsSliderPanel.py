
from PyQt6.QtCore     import Qt, pyqtSignal, QAbstractTableModel                    
from PyQt6.QtWidgets  import QPushButton, QWidget, QFrame, QSlider, QHBoxLayout, QVBoxLayout, \
                             QTableView, QHeaderView, QAbstractItemView, QLabel
                      
from dotsShared       import keyMenu, pathMenu

SliderW, SliderH, OffSet = 195, 685, 20

### --------------------- dotssliderPanel ------------------
''' dotssliderPanel contains the TableGroup and the SliderGroup
    and the TableModel class used by the TableView '''
### --------------------------------------------------------
class SliderPanel(QWidget):
### --------------------------------------------------------
    ## transfers slider output to bkgMaker
    sliderSignal = pyqtSignal(str, int)

    def __init__(self, parent):
        super().__init__()
        
        self.canvas = parent
    
        self.setFixedSize(SliderW, SliderH) 

        self.isEnabled = False
        self.pathMenuSet = False

        layout = QVBoxLayout(self)        
        layout.addWidget(self.addTableGroup())     
        layout.addSpacing(20)
        layout.addWidget(self.addSliderGroup())

        layout.setContentsMargins(20, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

### --------------------------------------------------------
    def enableSliders(self, bool=False): 
        self.isEnabled = bool
        self.rotateSlider.setValue(0)
        self.scaleSlider.setValue(100)
        self.opacitySlider.setValue(100)
        self.sliderGroup.setEnabled(bool)

### --------------------------------------------------------
    def addTableGroup(self):
        self.tableView = QTableView()
        self.setTableModel(keyMenu)  ## initial menu
         
        self.tableView.setFixedSize(SliderW-OffSet,350)
        self.tableView.setAlternatingRowColors(True) 
 
        ## make it read-only
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.setSelectionMode(self.tableView.SelectionMode.NoSelection)
        self.tableView.verticalHeader().setVisible(False)

        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.tableView.setColumnWidth(0, 48) 
        self.tableView.setColumnWidth(1, 110)

        return self.tableView

### --------------------------------------------------------
    def setTableModel(self, list):  ## called thru sideCar 'K' key
        header = [' Keys ', 'StoryBoard ']
        model = TableModel(list, header)
        self.tableView.setModel(model)
        if list != keyMenu:
            header[1] = 'PathMaker '
            self.tableView.horizontalHeader().setStyleSheet(
                "QHeaderView::section{\n"
                "background-color: rgb(144,238,144);\n"
                "border: .5px solid lightgray;\n"
                "font-size: 12px;\n"
                "}")  
            self.tableView.setStyleSheet("QTableView {\n"
                "alternate-background-color: rgb(144,238,144);\n"
                "font-size: 12px;\n"
                "}")  
        else:
            header[1] = 'StoryBoard '
            self.tableView.horizontalHeader().setStyleSheet(
                "QHeaderView::section{\n"
                "background-color: rgb(220,220,220);\n"
                "border: .5px solid lightgray;\n"
                "font-size: 12px;\n"
                "}") 
            self.tableView.setStyleSheet("QTableView {\n"
                "alternate-background-color: rgb(220,220,220);\n"
                "font-size: 12px;\n"
                "}")  

### --------------------------------------------------------
    def addSliderGroup(self):
        self.sliderGroup = QLabel()
        self.sliderGroup.setFixedSize(SliderW-OffSet-3,335)

        rotateLabel = QLabel("Rotate")
        self.rotateValue = QLabel("  0")
        self.rotateValue.setAlignment(Qt.AlignmentFlag.AlignLeft)

        scaleLabel = QLabel("Scale")
        self.scaleValue = QLabel("1.0")
        self.scaleValue.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        opacityLabel = QLabel("Opacity")
        self.opacityValue = QLabel("1.0")
        self.opacityValue.setAlignment(Qt.AlignmentFlag.AlignLeft)
       
        self.rotateSlider = QSlider(Qt.Orientation.Vertical)  
        self.rotateSlider.setMinimum(1)
        self.rotateSlider.setMaximum(360)
        self.rotateSlider.setSingleStep(1)
        self.rotateSlider.setValue(1) 
        self.rotateSlider.valueChanged.connect(self.setRotate)      
        self.rotateSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.rotateSlider.setTickInterval(90)
        
        self.scaleSlider = QSlider(Qt.Orientation.Vertical)  
        self.scaleSlider.setMinimum(25)
        self.scaleSlider.setMaximum(300)
        self.scaleSlider.setSingleStep(2)
        self.scaleSlider.setValue(100) 
        self.scaleSlider.valueChanged.connect(self.setScale)      
        self.scaleSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.scaleSlider.setTickInterval(25)

        self.opacitySlider = QSlider(Qt.Orientation.Vertical)
        self.opacitySlider.setMinimum(1)
        self.opacitySlider.setMaximum(100)
        self.opacitySlider.setSingleStep(1)
        self.opacitySlider.setValue(100) 
        self.opacitySlider.valueChanged.connect(self.setOpacity)
        self.opacitySlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.opacitySlider.setTickInterval(5)
        
        self.ctrBtn = QPushButton("Center")
        self.ctrBtn.clicked.connect(lambda: self.sliderSignal[str, int].emit("center", 0))
               
        lbox = QHBoxLayout()    ## labels
        lbox.addWidget(rotateLabel)
        lbox.addSpacing(-2) 
        lbox.addWidget(scaleLabel)     
        lbox.addSpacing(-5) 
        lbox.addWidget(opacityLabel)

        vabox = QHBoxLayout()    ## values
        vabox.addSpacing(8) 
        vabox.addWidget(self.rotateValue)
        vabox.addSpacing(-15) 
        vabox.addWidget(self.scaleValue)     
        vabox.addSpacing(2) 
        vabox.addWidget(self.opacityValue)

        sbox = QHBoxLayout()    ## sliders      
        sbox.addWidget(self.rotateSlider) 
        sbox.addWidget(self.scaleSlider)                  
        sbox.addWidget(self.opacitySlider) 

        vbox = QVBoxLayout()  
        vbox.addLayout(lbox)
        vbox.addLayout(vabox)
        vbox.addLayout(sbox)
        vbox.addWidget(self.ctrBtn)

        self.sliderGroup.setLayout(vbox)
        self.sliderGroup.setContentsMargins(-5, 5, 0, 10)
        self.sliderGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.sliderGroup.setLineWidth(1)

        return self.sliderGroup

### --------------------------------------------------------
    def setRotate(self, val):
        if val >= 179 and val <= 181: 
            val= 180
        elif val >= 89 and val <= 91: 
            val = 90
        elif val >= 269 and val <= 271: 
            val = 270
        if val < 0 or val > 360: val = 0 
        self.rotateValue.setText("{:3d}".format(val))
        if self.isEnabled:  
            self.sliderSignal[str, int].emit("rotate", int(val))

    def setScale(self, val):
        if val >= 99 and val <= 101: val= 100
        self.scaleValue.setText("{0:.2f}".format(val/100.0))
        if self.isEnabled:
            self.sliderSignal[str, int].emit("scale", int(val))
 
    def setOpacity(self, val):
        if val >= 99 and val <= 101: 
            val= 100
        elif val < 0: 
            val = 0
        self.opacityValue.setText("{0:.2f}".format(val/100.0))
        if self.isEnabled:
            self.sliderSignal[str, int].emit("opacity", int(val))
    
### --------------------- TableModel ----------------------- 
class TableModel(QAbstractTableModel):  
    def __init__(self, data, hdr):   
        super().__init__()
        
        self._data = data
        self._header = hdr
             
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        elif index.column() == 0:
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignHCenter + Qt.AlignmentFlag.AlignVCenter
           
    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])
  
    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and \
            role == Qt.ItemDataRole.DisplayRole:
            return self._header[col]
        return None

### -------------------- dotsSliderPanel -------------------

