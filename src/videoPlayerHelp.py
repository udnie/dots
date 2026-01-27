
from PyQt6.QtCore       import Qt, QTimer, QPoint
from PyQt6.QtGui        import QColor, QFont                      
from PyQt6.QtWidgets    import QWidget, QTableWidget, QAbstractItemView, \
                                QTableWidgetItem

from functools          import partial

from videoClipsWidget   import *

### ------------------ videoPlayerHelp.py -----------------
''' Tablewidgetsetup and help for videoPlayers and slideShow.
    The Menus selection isn't avaiable in SlideShow '''
### --------------------------------------------------------

helpMenuKeys = {   ## videoplayers
    'A':    'Apple/Academy 4X3',  
    'F':    'Full Screen 3X2',
    'H':    'Horiztonal HD 16X9',
    'S':    'Square',
    'T':    'Vertical 2X3',
    'U':    'Apple 3X4 Vertical',                  
    'V':    'Vertical 9X16',
    'C':    'To Clear',
    'L':    'Loop On/Off',
    'M':    'Menus',
    'W':    'Where am I?', 
    '>,  +,  ]':    'Scale Up',
    '<,  _,  [':    'Scale Down',
    'X, Q Escape':  'Quit/Exit',
    'Shift-S':      'Hide/Show Slider',
    'Aspect':       'Set Aspect (Button)',
    'Settings':     'ClipsMaker Settings',
    'Clips':        'Make a Clip',    
}

slideMenuKeys = {  ## slideShow
    'C':                'Clear Screen',  
    'F ':               'File Chooser', 
    'H ':               'Help Menu On/Off',
    'Right Arrow, N':   'Next Slide',
    'Left Arrow, B':    'Previous Slide',
    'O':                'Opening Layout',
    'L, R':             'Rotate 90.0',
    'S, SpaceBar':      'Slide Show',
    'T':                'Text On/Off',  
    'W':                'Where am I?', 
    '>,  +,  ]':        'Scale Up',
    '<,  _,  [':        'Scale Down',
    'Shift-B':          'Buttons Show/Hide', 
    'Shift-F':          'Frameless Hint', 
    'Shift-S':          'Select Files',
    'X, Q, Escape':     'Quit/Exit',
}

RH = 30
QL = QColor(230,230,230)  ## 10% gray
QC = QColor(210,210,210)  ## 18% gray
QH = QColor(220,220,220)  ## 14% gray

SlideShowKeys = ('B','C','F','H','N','O','R','L','S','T','W','X','[',']','Shift-B','Shift-F','Shift-S')

### -------------------------------------------------------- 
class VideoHelpWidget(QWidget):
### -------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
  
        self.parent = parent
        self.player = "two"
  
        self.label = QLabel()
        self.label.setStyleSheet("background: '#73fcd6'")

        vbox = QVBoxLayout()
        vbox.addWidget(self.label)

        quitButton = QPushButton("Click on Screen to Exit")
        quitButton.setMaximumWidth(200)
        quitButton.clicked.connect(self.parent.shared.closeVideoSlideMenus)

        hbox = QHBoxLayout()
        hbox.addWidget(quitButton, Qt.AlignmentFlag.AlignHCenter)
        
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        
        width, height = 1250, 850
        self.resize(width, height)
        
        x, y = int(self.parent.width()/2), int(self.parent.height()/2)
        p = self.parent.mapToGlobal(QPoint(x,y))
        x, y = int(p.x()), p.y()
              
        x = int(x - (width /2)) 
        y = int(y - (height /2)) 
 
        self.move(x,y)  
        self.show()
      
    def closeEvent(self, e):
        self.parent.shared.closeVideoSlideMenus()
        e.accept() 
        
    def mousePressEvent(self, e):  
        self.parent.shared.closeVideoSlideMenus()
        e.accept() 
             
### -------------------------------------------------------- 
class TableWidgetSetUp(QTableWidget):  ## duplicated as to not be reliant on dots
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
            'font-size: 13pt;\n' 
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
            item.setFont(QFont("Arial", 12))
                            
        if span == 2: 
            self.setSpan(row, 0, 1, 2) 
        elif span == 3:
            self.setSpan(row, 0, 1, 3) 
     
        return self.setItem(row, col, item)
    
### --------------------------------------------------------     
class VideoHelp(QWidget):  
### -------------------------------------------------------- 
    def __init__(self, parent, off=0, switch=''): 
        super().__init__()  
        
        self.parent = parent
        self.switch = switch
        
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.FramelessWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
    
        self.table = TableWidgetSetUp(100, 150, len(helpMenuKeys)+4)
        self.table.itemClicked.connect(self.clicked)
    
        width, height = 257, 666
        self.table.setFixedSize(width, height)
    
        str = "VideoPlayerOne" if self.parent.player == "one" else \
            "VideoPlayerTwo"
               
        self.table.setRow(0, 0, f'{str:<15}',QL,True, True, 2)
        
        row = 1  
        for k,  val in helpMenuKeys.items():
            if self.parent.player == "two" and row in (12,13,16):
                self.table.setRow(row, 0, k, QL,True,True)
                self.table.setRow(row, 1, "  " + val,QL,'',True)
            else:
                self.table.setRow(row, 0, k, '',True,True)
                self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1
                   
        self.table.setRow(row,     0,  f"{"Scale and Setting Aspect":<12}",QC,True,True, 2)
        self.table.setRow(row + 1, 0,  f"{"Don't Work in VideoPlayerTwo":<12}",QC,True,True, 2)
        self.table.setRow(row + 2, 0,  f"{'Right-Click or Click Here to Close':<12}",QL,True,True, 2)
        
        pwidth, pheight = self.parent.width(), self.parent.height() 
  
        if self.switch == '':   ## default
            p = self.parent.pos() 
            x = int(p.x() + (pwidth/2)) - int(width/2)   
            y = int(p.y() + (pheight/2)) - int(height/2) + 50  ## looks better for default
        else:
            x, y = int(pwidth/2), int(pheight/2)  ## from other source - dots
            p = self.parent.mapToGlobal(QPoint(x,y))
            x, y = int(p.x()), p.y()
            if off != 0: x += off
            x = int(x - (width /2)) 
            y = int(y - (height /2)) 
 
        self.table.move(x,y)  
        self.table.show()
        
    def clicked(self):
        if self.switch == '':
            help = self.table.item(self.table.currentRow(), 0).text().strip()
            match help: 
                case ('X, Q Escape'):
                    help = 'X'
                case ('>,  +,  ]'):
                    help = ']'
                case ('<,  _,  ['): 
                    help = '['     
            if help in VideoMenuKeys: 
                try:
                    QTimer.singleShot(25, partial(self.parent.VideoMenuKeys, help))
                except:
                    None
            self.parent.shared.closeHelpMenu()
        else:
            self.parent.shared.closeVideoSlideMenus()
  
    def tableClose(self):
        self.parent.helpFlag == False
        self.table.close()   
          
### --------------------------------------------------------     
class SlideShowHelp(QWidget): 
### -------------------------------------------------------- 
    def __init__(self, parent, off=0, switch=''): 
        super().__init__()  
        
        self.parent = parent
        self.switch = switch
                                     
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.FramelessWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
                                                                                        
        self.table = TableWidgetSetUp(115, 145, len(slideMenuKeys)+2)
        self.table.itemClicked.connect(self.clicked)

        width, height = 267, 547
        self.table.setFixedSize(width, height)  
         
        self.table.setRow(0, 0, f'{"SlideShow":<15}',QL,True, True, 2) 
        
        row = 1   
        for k,  val in slideMenuKeys.items():
            self.table.setRow(row, 0, k, '',True,True)
            self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1
                  
        self.table.setRow(row, 0,  f"{'Right-Click or Click Here to Close':<12}",QL,True,True, 2)
        
        pwidth, pheight = self.parent.width(), self.parent.height() 
  
        if self.switch != '':   ## help 
            x, y = int(pwidth/2), int(pheight/2)
            p = self.parent.mapToGlobal(QPoint(x,y))
            x, y = int(p.x()), p.y()
            if off != 0: x += off
            x = int(x - (width /2)) 
            y = int(y - (height /2)) 
        else:       
            p = self.parent.pos() 
            x = int(p.x() + (pwidth/2)) - int(width/2)   
            y = int(p.y() + (pheight/2)) - int(height/2)  
        
        self.table.move(x,y)  
        self.table.show()
        
    def clicked(self):
        if self.switch == '':
            help = self.table.item(self.table.currentRow(), 0).text().strip()
            if help == 'H': help = 'skip'  ## don't send it to shared
            match help:    
                case 'S, SpaceBar':  
                    help = 'S'
                case 'L, R':        
                    help = 'R'
                case 'Right Arrow, N':
                    help = 'N'
                case 'Left Arrow, B': 
                    help = 'B'               
                case '>,  +,  ]':
                    help = ']'
                case '<,  _,  [':  
                    help = '['
                case 'X, Q, Escape':
                    help = 'X'    
            if help in SlideShowKeys:
                try:
                    QTimer.singleShot(25, partial(self.parent.slideMenuKeys, help))
                except:
                    None
            if self.switch == '':  ## still in slideShow
                self.parent.closeHelpMenu()  
        else:
            self.parent.shared.closeVideoSlideMenus()  ## change of parent run by videoplayer
            
    def tableClose(self):
        self.parent.helpFlag = False 
        self.table.close()                                                                               
        
### ---------------------- that's all ---------------------- 

  
    
    
