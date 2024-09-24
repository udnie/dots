
from functools          import partial

from PyQt6.QtCore       import QTimer

from dotsSideGig        import *
from dotsTableModel     import TableWidgetSetUp, QL, QC, QH

pixKeys = {
    ' F ':      'Flop It',   
    ' H ':      'This Help Menu',
    ' T ':      'Toggle Lock',
    ' \\ ':     'Background Tag',
    'del':      'delete from screen', 
    'enter':    'move to the front',
    'return':   'move to the front',   
    'shift':    'move back one ZValue', 
    'opt':      'Drag using Mouse to Clone', 
     '_/+':  'Rotate 1 deg',  
    '-/=':  'Rotate 15 deg',
    '[/]':  'Rotate 45 deg',
    '</>':  'Toggle Size',  
}
          
bkgHelpKeys = {
    ' B ':      'Background TableWidget',
    ' E ':      'Eye-Dropper',  
    ' F ':      'Flop It', 
    ' H ':      'This Help Menu',
    ' T ':      'Toggle Lock',
    ' \\ ':     'Background Tag',
    'del':      'delete from screen',  
    'enter':    'move to the front',
    'return':   'move to the front',    
    'shift':    'move back one ZValue',
}

shadowKeys = {
    ' ** ':     'DblClick Toggles Outline',
    ' H ':      'This Help Menu',
    ' T ':      'Toggles Link', 
    ' / ':      'Update Shadow',
    ' \\ ':     'Background Tag',
    'del':      'delete from screen', 
    'enter':    'move to the front',
    'return':   'move to the front',   
    'shift':    'move back one ZValue',      
}

## avoids a circular reference
SharedKeys =  ('H','T','/','del','tag','shift','enter','return') 

### --------------------- dotsHelpMonkey ------------------- 
''' classes: PixHelp, BkgHelp and ShadowHelp '''
### --------------------------------------------------------
    ## Canvas and StoryBoard Menus in helpButtons
    ## PathHelp2, PixHelp2, StoryHelp2 in helpDesk    
    ## Demos, Screens Menus in helpMenus
    ## Sprites, Background and Shadow Menus in helpMonkey
    ## Widgets for Pixitems, Backgrounds., in helpMaker
    ## Animation Menu in pixWork
    ## Frames and Flats Menu in frames and flats
    ## Matte Menu in bkgMatte    
    ## PathMaker Menu in pathWorks    
### --------------------------------------------------------     
class PixHelp: 
### -------------------------------------------------------- 
    def __init__(self, parent, off=0, switch=''):
        super().__init__()  
   
        self.pixitem = parent ## pixitem   
        self.canvas = self.pixitem.canvas
        
        self.switch = switch
                      
        self.table = TableWidgetSetUp(50, 190, len(pixKeys)+6)
        self.table.itemClicked.connect(self.clicked)    
    
        width, height = 246, 577
        self.table.setFixedSize(width, height)
                          
        self.table.setRow(0, 0, f'{"Sprite/PixItem Help Menu":<25}','',True, True, 2)
        
        row = 1
        for k , val in pixKeys.items():    
            if row == 10:
                self.table.setRow(row,      0, f'{"These Commands Require A Keyboard     "}',QC,True,True, 2) 
                self.table.setRow(row + 1,  0, f'{"And Sprites Are Selected "}',QC,True,True, 2) 
                row = 12  
                
            if row >= 12:
                self.table.setRow(row, 0, k, QL,True,True)
                self.table.setRow(row, 1, "  " + val, QL,'',True)
            else:                  
                self.table.setRow(row, 0, k, '',True,True)
                self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1
        
        self.table.setRow(row,      0, f'{"Hold Down Key and Click on Sprite   ":<35}',QC,True, True,2) 
        self.table.setRow(row + 1,  0, f'{"Enter Key or Select From Above   "}',QH,True,True, 2)     
        self.table.setRow(row + 2,  0,  f"{'Click Here to Close':<22}",'',True,True, 2)
    
        x, y = getVuCtr(self.pixitem.canvas)  ## need the 'y'
    
        if self.switch != 'pix':
            if off != 0: x += off
            x = int(x - width /2)  
            y = int(y - height /2) 
        else: 
            x, y = self.pixitem.works.makeXY()  ## for 'y'
            y = int(y - 100)
            b = self.pixitem.boundingRect()
            width = int(b.width() + 20)
            x = int(off + width)
     
        self.table.move(x, y)     
        self.table.show()  
      
    def clicked(self):
        if self.switch == '' or self.switch == 'pix':
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
        if self.switch !='' and self.switch != 'pix':
            self.pixitem.canvas.setKeys('N')
    
### --------------------- dotsBkgHelp ----------------------       
class BkgHelp: 
### -------------------------------------------------------- 
    def __init__(self, parent, off=0, switch=''):
        super().__init__()  
        
        self.bkgItem = parent 
        self.switch = switch 

        self.table = TableWidgetSetUp(50, 200, len(bkgHelpKeys)+4)
        self.table.itemClicked.connect(self.clicked)    
    
        width, height = 256, 427
        
        self.table.setFixedSize(width, height)  
        self.table.setRow(0, 0, f'{"Background Help Menu":<22}','',True,True,2)
    
        row = 1
        for k , val in bkgHelpKeys.items():
            self.table.setRow(row, 0, k,'',True,True)
            self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1

        self.table.setRow(row, 0, f"{'Arrow Keys Can Modify ScreenRates ':<15}",QC,True,True, 2)
        self.table.setRow(row + 1, 0, f'{"Hold Down Key and Click on Background   ":<15}', QL,True, True, 2) 
        self.table.setRow(row + 2, 0, f"{'Click Here to Close':<22}",'',True,True, 2)

        x, y = getVuCtr(self.bkgItem.canvas)  
        if off != 0: x += off  
        
        self.table.move(int(x - width /2), int(y - height /2)+10)    
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
            self.bkgItem.canvas.setKeys('N')  
     
### ------------------- dotsShadowHelp ---------------------    
class ShadowHelp:  
### --------------------------------------------------------
    def __init__(self, parent, off=0, switch=''):
        super().__init__()  
        
        self.maker = parent  
        self.switch = switch 
                         
        self.table = TableWidgetSetUp(50, 180, len(SharedKeys)+4)
        self.table.itemClicked.connect(self.clicked)   
 
        width, height = 236, 366
        self.table.setFixedSize(width, height)

        self.table.setRow(0, 0, f'{" Shadow Help Menu":<20}','',True,True, 2)

        row = 1
        for k , val in shadowKeys.items():
            self.table.setRow(row, 0, k,'',True,True)
            self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1
        
        self.table.setRow(row,     0, f'{"Hold Down Key and Click on Shadow   ":<35}',QL,True, True,2)       
        self.table.setRow(row + 1, 0, f'{"Click Here to Close  ":<22}','',True, True, 2)
    
        x, y = getVuCtr(self.maker.canvas) 

        if self.switch != 'pix':
            if off != 0: x += off
            x = int(x - width /2)  
            y = int(y - height /2) 
        else: 
            x, y = self.maker.getXY() 
            y = int(y - 80)     
            b = self.maker.shadow.boundingRect()
            width = int(b.width() + 20)
            x = int(x + width)       
    
        self.table.move(x, y)          
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
        if self.switch !='' and self.switch != 'pix':
            self.maker.canvas.setKeys('N')  
             
### -------------------- dotsHelpMonkey -------------------- 

                
