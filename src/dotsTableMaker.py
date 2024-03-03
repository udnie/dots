
import os

from PyQt6.QtCore       import Qt
from PyQt6.QtGui        import QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets    import QTableView, QAbstractItemView


from dotsScreens        import getCtr
from dotsShared         import Types
from dotsTableModel     import TableModel, Typelist
from dotsShowFiles      import ShowFiles 
from dotsShowWorks      import ShowWorks 

MinRows = 5
MaxRows = 25

MaxCols = 15
MinCols = 7

ColWidth  = 100  ## seems to be the default sizes on my mac 
RowHeight = 30   

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
    
        self.showtime  = self.showbiz.showtime   
        self.showWorks = ShowWorks(self.canvas)
     
        self.showFiles = ShowFiles(self.canvas) 
  
        self.hdr, self.cols = '', 0
        self.deleteKey = False

        self.selected = []  ## fileName and zValue used to delete selected rows rather than just by filename
        self.typelist = []  ## stores type, hdr, col
             
        self.Missingfiles = []  ## copy of missing files
                
        self.tableView = QTableView()        
        self.tableView.horizontalHeader().setStretchLastSection(True)
    
        self.tableView.horizontalScrollBar().setStyleSheet('QScrollBar:horizontal{\n' 
            'background-color: rgb(225,225,225)}'); 
           
        self.tableView.verticalScrollBar().setStyleSheet('QScrollBar:vertical {\n' 
            'backround: rgb(245,245,245) ; \n'                                  
            'background-color: rgb(225,225,225)}');
        
        self.tableView.horizontalHeader().setStyleSheet('QHeaderView::section{\n'
            'background-color: rgb(225,225,225);\n'
            'border:  1px solid rgb(240,240,240); \n'
            'text-align: center; \n' 
            'font-size: 14px;}')  
                 
        self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
                 
        ## dbl-click on any row to close the tableview except the header or white space
        self.tableView.doubleClicked.connect(self.bye)
        
        ##  or use 'C' to clear the tableview and not what it's in back of it
        self.shortcut = QShortcut(QKeySequence("C"), self.tableView)
        self.shortcut.activated.connect(self.bye)
        
        ## saves to file, but undeleted files won't disappear if saved from canvas rather than storyboard
        self.shortcut = QShortcut(QKeySequence("S"), self.tableView)
        self.shortcut.activated.connect(self.shuffle)
                         
        self.shortcut = QShortcut(QKeySequence("D"), self.tableView)
        self.shortcut.activated.connect(self.deleteSelectedRows) 
 
        self.tableView.setAlternatingRowColors(True) 
                
        self.makeTable(self.data)  ## which calls addTable further down - lots of fussy stuff in between     
                    
### --------------------------------------------------------
    def addTable(self, data, miss, save):  ## called by self.unpackIt(data)       
        font = QFont("Arial", 14)    
        width, height = self.widthHeight(data)
        
        file = os.path.basename(self.canvas.openPlayFile)
        
        self.dots.statusBar.showMessage(file) 
        self.tableView.setWindowTitle(f"{file} - {len(data)} rows") 
        
        self.model = TableModel(data, self.cols, self.hdr)   
        self.tableView.setModel(self.model)
      
        ## make changes to the table layout by row - good to know - thanks Martin
        for i in save: 
            self.model.setHdrColor(i, '#e2e2e2')  ## make it look like a header
            self.model.setHdrFonts(i, font)  ## type instructions
            
        for i in miss: 
            self.model.setHdrColor(i, 'yellow')  ## missing files 
            self.model.setMisses(i, font)
            
        self.tableView.resize(width, height)
        self.tableView.show()
   
        p, g = self.tableView.pos(), getCtr()  ## move it up a bit higher                  
        self.tableView.move(p.x(), g.y() - int(height/2)-100) 
        
        del data
 
### --------------------------------------------------------
    def deleteSelectedRows(self):  ## makes a list of selected rows by filename and zValue   
        self.selected.clear() 
        if len({index.row() for index in self.tableView.selectionModel().selectedIndexes()}) > 0:    
            for indexes in sorted(self.tableView.selectionModel().selectedRows()):
                # print(self.model.data[indexes.row()][:5])
                self.updateSelected(self.model.data[indexes.row()])
        else:
            for tmp in self.Missingfiles:  ## delete all 
                self.selected.append((tmp['fileName'], tmp['z']))
            self.deleteKey = True
        if len(self.selected) > 0:             
            self.updateTables()   
            # print('make', list(self.selected))    
            self.makeTable(self.data)  ## writes a new tmp file if there's anything to write
     
    def updateSelected(self, tmp):  ## make a list of fileName and zValue  
        file  = tmp[0]  ## fileName
        zval = tmp[4]  ## the zValue
        if 'fileName' in file:  ## it's a hdr
            return
        self.selected.append((file, zval))
         
    def updateTables(self):  ## delete rows from view display and model data
        sorted(self.selected, key=lambda x: x[1], reverse=True)  
        self.deleteFromTable()  
                          
    def deleteFromTable(self):  ## doesn't effect actual file 
        for s in self.selected:
            for tmp in self.data:
                if s[0] == tmp['fileName'] and s[1] == tmp['z']:
                    self.data.remove(tmp) 
                    break   

    def shuffle(self):  ## the save key
        if self.src != 'table':  
            self.showtime.savePlay()  ## drops missing files if any
        else:
            self.showWorks.saveToPlays(self.data)  ## doesn't filter out missing
                        
### --------------------------------------------------------          
    def makeTable(self, dlist):  ## first make the typelist 
        ## order .play file by Types = ['frame', 'pix', 'bkg', 'flat'] - see common
        ## flat and frame make it difficult to sort correctly as 'flat' comes before 'frame'
        typ, save = [], [] 
        self.typelist.clear()
        for type in Types:
            for tmp in dlist: 
                if tmp['type'] == type:
                    if tmp['type'] not in typ:  ## set the types to watch
                        self.typelist.append(Typelist(tmp['type']))  
                        typ.append(tmp['type'])  ## there can be only one   
                    save.append(tmp)  ## saving them by type                        
        dlist = save
        del save      
        self.setupHdrs(dlist)
 
### --------------------------------------------------------                    
    ## looking for the greatest number of .keys() per type and saving it as the type header
    def setupHdrs(self, dlist):
        for typ in self.typelist: 
            for tmp in dlist:
                if tmp['type'] == typ.type:
                    if len(tmp.keys()) > typ.len:  ## save it to typelist
                        typ.len = len(tmp.keys())
                        typ.hdr = list(tmp.keys())
                    if len(tmp.keys()) > self.cols:  ## save most number of columns
                        self.cols = len(tmp.keys()) 
                    break      
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
            self.addTable(data, miss, save) 
            self.deleteKey == False     
            
        elif len(self.Missingfiles) == 0 and self.src != 'table':  ## nothing to show 
            return
                 
### --------------------------------------------------------
    def widthHeight(self, data):
        rows   = len(data)  
        width  = self.cols * ColWidth       
        height = (rows + 1) * RowHeight   
              
        if height > MaxRows * RowHeight:  
            height = MaxRows * RowHeight   
        elif height < MinRows * RowHeight:
            height = MinRows * RowHeight
        height += 20  ## header is roughly 20px
       
        width = self.cols * ColWidth 
        if self.cols > MaxCols: 
            width = MaxCols * ColWidth
        elif self.cols < MinCols: 
            width = MinCols * ColWidth
        width += 20         
        return width, height

    def bye(self): 
        self.tableView.setModel(None)  ## clears the table - a must do
        self.tableView.close() 
        self.tableView.src = ''
        self.dots.statusBar.showMessage('') 
           
### --------------------- dotsTableMaker -------------------
  


