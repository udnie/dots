
from functools          import partial

from PyQt6.QtCore       import QTimer
from PyQt6.QtGui		import QColor
            
from dotsTableModel     import TableWidgetSetUp
from dotsSideGig        import getVuCtr
          
bkgHelpKeys = {
    ' B ':      'Background Tablewidget',
    ' E ':      'Eye-dropper',  
    ' F ':      'Flop It', 
    ' H ':      'Help Menu',
    ' T ':      'Toggle Lock',
    ' \ ':      'Background Tag',
    'del':      'delete from screen',  
    'enter':    'move to the front',
    'return':   'move to the front',    
    'shift':    'move back one ZValue',
}
 
### --------------------- dotsBkgHelp ----------------------       
class BkgHelp:  
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()  
        
        self.bkgItem = parent  ## bkgItem
        self.canvas = self.bkgItem.canvas

 ### --------------------------------------------------------
    def openMenu(self):
        if self.bkgItem.bkgMaker.widget != None: 
            self.bkgItem.bkgMaker.closeWidget()
        
        self.tableWidget = TableWidgetSetUp(50, 250, len(bkgHelpKeys)+4, self.canvas)
        self.tableWidget.itemClicked.connect(self.clicked)    
    
        width, height = 285, 450
        self.tableWidget.setFixedSize(width, height)
    
        x, y = getVuCtr(self)
        x = int(x - width /2)
        y = int(y - height /2)
        
        self.tableWidget.move(x, y)
        color = QColor(220,220,220)
        
### --------------------------------------------------------          
        self.tableWidget.setSpan(0, 0, 1, 2) 
        self.tableWidget.setRow(0, 0, f'{"Background KeyBoard Help":<30}')
    
        row = 1
        for k , val in bkgHelpKeys.items():
            self.tableWidget.setRow(row, 0, k)
            self.tableWidget.setRow(row, 1, val, '', False)
            row += 1

        self.tableWidget.setSpan(row, 0, 1, 2) 
        self.tableWidget.setRow(row, 0, f'{"Hold Down Key - Click on Background":<45}')
                                
        self.tableWidget.setSpan(row+1, 0, 1, 2) 
        self.tableWidget.setRow(row+1, 0, f"{'Arrow Keys Can Modify Widget ScreenRates':<45}", color)

        self.tableWidget.setSpan(row+2, 0, 1, 2) 
        self.tableWidget.setRow(row+2, 0, f'{"Click Here to Close Menu":<30}')
 
        self.tableWidget.show()
  
    def clicked(self, help):
        help = self.tableWidget.item(self.tableWidget.currentRow(), 0).text().strip()
        if help == '\\': help = 'tag'
        if help in self.bkgItem.sharedKeys:
            QTimer.singleShot(25, partial(self.bkgItem.shared, help))         
        self.closeMenu()
       
    def closeMenu(self):
        self.tableWidget.close()
      
### --------------------- dotsBkgHelp ----------------------
     
     
        