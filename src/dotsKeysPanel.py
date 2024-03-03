
from PyQt6.QtCore       import Qt, QAbstractTableModel    
from PyQt6.QtGui        import QFont               
from PyQt6.QtWidgets    import QWidget, QVBoxLayout, QTableView, QHeaderView, \
                                QAbstractItemView
                                
from dotsShared         import common                           

### ---------------------- dotskeysPanel -------------------
''' dotskeysPanel contains TableGroup and TableModel class 
    used by the TableView '''       
### --------------------------------------------------------
class KeysPanel(QWidget):
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
        
        self.canvas = parent
                                                        
        self.keyMenu     = storyBoard()
        self.pathMenu    = pathMaker()
        self.pathMenuSet = False
                        
        self.setFixedSize(common['SliderW'], common['SliderH']) 
        
        self.layout = QVBoxLayout(self)        
        self.layout.addWidget(self.addTableGroup(), Qt.AlignmentFlag.AlignVCenter) 
        self.layout.setContentsMargins(0, common['margin1'],0, common['margin2']+3)
        
        if common['Screen'] == '912':
            self.layout.setContentsMargins(0, common['margin1'],15, common['margin2']+3)
        
        self.layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            
### --------------------------------------------------------
    def toggleMenu(self):  ## called thru sideCar 'K' key
        if self.pathMenuSet:
            self.setTableModel(self.keyMenu)
            self.pathMenuSet = False
        else:
            self.setTableModel(self.pathMenu)
            self.pathMenuSet = True 

    def addTableGroup(self):                   
        self.tableView = QTableView()
        self.setTableModel(self.keyMenu)  ## initial menu
         
        self.tableView.setFixedSize(common['SliderW']-common['OffSet'], \
            common['SliderH']-common['fix'])        
        self.tableView.setAlternatingRowColors(True) 
        self.tableView.setStyleSheet('border: 1px solid rgb(180,180,180)')
         
        font = QFont()
        font.setFamily('Arial')
        font.setPointSize(12)
        self.tableView.setFont(font)
                
        ## make it read-only
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.setSelectionMode(self.tableView.SelectionMode.NoSelection)
        
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        
        self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.tableView.setColumnWidth(0, 46) 
        self.tableView.setColumnWidth(1, 108)
        
        return self.tableView
                                
### --------------------------------------------------------
    def setTableModel(self, list):
        header = [' Keys ', 'StoryBoard ']
        model = TableModel(list, header)
        self.tableView.setModel(model)
        
        if list != self.keyMenu:
            header[1] = 'PathMaker '
            self.tableView.horizontalHeader().setStyleSheet(
                'QHeaderView::section{\n'
                'background-color: rgb(144,238,144);\n'
                'border:  1px solid rgb(240,240,240); \n'
                'font-size: 12px;\n'
                '}')  
            self.tableView.setStyleSheet('QTableView {\n'
                'alternate-background-color: rgb(144,238,144);\n'
                'font-size: 12px;\n'
                '}')  
        else:
            header[1] = 'StoryBoard '
            self.tableView.horizontalHeader().setStyleSheet(
                'QHeaderView::section{\n'
                'background-color: rgb(220,220,220);\n'
                'border: 1px solid rgb(240,240,240);\n'
                'font-size: 12px;\n'
                '}') 
            self.tableView.setStyleSheet('QTableView {\n'
                'alternate-background-color: rgb(220,220,220);\n'
                'font-size: 12px;\n'
                '}') 
                        
        del list 
            
### --------------------------------------------------------    
class TableModel(QAbstractTableModel):  
    def __init__(self, data, hdr):   
        super().__init__()
        
        self.data = data
        self.header = hdr
             
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.data[index.row()][index.column()]
        elif index.column() == 0:
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignHCenter + Qt.AlignmentFlag.AlignVCenter
           
    def rowCount(self, index):
        return len(self.data)

    def columnCount(self, index):
        return len(self.data[0])
  
    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and \
            role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]
        return None
  
### --------------------------------------------------------      
def storyBoard():
    menu = ( ## pixitems and bkgitems
        ('A', 'Select All'),   
        ('C', 'Clear Canvas'),        
        ('D', 'Delete Selected'),
        ('F', 'Flop Selected'),
        ('G', 'Add/Hide Grid'),
        ('H', 'Hide/UnHide'),
        ('J', 'JSON Viewer'),
        ('K', 'Toggle KeyList'),
        ('L', 'Load Play'),
        ('M', 'Map Selected'),
        ('O', 'Toggle Outlines'),
        ('P', 'Toggle Paths'),
        ('R', 'Run/DemoMenu'),
        ('S', 'Stop/SceenMenu'),
        ('T', 'Toggle Tags'),
        ('U', 'UnSelect All'),
        ('W', 'Clear Widgets'),   
        ('L/R', 'Arrow Keys'),
        ('U/D', 'Arrow Keys'),
        ('X, Q', 'Escape to Quit'),
        ('Cmd', 'Drag to Select'),
        ('Del', 'Clk to Delete'),
        ('Opt', 'DbClk to Clone'),
        ('Opt', 'Drag Clones'), 
        ('Opt', 'Show this Tag'),
        ('Rtn', 'Enter to Front'),
        ('Shift', 'Clk to Flop'),   
        ('Shift', '+B Dump Bkgs'),   
        ('Shift', '+H Hide Selected'), 
        ('Shift', '+J Play Table'), 
        ('Shift', '+L ToggleLocks'),
        ('Shift', '+O Hide Outlines'),
        ('Shift', '+R Locks All'),
        ('Shift', '+T TagSelected'),
        ('Shift', '+U Unlocks All'),  
        ('\'', 'Toggle this lock'),
        ('/', 'Clk to Back'),
        (',', 'Clk Back One Z'),
        ('.', 'Clk Up One Z'),
        ('_/+', 'Rotate 1 deg'),  
        ('-/=', 'Rotate 15 deg'),
        ('[/]', 'Rotate 45 deg'),
        ('</>', 'Toggle Size'),
    )
    return menu
      
def pathMaker():
    menu = (
        ('C', 'Center Path'),
        ('D', 'Delete Screen'), 
        ('E', 'Edit Points'),
        ('F', 'Files'),
        ('L', 'Lasso'),
        ('N', 'New Path'),
        ('P', 'Path Chooser'),
        ('R', 'Reverse Path'),
        ('S', 'Save Path'),
        ('T', 'Test'),
        ('U', 'UnSelect Points'),
        ('V', 'View Points'),
        ('cmd',   'Closes Path'),   
        ('del',   'Delete a Point'),     
        ('opt',   'Add a Point'),
        ('Shift', '+D Delete Pts'),
        ('Shift', '+W Way Pts'),
        ('>',   'Shift WayPts +5%'),
        ('<',   'Shift WayPts -5%'),
        ('</>', 'Toggle Size'), 
        ('! ',  'Half Path Size'),
        ('@ ',  'Redistribute Pts'),        
        ('/',   'Path Color'),    
        ('} ',  'Flop Path'),
        ('{ ',  'Flip Path'),     
        (':/\'', 'Scale X'),
        (';/\'', 'Scale Y'),    
        ('U/D',  'Arrow Keys'),
        ('L/R',  'Arrow Keys'), 
        ('_/+',  'Rotate 1 deg'),  
        ('-/=',  'Rotate 15 deg'),
        ('[/]',  'Rotate 45 deg'),
    )
    return menu

### --------------------- dotsKeysPanel --------------------


