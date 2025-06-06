
import os
from functools          import partial

from PyQt6.QtCore       import Qt, QTimer, QPoint
from PyQt6.QtGui        import QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets    import QTableView, QAbstractItemView

from dotsScreens        import getCtr
from dotsTableModel     import TableModel, Typelist, Types
from dotsShowFiles      import ShowFiles 
from dotsShowWorks      import ShowWorks 
from dotsSideGig        import MsgBox

MinRows = 5  ## to display
MaxRows = 17

MaxCols = 15  ## shown
MinCols = 7

ColWidth  = 100  ## seems to be the default size - see also 85px.
RowHeight = 27

ColumnWidths = [1,2,3,4,6,7,8,9,10,11,12,13,14,15]  ## set these columns width to 85px
##                      5,16...

Columns = {  ## set widths by number of columns
    21:  1605,
    18:  1505,
    16:  1415,
    12:  1065,
     8:   715,
     7:   630,
}

### --------------------------------------------------------
class TableView:  ## formats a json .play file to display missing files or not
### --------------------------------------------------------
    def __init__(self, parent, data, src=''):
        super().__init__()

        self.showbiz = parent
        self.canvas   = self.showbiz.canvas
        self.dots     = self.canvas.dots
 
        self.src = src  ## if it's 'table' then it's from the canvas - typed in 'J'
        self.data = data
    
        self.showWorks = ShowWorks(self.canvas)
        self.showFiles = ShowFiles(self.canvas) 
  
        self.loadingError = False
  
        self.hdr, self.cols = '', 0
        self.deleteKey = False
 
        self.selected = []  ## fileName and zValue used to delete selected rows rather than just by filename
        self.typelist = []  ## stores type, hdr, col
             
        self.Missingfiles = []  ## copy of missing files - showWorks has MissingFiles
        self.missing = []
         
### --------------------------------------------------------              
        self.tableView = QTableView()        
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionsMovable(True)
    
        self.tableView.horizontalScrollBar().setStyleSheet('QScrollBar:horizontal{\n' 
            'border:  9px solid rgb(185,185,185);\n'    
            'height: 18px;\n'  ## couldn't style the scroll handle so did this instead     
            'background-color: rgb(220,220,220)}')     
         
        self.tableView.verticalScrollBar().setStyleSheet('QScrollBar:vertical{\n' 
            'border: 9px solid rgb(185,185,185);\n'    
            'width: 18px;\n'          
            'background-color: rgb(220,220,220)}')
      
        self.tableView.horizontalHeader().setStyleSheet('QHeaderView::section{\n'
            'border: 1px solid rgb(240,240,240);\n'
            'text-align: center;\n' 
            'font-size: 13px;\n' 
            'background-color: rgb(225,225,225)}')  
           
        self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
                    
        ## dbl-click on any row to close the tableview except the header or white space
        self.tableView.doubleClicked.connect(self.bye)
     
        ##  or use 'C' to clear the tableview and not what it's in back of it
        self.shortcut = QShortcut(QKeySequence("C"), self.tableView)
        self.shortcut.activated.connect(self.bye)
        
        ##  or use 'J' to clear the tableview and not what it's in back of it
        self.shortcut = QShortcut(QKeySequence("J"), self.tableView)
        self.shortcut.activated.connect(self.bye)
        
        ## saves to file, but undeleted files won't disappear if saved from canvas rather than storyboard
        self.shortcut = QShortcut(QKeySequence("S"), self.tableView)
        self.shortcut.activated.connect(self.shuffle)
                         
        self.shortcut = QShortcut(QKeySequence("D"), self.tableView)
        self.shortcut.activated.connect(self.deleteSelectedRows) 
 
        self.tableView.setAlternatingRowColors(True) 
          
        self.makeTable(self.data)  ## eventually calls addTable unless loading error
                                    
### --------------------------------------------------------
    def addTable(self, data, miss, save):        
        width, height = self.widthHeight(data)
        
        self.missing = miss  ## used to delete
  
        file = os.path.basename(self.canvas.openPlayFile)
        self.dots.statusBar.showMessage(file)      
          
        self.tableView.setWindowTitle(f"C: to Close -- D: to Delete -- J: Toggles Viewer -- S: to Save")
        QTimer.singleShot(10000, partial(self.tableView.setWindowTitle, f"{file} - {len(data)-1} rows"))  
   
        self.model = TableModel(data, self.cols, self.hdr)   
        self.tableView.setModel(self.model)
      
        width = self.resetColumnWidths(width)
       
        ## make changes to the table layout by row - good to know - thanks Martin
        font = QFont("Arial", 14)  
        for i in save: 
            self.model.setHdrColor(i, '#e2e2e2')  ## make it look like a header
            self.model.setHdrFonts(i, font)  ## type instructions
            
        for i in miss: 
            self.model.setHdrColor(i, 'yellow')  ## missing files 
            self.model.setMisses(i, font)
            
        self.tableView.resize(width, height)
        self.tableView.move(self.reposition(height))  ## uses both width(self.cols) & height
        
        self.tableView.show()
        
        del data
 
### --------------------------------------------------------
    def deleteSelectedRows(self):  ## makes a list of selected rows by filename and zValue 
        if len(self.selected) > 0: 
            self.selected.clear() 
           
        if len(self.Missingfiles) > 0:
            if len({index.row() for index in self.tableView.selectionModel().selectedIndexes()}) > 0:    
                for indexes in sorted(self.tableView.selectionModel().selectedRows()):
                    if indexes.row() in self.missing:  ## only place self.missing is used
                        tmp = list(self.data[indexes.row()].values())
                        self.selected.append((tmp[0], tmp[4]))
            else:
                for tmp in self.Missingfiles:  ## delete all missing files
                    self.selected.append((tmp['fileName'], tmp['z'])) 
                       
        if len(self.selected) > 0:   
            self.deleteKey = True  
            sorted(self.selected, key=lambda x: x[1], reverse=True)  
            self.deleteFromTable() 
            
        self.makeTable(self.data)  ## refreshes tableview if anything was deleted or not
              
    def deleteFromTable(self):  ## doesn't affect the .play file unless saved    
        for s in self.selected:  
            for tmp in self.data:
                if s[0] == tmp['fileName'] and s[1] == tmp['z']:          
                    self.data.remove(tmp) 
                    break
                    
### --------------------------------------------------------                            
    def resetColumnWidths(self, width):  
        self.tableView.setColumnWidth(0, 135)
        for i in range(1, self.cols):  
            if i in ColumnWidths:  ## reduce column widths for these
                self.tableView.setColumnWidth(i, 85)  ## why is this so hard to find?      
        if Columns.get(self.cols):
            return Columns[self.cols]
        else:
            return width + 10
 
    def shuffle(self):  ## the save key
        if self.src != 'table':  
            self.showbiz.showtime.savePlay()  ## drops any missing files
        else:
            self.showWorks.saveToPlays(self.data)  ## retains remaining missing files when saved
 
    def reposition(self, height):
        g = getCtr()  ## reposition viewer if column number changes  
        c = Columns[self.cols]  ## replacing dictionary value prior to math
        x = int(g.x() - int(c/2))
        y = int(g.y() - int(height/2)-100)
        return QPoint(x, y)
 
    def bye(self): 
        self.tableView.setModel(None)  ## clears the table - a must do
        self.tableView.close() 
        self.tableView.src = ''  
        self.dots.statusBar.showMessage('')
                          
### --------------------------------------------------------          
    def makeTable(self, dlist):  ## first make the typelist 
        ## order .play file by Types = ['frame', 'pix', 'bkg', 'flat'] - see common
        ## flat and frame make it difficult to sort correctly as 'flat' comes before 'frame'
        typ, save = [], [] 
        self.typelist.clear()
        for types in Types:
            for tmp in dlist: 
                try:
                    if tmp['type'] == types:
                        if tmp['type'] not in typ:  ## set the types to watch
                            self.typelist.append(Typelist(tmp['type']))  ## Typelist is a class, type, hdr, len
                            typ.append(tmp['type'])  ## there can be only one   
                        save.append(tmp)  ## saving them by type  
                except: 
                    self.loadingError = True  ## read by showrunner 
                    MsgBox("TableMaker: Error Loading Play File", 5)
                    return                 
        dlist = save
        del save    
        self.setupHdrs(dlist)
 
### --------------------------------------------------------                    
    ## looking for the greatest number of .keys() per type and saving it as the type header
    def setupHdrs(self, dlist):
        self.cols = 0  ## just to make sure
        for typ in self.typelist: ## a list of Typelists - type, hdr, len
            for tmp in dlist:
                if tmp['type'] == typ.type:  ## read them all  
                    if len(tmp.keys()) > typ.len:  ## save it to typelist
                        typ.len = len(tmp.keys())
                        typ.hdr = list(tmp.keys())
                    if len(tmp.keys()) > self.cols:  ## save the most number of columns
                        self.cols = len(tmp.keys()) 
        self.unpackIt(dlist)
    
### -------------------------------------------------------- 
    def unpackIt(self, dlist):
        self.Missingfiles.clear()
        ## unpack dictionary values and save them as a list in data
        data, save, miss, k, first = [], [],[], 0, ''
        for tmp in dlist:  
            for typ in self.typelist:  ## do type header stuff
                if tmp['type'] == typ.type and typ.type != first:
                    if first == '':
                        self.hdr = typ.hdr  ## make this the top header 
                    else:
                        data.append(typ.hdr)  ## do this when the type changes 
                        save.append(k)  ## keep track of hdr row index
                        k += 1
                    first = typ.type   
                    
            if self.showFiles.fileNotFound(tmp):          
                miss.append(k) 
                self.Missingfiles.append(tmp)                
                                          
            data.append(list(tmp.values()))  
            k += 1  ## tracking the row number       
                          
        if self.deleteKey == True or self.src in('view', 'table') or len(self.Missingfiles) > 0:
            data.append(' ')  ## last line fix
            self.addTable(data, miss, save) 
            self.deleteKey == False    
             
        elif len(self.Missingfiles) == 0 and self.src != 'table':  ## nothing to show 
            return 
                 
### --------------------------------------------------------
    def widthHeight(self, data):
        rows   = len(data)
        width  = self.cols * ColWidth       
        height = (rows + 2) * RowHeight   
              
        if height > MaxRows * RowHeight:  
            height = MaxRows * RowHeight   
        elif height < MinRows * RowHeight:
            height = MinRows * RowHeight
        height += 10  ## add for header 
       
        width = self.cols * ColWidth 
        if self.cols > MaxCols: 
            width = MaxCols * ColWidth
        elif self.cols < MinCols: 
            width = MinCols * ColWidth
        width += 20         
        return width, height
           
### --------------------- dotsTableMaker -------------------
  


