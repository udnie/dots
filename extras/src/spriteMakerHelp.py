
from PyQt6.QtCore       import Qt, QTimer, QPoint
from PyQt6.QtGui        import QColor, QFont                      
from PyQt6.QtWidgets    import QWidget, QTableWidget, QAbstractItemView, \
                                QTableWidgetItem

from functools          import partial

### ------------------ spriteMakerHelp.py -----------------
helpMenuKeys = {  
    'F':    'Open Files',
    'O':    'OutLine',
    'P':    'Path Color',
    'E':    'Edit',
    'B':    'Background Preview',
    'H':    'Help',
    'C':    'To Clear',
    'S':    'Save',           
    'X, Q Escape':  'Quit/Exit',    
    'delete':   'Delete a Point',
    'option':   'Insert a Point',
    'shift/spacebar':   'Hold Magnifier',
    'up/right arrow':   'Next Point',
    'down/left arrow':  'Last Point', 
}

RH = 30
QL = QColor(230,230,230)  ## 10% gray
QC = QColor(210,210,210)  ## 18% gray
QH = QColor(220,220,220)  ## 14% gray
SD = QColor(115,252,214,125)  ## spindrift-lite

MenuKeys = ['F','O','P','E','B','C','H','S','X, Q Escape','shift',] + \
            ['option','delete', 'up/right arrow', 'shift/spacebar','down/left arrow']
        
### -------------------------------------------------------- 
class TableWidgetSetUp(QTableWidget):  ## duplicated from dots
### -------------------------------------------------------- 
    def __init__(self, a, b, c, cols3=0, fontSize=0):  ##  a, b, c - column widths 
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
            'font-size: 15pt;\n' 
            'font-family: Arial;\n' 
            'border: 3px solid dodgerblue;\n'
            'gridline-color: rgb(180,180,180);}')
          
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
            item.setFont(QFont("Arial", 14))  
                            
        if span == 2: 
            self.setSpan(row, 0, 1, 2) 
        elif span == 3:
            self.setSpan(row, 0, 1, 3) 
     
        return self.setItem(row, col, item)
    
### --------------------------------------------------------     
class SpriteHelp(QWidget):  
### -------------------------------------------------------- 
    def __init__(self, parent, off=0, switch=''): 
        super().__init__()  
        
        self.parent = parent
        self.switch = switch
        
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.FramelessWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
        
        self.table = TableWidgetSetUp(115, 165, len(helpMenuKeys)+3)
        self.table.itemClicked.connect(self.clicked)
    
        width, height = 287, 517
        self.table.setFixedSize(width, height)
    
        str = "SpriteMaker"           
        self.table.setRow(0, 0, f'{str:<15}',QL,True, True, 2)
        
        row = 1  
        for k,  val in helpMenuKeys.items(): 
            if row < 10:
                self.table.setRow(row, 0, k, '', True,True)
                self.table.setRow(row, 1, "  " + val, '', '',True)      
                row += 1
            else:
                if row == 10:
                    self.table.setRow(row, 0, f"{'Point Editing Commands':<22}",QC,True,True,2)
                    row += 1
                self.table.setRow(row, 0, k, '',True,True)
                self.table.setRow(row, 1, "  " + val,'','',True)
                row += 1
                   
        self.table.setRow(row, 0,  f"{'Right-Click or Click Here to Close':<12}",QL,True,True, 2)
        
        pwidth, pheight = self.parent.width(), self.parent.height() 
  
        if self.switch == '':   ## default
            p = self.parent.pos()  
            x = int(p.x() + (pwidth/2)) - int(width/2)   
            y = int(p.y() + (pheight/2)) - int(height/2) - 15
        else:
            x, y = int(pwidth/2), int(pheight/2)  ## copied over from dots
            p = self.parent.mapToGlobal(QPoint(x,y))
            x, y = int(p.x()), p.y()
            if off != 0: x += off
            x = int(x - (width /2)) 
            y = int(y - (height /2)) +25
 
        self.table.move(x,y)  
        self.table.show()
        
    def clicked(self):
        if self.switch == '':
            help = self.table.item(self.table.currentRow(), 0).text().strip()
            if help in MenuKeys:  
                match help: 
                    case 'X, Q Escape':
                        help = 'X'     
                    case 'delete':
                        help = 'del'
                    case 'option': 
                        help = 'opt'
                    case 'up/right arrow':
                        help = 'next'
                    case 'down/left arrow': 
                        help = 'last'     
                    case 'shift/spacebar':
                        help = 'shift'
                try:
                    QTimer.singleShot(25, partial(self.parent.shared, help)) 
                except:
                    None
            self.parent.works.closeHelpMenu()
            self.tableClose()
     
    def tableClose(self):
        self.parent.helpFlag = False 
        self.table.close()                                                                               
        
### ---------------------- that's all ---------------------- 

  
    
    
