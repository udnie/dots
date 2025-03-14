
from PyQt6.QtCore       import Qt, QAbstractTableModel
from PyQt6.QtGui        import QColor, QFont
from PyQt6.QtWidgets    import QTableWidget, QTableWidgetItem, QAbstractItemView

CTR = True

QL = QColor(230,230,230)  ## 10% gray
QC = QColor(210,210,210)  ## 18% gray
QH = QColor(220,220,220)  ## 14% gray

RH = 30

Types = ['frame', 'pix', 'video', 'bkg', 'flat']  ## used by tableMaker

### --------------------- dotsTableModel -------------------
''' classes: TableWidgetSetUp, Typelist and TableModel '''  
### --------------------------------------------------------  
class Typelist:  ## for type header 
### --------------------------------------------------------
    def __init__(self, typ):  
        super().__init__()

        self.type = typ    
        self.len  = 0
        self.hdr  = ''

### -------------------------------------------------------- 
class TableWidgetSetUp(QTableWidget):  ## used by help menus 
### -------------------------------------------------------- 
    def __init__(self, a, b, c, cols3=0, fontSize=0):
        super().__init__()   
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
                      
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        if cols3 == 0:
            self.setRowCount(c) 
            self.setColumnCount(2)
            
            self.setColumnWidth(0, a) 
            self.setColumnWidth(1, b)
        elif cols3 > 0:
            self.setRowCount(cols3) 
            self.setColumnCount(3)
            
            self.setColumnWidth(0, a) 
            self.setColumnWidth(1, b)
            self.setColumnWidth(2, c) 
      
        self.setStyleSheet('QTableWidget{\n'   
            'background-color: rgb(250,250,250);\n'                 
            'font-size: 12pt;\n' 
            'font-family: Arial;\n' 
            'border: 3px solid dodgerblue;\n'
            'gridline-color: silver;}')  
          
        self.type = 'widget'
        self.setAccessibleName('widget')
        self.height = fontSize
        
    def setRow(self, row, col, str, color='', ctr=False, bold=False, span=0):
        self.setRowHeight(row, self.height) if self.height > 0 else self.setRowHeight(row, RH)
        item = QTableWidgetItem(str)
        
        if color != '': item.setBackground(QColor(color))
        if ctr: item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if bold: 
            item.setFont( QFont("Arial", 13, 58))
        elif span == 7:
            item.setFont(QFont("Arial", 14, bold))
        else:
            item.setFont(QFont("Arial", 12))
                            
        if span == 2: 
            self.setSpan(row, 0, 1, 2) 
        elif span == 3:
            self.setSpan(row, 0, 1, 3) 
     
        return self.setItem(row, col, item)
                             
### --------------------------------------------------------
class TableModel(QAbstractTableModel):  ## used by tableMaker
### --------------------------------------------------------
    def __init__(self, data, cols, hdr):
        super(TableModel, self).__init__()
   
        self.cols = cols
        self._data = data
        self.idx = 0
        self.target = -1
        
        self.header = hdr  ## first row - column titles
        
        ## holds row indexs to modify both color and alignment 
        self.rowfonts = {}       
        self.rowheaders = {}  
        self.rowMiss = {}
    
    def data(self, index, role): 
        try:   
            if role == Qt.ItemDataRole.DisplayRole: 
                val = self._data[index.row()][index.column()]
                if isinstance(val, bool) and index.column() == 12:  ## scroller
                    if str(val) == 'True':        
                        return 'mirrored'
                    else:
                        return 'continuous' 
                elif isinstance(val, str) and val[-1] == '/':
                    return val[5:-1]
                return self._data[index.row()][index.column()]
            
            if role == Qt.ItemDataRole.BackgroundRole:  ## background color for hdrs
                color = self.rowheaders.get(index.row())  
                if color:      
                    return QColor(color)  ## combined hdrs and missing colors
                
            if role == Qt.ItemDataRole.FontRole:  ##  font size
                font = self.rowfonts.get(index.row())  
                if font:      
                    return font
                    
            if role == Qt.ItemDataRole.TextAlignmentRole:  ## missing files   
                val = self._data[index.row()][index.column()]  
                
                if self.rowMiss.get(index.row()):  
                    if  isinstance(val, bool):
                        return Qt.AlignmentFlag.AlignLeft + Qt.AlignmentFlag.AlignVCenter
                    
                    elif isinstance(val, int) or isinstance(val, float) or val[0] == '#':
                        return Qt.AlignmentFlag.AlignRight + Qt.AlignmentFlag.AlignVCenter
                    
                    elif val in Types and index.column() == 1:
                        return Qt.AlignmentFlag.AlignHCenter + Qt.AlignmentFlag.AlignVCenter
                    
                    elif isinstance(val, str) or not isinstance(val, str):
                        return Qt.AlignmentFlag.AlignLeft + Qt.AlignmentFlag.AlignVCenter 
                    
            if role == Qt.ItemDataRole.TextAlignmentRole:  
                val = self._data[index.row()][index.column()] 
                      
                if self.rowheaders.get(index.row()): ## center 'type' header titles    
                    return Qt.AlignmentFlag.AlignCenter    
                  
                elif  isinstance(val, bool):  ## non-header alignments
                    return Qt.AlignmentFlag.AlignLeft + Qt.AlignmentFlag.AlignVCenter   
                     
                elif isinstance(val, int) or isinstance(val, float) or val[0] == '#':
                    return Qt.AlignmentFlag.AlignRight + Qt.AlignmentFlag.AlignVCenter  
                    
                elif val in Types and index.column() == 1:
                    return Qt.AlignmentFlag.AlignHCenter + Qt.AlignmentFlag.AlignVCenter
                   
                elif not isinstance(val, str):
                    return Qt.AlignmentFlag.AlignLeft + Qt.AlignmentFlag.AlignVCenter    
        except:
            return  ## required for forcing the column width 
                      
    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return self.cols 
       
    def setHdrColor(self, row, color):  ## happens in tableView - tags a row by index
        self.rowheaders[row] = color
        
    def setHdrFonts(self, row, font):  
        self.rowfonts[row] = font 
        
    def setMisses(self, row, font):  
        self.rowMiss[row] = font 
        
    def headerData(self, col, orientation, role):
        try:
            if orientation == Qt.Orientation.Horizontal:
                if role == Qt.ItemDataRole.DisplayRole:       
                    return self.header[col]
        except:
            return  ## because the header may not match longest set of values
      
### --------------------- dotsTableModel ------------------- 
 
        
        # print(typ.type, typ.len, list(typ.hdr)[:12]) 
          
        # s = f'{self.hdr}\t{rows}\t{rows + self.hdr}\t'
        # t = f'{self.cols}\t{self.cols * (rows + self.hdr)}'  
        # print(s + t)
  
        # atmp = list(tmp.items())[:2] 
        # atmp.append(('x', pathStr))  ## for tableview display 
        # atmp =  atmp + list(tmp.items())[3:]  ## glue it back together
        # tmp  = dict(atmp)    
  
        #  f"({pt.x():.2f}, {pt.y():.2f})  %{pct:.2f}   {idx}"
  
  
        ## for k in newlist: print(k['fileName'], k['z'])         
        # dlist = sorted(dlist, key=lambda x: x['z'], reverse=True)  ## sort by 'z' val  
  
        #    if self.Lostfiles.hastmp:
        #         if rows := self.Lostfiles.returnMissingFiles():
        #             if src != 'table':
        #                 dlist = rows
        
    
        
                 