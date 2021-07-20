from PyQt5.QtCore    import Qt, pyqtSignal, QAbstractTableModel
from PyQt5.QtWidgets import QWidget, QFrame, QSlider, QHBoxLayout, QVBoxLayout, \
                            QTableView, QHeaderView, QAbstractItemView, QLabel
                        
from dotsShared      import keyMenu, pathMenu

SliderW, SliderH, OffSet = 180, 685, 20


### --------------------- dotsSliderPanel ------------------
''' dotsSliderPanel contains the TableGroup and the SliderGroup
    and the TableModel class used by the TableView '''
### --------------------------------------------------------
class SliderPanel(QWidget):
### --------------------------------------------------------
    ## transfers slider output to initBkg
    sliderSignal = pyqtSignal(str, int)

    def __init__(self, parent):
        super().__init__()
        
        self.dots = parent

        self.setFixedSize(SliderW, SliderH) 

        self.isEnabled = False
        self.pathMenuSet = False

        layout = QVBoxLayout(self)        
        layout.addWidget(self.addTableGroup())     
        layout.addSpacing(20)
        layout.addWidget(self.addSliderGroup())

        layout.setContentsMargins(18, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

### --------------------------------------------------------
    def enableSliders(self, bool=False): 
        self.isEnabled = bool
        self.rotateSldr.setValue(0)
        self.scaleSldr.setValue(100)
        self.opacitySldr.setValue(100)
        self.sliderGroup.setEnabled(bool)
### --------------------------------------------------------
    def addTableGroup(self):
        self.tableView = QTableView()
        self.tableView.setFixedSize(SliderW-OffSet,350)
        self.tableView.setAlternatingRowColors(True) 
 
        ## make it read-only
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(self.tableView.NoSelection)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
    
        ## stylesheets set in self.setTableModel()
        self.setTableModel(keyMenu)
        self.tableView.setColumnWidth(0, 38) 
        self.tableView.setColumnWidth(1, 105)

        return self.tableView

### --------------------------------------------------------
    def toggleMenu(self):
        if self.pathMenuSet:
            self.setTableModel(keyMenu)
            self.pathMenuSet = False
        else:
            self.setTableModel(pathMenu)
            self.pathMenuSet = True

    def setTableModel(self, list):
        header = ['Keys', 'Action']
        model = TableModel(list, header)
        self.tableView.setModel(model)
        if list != keyMenu:
            header[1] = 'PathMaker'
            self.tableView.horizontalHeader().setStyleSheet(
                "QHeaderView::section{\n"
                "background-color: rgb(144,238,144);\n"
                "border: .5px solid lightgray;\n"
                "}")  
            self.tableView.setStyleSheet("QTableView {\n"
                "alternate-background-color: rgb(144,238,144);\n"
                "}")  
        else:
            header[1] = 'Action'
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
        self.sliderGroup.setFixedSize(SliderW-OffSet,335)

        rotateLabel = QLabel("Rotate")
        self.rotateValue = QLabel("  0")
        self.rotateValue.setAlignment(Qt.AlignLeft)

        scaleLabel = QLabel("Scale")
        self.scaleValue = QLabel("1.0")
        self.scaleValue.setAlignment(Qt.AlignHCenter)

        opacityLabel = QLabel("Opacity")
        self.opacityValue = QLabel("1.0")
        self.opacityValue.setAlignment(Qt.AlignLeft)

        self.rotateSldr = QSlider(Qt.Vertical, 
            minimum=-1, maximum=360,
            singleStep=1, value=1, 
            valueChanged=self.setRotate)  
        self.rotateSldr.setTickPosition(QSlider.TicksBothSides)
        self.rotateSldr.setTickInterval(90)
        
        self.scaleSldr = QSlider(Qt.Vertical, 
            minimum=50, maximum=225,
            singleStep=2, value=100, 
            valueChanged=self.setScale)
        self.scaleSldr.setTickPosition(QSlider.TicksBothSides)
        self.scaleSldr.setTickInterval(25)

        self.opacitySldr = QSlider(Qt.Vertical, 
            minimum=-1, maximum=100,
            singleStep=1, value=100, 
            valueChanged=self.setOpacity)
        self.opacitySldr.setTickPosition(QSlider.TicksBothSides)
        self.opacitySldr.setTickInterval(5)
            
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
        sbox.addWidget(self.rotateSldr) 
        sbox.addWidget(self.scaleSldr)                  
        sbox.addWidget(self.opacitySldr) 

        vbox = QVBoxLayout()  
        vbox.addLayout(lbox)
        vbox.addLayout(vabox)
        vbox.addLayout(sbox)

        self.sliderGroup.setLayout(vbox)
        self.sliderGroup.setContentsMargins(-5, 5, 0, 10)
        self.sliderGroup.setFrameStyle(QFrame.Box|QFrame.Plain)
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
class TableModel(QAbstractTableModel):  ## thanks stackoverflow 
    def __init__(self, data, hdr):      ## my mods
        super(TableModel,self).__init__()
        self.data = data
        self.header = hdr
 
    def rowCount(self, index):
        return len(self.data)

    def columnCount(self, index):
        return len(self.data[0])
  
    def data(self, index, role):
        if not index.isValid():
            return None
        elif index.column() == 0 and role == Qt.TextAlignmentRole:
            return Qt.AlignHCenter + Qt.AlignVCenter
        elif role == Qt.DisplayRole:
            return self.data[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

### -------------------- dotsSliderPanel -------------------
