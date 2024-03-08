
from PyQt6.QtCore       import Qt, QAbstractTableModel
from PyQt6.QtGui        import QColor

from dotsShared         import Types

### --------------------- dotsTableModel -------------------
''' classses: Typelist and TableModel '''  
### --------------------------------------------------------  
class Typelist:  ## for type header 
### --------------------------------------------------------
    def __init__(self, type):  
        super().__init__()

        self.type = type    
        self.len  = 0
        self.hdr  = ''
        
### --------------------------------------------------------
class TableModel(QAbstractTableModel):
### --------------------------------------------------------
    def __init__(self, data, cols, hdr):
        super(TableModel, self).__init__()
   
        self.cols = cols
        self.data = data
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
                val = self.data[index.row()][index.column()]
                if isinstance(val, bool) and index.column() == 12:  ## scroller
                    if str(val) == 'True':        
                        return 'mirrored'
                    else:
                        return 'continuous' 
                return self.data[index.row()][index.column()]
            
            if role == Qt.ItemDataRole.BackgroundRole:  ## background color for hdrs
                color = self.rowheaders.get(index.row())  
                if color:      
                    return QColor(color)  ## combined hdrs and missing colors
                
            if role == Qt.ItemDataRole.FontRole:  ##  font size
                font = self.rowfonts.get(index.row())  
                if font:      
                    return font
                    
            if role == Qt.ItemDataRole.TextAlignmentRole:  ## missing files   
                val = self.data[index.row()][index.column()]  
                
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
                val = self.data[index.row()][index.column()] 
                      
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
        return len(self.data)

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
        
    
        
                 