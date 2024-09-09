
from functools          import partial

from PyQt6.QtCore       import QTimer

from dotsSideGig        import *
from dotsTableModel     import TableWidgetSetUp, QL, QC, QH
from dotsHelpButtons    import CanvasHelp, StoryHelp
from dotsPathWorks      import PathHelp

pixKeys = {
    ' F ':      'Flop It',   
    ' H ':      'Help Menu',
    ' T ':      'Toggle Lock',
    ' \ ':      'Background Tag',
    'del':      'delete from screen', 
    'enter':    'move to the front',
    'return':   'move to the front',   
    'shift':    'move back one ZValue', 
    'opt':      'Drag using Mouse to Clone',   
}
          
bkgHelpKeys = {
    ' B ':      'Background TableWidget',
    ' E ':      'Eye-Dropper',  
    ' F ':      'Flop It', 
    ' H ':      'Help Menu',
    ' T ':      'Toggle Lock',
    ' \ ':      'Background Tag',
    'del':      'delete from screen',  
    'enter':    'move to the front',
    'return':   'move to the front',    
    'shift':    'move back one ZValue',
}

shadowKeys = {
    ' ** ':     'DblClick Toggles Outline',
    ' H ':      'Help Menu',
    ' T ':      'Toggles Link', 
    ' / ':      'Update Shadow',
    ' \ ':      'Background Tag',
    'del':      'delete from screen', 
    'enter':    'move to the front',
    'return':   'move to the front',   
    'shift':    'move back one ZValue',      
}

## avoids a circular reference
SharedKeys =  ('H','T','/','del','tag','shift','enter','return') 

### --------------------- dotsHelpMonkey ------------------- 
''' classes: HelpMonkey, PixHelp, BkgHelp and ShadowHelp '''
### --------------------------------------------------------
    ## Canvas, StoryBoard and PathMaker, in helpButtons and pathWorks
    ## Demos, Screens and Animation Help,in helpMenus and pixWorks
    ## Frame, Flats and Matte Help,      in flat and frames and bkgMatte
    ## Widgets for Pixitems, Backgrounds.,  in helpMaker
### --------------------------------------------------------
class HelpMonkey:  ## the three scene items
### --------------------------------------------------------    
    def __init__(self, parent):
        super().__init__()
        
        self.canvas = parent 
        self.scene  = self.canvas.scene
        self.switch = str
        
    def buttonHelp(self, str=''):
        self.canvas.clear()
        self.canvas.bkgMaker.openFlatFile(paths['bkgPath'] + 'spin.bkg')
        
        self.canvasHelp = CanvasHelp(self, self.canvas, -350, str)
        self.storyHelp  = StoryHelp(self, self.canvas, 0, str)
        self.pathHelp   = PathHelp(self, self.canvas, 350, str)
    
    def screenitems(self, str=''): 
        self.canvas.clear()
        self.canvas.bkgMaker.openFlatFile(paths['bkgPath'] + 'spin.bkg')
        
        self.bkgHelp    = BkgHelp(self.canvas,0, str)
        self.shadowHelp = ShadowHelp(self.canvas, 350, str)
        self.pixHelp    = PixHelp(self.canvas, -350, str)
        
### --------------------------------------------------------     
class PixHelp: 
### -------------------------------------------------------- 
    def __init__(self, parent, off=0, str=''):
        super().__init__()  
   
        self.pixitem = parent ## pixitem   
        self.switch = str
                        
        self.table = TableWidgetSetUp(50, 205, len(pixKeys)+3)
        self.table.itemClicked.connect(self.clicked)    
    
        width, height = 261, 367
        self.table.setFixedSize(width, height)
                          
        self.table.setRow(0, 0, f'{"PixItem/Sprite Help Menu":<25}','',True, True, 2)
        
        row = 1
        for k , val in pixKeys.items():
            if row == 9:
                self.table.setRow(row, 0, k, QC, True,True)
                self.table.setRow(row, 1, "  " + val, QC,'',True)
            else:
                self.table.setRow(row, 0, k)
                self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1
        
        self.table.setRow(row, 0,  f'{"Hold Down Key and Click on Sprite  ":<34}',QL,True, True, 2)
        self.table.setRow(row + 1, 0, f"{'Click Here to Close':<22}",'',True,True, 2)
   
        x, y = getVuCtr(self.pixitem.canvas)
        if off != 0: x += off
  
        self.table.move(int(x - width /2), int(y - height /2))
        self.table.show()  
      
    def clicked(self):
        if self.switch == '':
            try:
                help = self.table.item(self.table.currentRow(), 0).text().strip()
                if help == '\\': help = 'tag'
                if help != 'H' and help in self.pixitem.sharedKeys:
                    QTimer.singleShot(25, partial(self.pixitem.shared, help))      
            except:
                None
        self.closeMenu()

    def closeMenu(self): 
        self.table.close()
        if self.switch !='':
            self.pixitem.canvas.setKeys('M')
    
### --------------------- dotsBkgHelp ----------------------       
class BkgHelp: 
### -------------------------------------------------------- 
    def __init__(self, parent, off=0, str=''):
        super().__init__()  
        
        self.bkgItem = parent 
        self.switch = str 

        self.table = TableWidgetSetUp(60, 215, len(bkgHelpKeys)+4)
        self.table.itemClicked.connect(self.clicked)    
    
        width, height = 282, 427
        
        self.table.setFixedSize(width, height)  
        self.table.setRow(0, 0, f'{"Background Help Menu":<22}','',True,True,2)
    
        row = 1
        for k , val in bkgHelpKeys.items():
            self.table.setRow(row, 0, k)
            self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1

        self.table.setRow(row, 0, f"{'Arrow Keys Can Modify ScreenRates ':<15}",QC,True,True, 2)
        self.table.setRow(row + 1, 0, f'{"Hold Down Key and Click on Background   ":<15}', QL,True, True, 2) 
        self.table.setRow(row + 2, 0, f"{'Click Here to Close':<25}",'',True,True, 2)

        x, y = getVuCtr(self.bkgItem.canvas)  
        if off != 0: x += off  
        
        self.table.move(int(x - width /2), int(y - height /2))    
        self.table.show()
  
    def clicked(self):
        if self.switch == '':
            try:
                help = self.table.item(self.table.currentRow(), 0).text().strip()
                if help == '\\': help = 'tag'
                if help != 'H' and help in self.bkgItem.sharedKeys:
                    QTimer.singleShot(25, partial(self.bkgItem.shared, help))         
            except:
                None
        self.closeMenu()
       
    def closeMenu(self):
        self.table.close()
        if self.switch !='':
            self.bkgItem.canvas.setKeys('M')  
     
### ------------------- dotsShadowHelp ---------------------    
class ShadowHelp:  
### --------------------------------------------------------
    def __init__(self, parent, off=0, str=''):
        super().__init__()  
        
        self.maker = parent  
        self.switch = str 
                         
        self.table = TableWidgetSetUp(50, 200, len(SharedKeys)+4)
        self.table.itemClicked.connect(self.clicked)   
 
        width, height = 256, 366
        self.table.setFixedSize(width, height)

        self.table.setRow(0, 0, f'{" Shadow Help Menu":<20}','',True,True, 2)

        row = 1
        for k , val in shadowKeys.items():
            self.table.setRow(row, 0, k)
            self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1
        
        self.table.setRow(row,     0, f'{"Hold Down Key and Click on Shadow   ":<35}',QL,True, True,2)       
        self.table.setRow(row + 1, 0, f'{"Click Here to Close  ":<22}','',True, True, 2)
          
        x, y = getVuCtr(self.maker.canvas) 
        if off != 0: x += off
        
        self.table.move(int(x - width /2), int(y - height /2))   
        self.table.show() 
 
    def clicked(self):
        if self.switch == '':
            try:
                help = self.table.item(self.table.currentRow(), 0).text().strip()
                if help == '\\': help = 'tag'
                if help != 'H' and help in SharedKeys:
                    QTimer.singleShot(25, partial(self.maker.shadow.shared, help))
            except:
                None
        self.closeMenu()

    def closeMenu(self):   
        self.table.close()  
        if self.switch !='':
            self.maker.canvas.setKeys('M')  
             
### -------------------- dotsHelpMonkey -------------------- 

                
