from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsShared      import keyMenu, pathMenu

### ------------------- dotsSliderPanel ----------------
SliderW, SliderH = 195, 682

### ----------------------------------------------------
''' dotsSliderPanel contains the TableGroup and the SliderGroup
    and the TableModel class used by the TableView '''
### --------------------------------------------------------
class SliderPanel(QWidget):

    sliderSignal = pyqtSignal(str, int)

    def __init__(self, parent):
        super().__init__()
        
        self.dots = parent

        self.setFixedSize(SliderW, SliderH) 
  
        self.isEnabled = False
        self.pathMenuSet = False

        layout = QVBoxLayout(self)        
        layout.addWidget(self.addTableGroup())     
        layout.addWidget(self.addSliderGroup())

        layout.setContentsMargins(0, 0, 0, 0)

### -----------------------------------------------------
    def enableSliders(self, bool): 
        self.isEnabled = bool
        self.rotateSldr.setValue(0)
        self.scaleSldr.setValue(100)
        self.opacitySldr.setValue(100)
        self.sliderGroup.setEnabled(bool)

### -----------------------------------------------------
    def addTableGroup(self):
        tableGroup = QGroupBox("")
        tableGroup.setFixedSize(SliderW,352)
        tableGroup.setStyleSheet("QGroupBox {\n"
            "background-color: rgb(250,250,250);\n"
            "border: .5px solid rgb(125,125,125);\n"
            "}")

        self.tableView = QTableView()
        self.tableView.setAlternatingRowColors(True) 
        self.tableView.setStyleSheet("QTableView {\n"
            "alternate-background-color: rgb(220,220,220);\n"
            "border: .5px solid rgb(200,200,200);\n"
            "background-color: white;\n"
            "}")  
        
        ## make it read-only
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(self.tableView.NoSelection)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tableView.horizontalHeader().setStyleSheet("QHeaderView {\n"
            "border: .5px solid rgb(200,200,200);\n"
            "font-size: 13px;\n"
            "}")  

        self.setTableModel(keyMenu)
        self.tableView.setColumnWidth(0, 45) 
        self.tableView.setColumnWidth(1, 107)

        layout = QVBoxLayout()    
        layout.addWidget(self.tableView, Qt.AlignHCenter|Qt.AlignVCenter)

        tableGroup.setLayout(layout)

        return tableGroup

### --------------------------------------------------------
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
                "}") 
            self.tableView.setStyleSheet("QTableView {\n"
                "alternate-background-color: rgb(220,220,220);\n"
                "}")  

    def toggleMenu(self):
        if self.pathMenuSet:
            self.setTableModel(keyMenu)
            self.pathMenuSet = False
        else:
            self.setTableModel(pathMenu)
            self.pathMenuSet = True

    def addSliderGroup(self):
        self.sliderGroup = QGroupBox("")
        self.sliderGroup.setFixedSize(SliderW,325)
        self.sliderGroup.setStyleSheet("QGroupBox {\n"
            "background-color: rgb(250,250,250);\n"
            "border: 1px solid rgb(125,125,125);\n"
            "}")

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
        
        mainLayout = QVBoxLayout() 

        hbox = QHBoxLayout()     
        hbox.addSpacing(10)  
        hbox.addWidget(rotateLabel, Qt.AlignTop|Qt.AlignLeft)
        hbox.addSpacing(10) 
        hbox.addWidget(scaleLabel, Qt.AlignTop|Qt.AlignRight) 
        hbox.addSpacing(0) 
        hbox.addWidget(opacityLabel, Qt.AlignTop|Qt.AlignRight) 

        hbox1 = QHBoxLayout()   
        hbox1.addSpacing(25) 
        hbox1.addWidget(self.rotateValue)
        hbox1.addSpacing(-5) 
        hbox1.addWidget(self.scaleValue)        
        hbox1.addSpacing(23) 
        hbox1.addWidget(self.opacityValue)  

        hbox2 = QHBoxLayout()
        hbox2.addStretch(2)    
        hbox2.addWidget(self.rotateSldr)
        hbox2.addStretch(2)
        hbox2.addWidget(self.scaleSldr)
        hbox2.addStretch(2)
        hbox2.addWidget(self.opacitySldr)
        hbox2.addStretch(1)

        mainLayout.addSpacing(5) 
        mainLayout.addLayout(hbox)
        mainLayout.addSpacing(2) 
        mainLayout.addLayout(hbox1)
        mainLayout.addSpacing(2) 
        mainLayout.addLayout(hbox2)

        mainLayout.addSpacing(10)
        mainLayout.setContentsMargins(0, 0, 5, 0)

        self.sliderGroup.setLayout(mainLayout)

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
    def __init__(self, data, hdr):
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
