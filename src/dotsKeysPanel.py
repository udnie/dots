
from PyQt6.QtCore       import Qt, QAbstractTableModel    
from PyQt6.QtGui        import QFont               
from PyQt6.QtWidgets    import QWidget, QVBoxLayout, QTableView, QHeaderView, \
                                QAbstractItemView
                                
from dotsShared         import common    

### --------------------- dotsKeysAndHelp ------------------
''' classes:  KeysPanel and TableModel '''              
### --------------------------------------------------------
class KeysPanel(QWidget):
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
        
        self.canvas = parent
        self.scene  = self.canvas.scene
                                                        
        self.storyKeys   = storyBoard()  ## list of storybroad keys
        self.pathKeys    = pathMaker()   ## list of path keys
        self.pathKeysSet = False
                                                 
        self.setFixedSize(common['SliderW'], common['SliderH']) 
        
        self.layout = QVBoxLayout(self)        
        self.layout.addWidget(self.addTableGroup(), Qt.AlignmentFlag.AlignVCenter) 
        self.layout.setContentsMargins(0, common['margin1'],0, common['margin2']+3)
        
        if common['Screen'] == '911':
            self.layout.setContentsMargins(0, common['margin1'],15, common['margin2']+3)
        
        self.layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            
### --------------------------------------------------------
    def toggleKeysMenu(self):  ## called thru sideCar 'K' key
        if self.pathKeysSet:
            self.setTableModel(self.storyKeys)
            self.pathKeysSet = False
        else:
            self.setTableModel(self.pathKeys)
            self.pathKeysSet = True 

    def addTableGroup(self):                   
        self.tableView = QTableView()
        self.setTableModel(self.storyKeys)  ## initial menu
         
        if not self.canvas.dots.Vertical:
            self.tableView.setFixedSize(common['SliderW']-common['OffSet'], \
                common['SliderH']-common['fix'])       
        
        self.tableView.setAlternatingRowColors(True) 
        self.tableView.setStyleSheet('border: 1px solid rgb(180,180,180)')
         
        font = QFont()
        font.setFamily('Arial')
        font.setPointSize(11)
        self.tableView.setFont(font)
                
        ## make it read-only
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.setSelectionMode(self.tableView.SelectionMode.NoSelection)
        
        self.tableView.verticalHeader().setVisible(False)        
        self.tableView.horizontalHeader().setSectionsMovable(True)
          
        self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.tableView.setColumnWidth(0, 34) 
        self.tableView.setColumnWidth(1, 90)
        
        return self.tableView
                                
### --------------------------------------------------------
    def setTableModel(self, list):
        header = [' Keys ', 'StoryBoard ']
        model = TableModel(list, header)
        self.tableView.setModel(model)
        
        if list != self.storyKeys:
            header[1] = 'PathMaker '
            self.tableView.horizontalHeader().setStyleSheet(
                'QHeaderView::section{\n'
                'background-color: rgb(115,252,214);\n'
                'border:  1px solid rgb(240,240,240); \n'
                'font-size: 11px;\n'
                '}')  
            self.tableView.setStyleSheet('QTableView {\n'
                'alternate-background-color: rgb(115,252,214);\n'
                'font-size: 11px;\n'
                '}')  
        else:
            header[1] = 'StoryBoard '
            self.tableView.horizontalHeader().setStyleSheet(
                'QHeaderView::section{\n'
                'background-color: rgb(220,220,220);\n'
                'border: 1px solid rgb(240,240,240);\n'
                'font-size: 11px;\n'
                '}') 
            self.tableView.setStyleSheet('QTableView {\n'
                'alternate-background-color: rgb(220,220,220);\n'
                'font-size: 11px;\n'
                '}') 
                        
        del list 
            
### --------------------------------------------------------    
class TableModel(QAbstractTableModel):  
### -------------------------------------------------------- 
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
    menu = (       ## a mix of canvas, storyboard, pixitems and bkgItems    
        ('F', 'Flop Selected'),
        ('G', 'Add/Hide Grid'),
        ('H', '+Shift Hide/UnHide'),
        ('M', 'Map Selected'),
        ('O', '+ShiftToggle Outlines'),
        ('P', 'Toggle Paths'),
        ('T', 'Toggle Tags'),
        ('L/R', 'Arrow Keys'),
        ('U/D', 'Arrow Keys'),
        ('Cmd', 'Drag to Select'),
        ('Del', 'Clk to Delete'),
        ('Opt', 'DbClk to Clone'),
        ('Opt', 'Drag Clones'), 
        ('Rtn', 'Enter to Front'),
        ('Shift', 'Clk to Flop'),     
        ('Shift', '+H Hide Selected'), 
        ('Shift', '+J Play Table'), 
        ('Shift', '+L ToggleLocks'),
        ('Shift', '+O Hide Outlines'),
        ('Shift', '+R Locks All'),
        ('Shift', '+S UnLinks All'),
        ('Shift', '+T TagSelected'),
        ('Shift', '+U Unlocks All'),  
        ('/', 'Clk to Back'),
        ('_/+', 'Rotate 1 deg'),  
        ('-/=', 'Rotate 15 deg'),
        ('[/]', 'Rotate 45 deg'),
        ('</>', 'Toggle Size'),     
        ('\\',  'Show this Tag'),
        ('A', 'Add a Background'), 
        ('A', 'Select All'),  
        ('C', 'Clear Canvas'),
        ('D', 'Display the Demo Menu'),
        ('D', 'Delete Selected'),
        ('J', 'JSON Viewer'),
        ('L', 'Load Play'), 
        ('P', 'Switch to PathMaker'), 
        ('R', 'Run/DemoHelp'),
        ('S', 'Stop/SceenMenu'),   
        ('U', 'UnSelect All'),
        ('W', 'Clear Widgets'),  
        ('X, Q', 'Escape to Quit'),     
    )
    return menu
      
def pathMaker():
    menu = (
        ('Shift', '+W Way Pts'),
        ('>',   'Shift WayPts +5%'),
        ('<',   'Shift WayPts -5%'),
        ('</>', 'Toggle Size'), 
        ('! ',  'Half Path Size'),
        ('@ ',  'Redistribute Pts'),        
        ('/',   'Path Color'),    
        ('} ',  'Flop Path'),
        ('{ ',  'Flip Path'),     
        (':/\'',  'Scale X'),
        (';/\'',  'Scale Y'),    
        ('U/D',   'Arrow Keys'),
        ('L/R',   'Arrow Keys'), 
        ('_/+', 'Rotate 1 deg'),  
        ('-/=', 'Rotate 15 deg'),
        ('[/]', 'Rotate 45 deg'),
        ('E',   'Edit Points'),
        ('del', 'Delete a Point'),     
        ('opt', 'Add a Point'), 
        ('shift',   'D Deletes Selected Pts'),
        ('L',   'Lasso'), 
        ('U',   'UnSelect Points'), 
        ('C',   'Center Path'),
        ('D',   'Delete Screen'), 
        ('N',   'New Path'),
        ('N',   'Closes Path'),   
        ('P',   'PathChooser'),
        ('R',   'Reverse Path'),
        ('S',   'Save Path'),
        ('T',   'Test'),
    )
    return menu

### --------------------- dotsKeysAndHelp ------------------

