
from functools          import partial

from PyQt6.QtCore       import QTimer
from PyQt6.QtGui        import QKeySequence

from dotsSideGig        import *
from dotsTableModel     import TableWidgetSetUp, QL, QC, QH

pixKeys = {  ## sprites
    ' F ':      'Flop It',   
    ' H ':      'This Help Menu',
    ' T ':      'Toggle Lock',
    ' \\ ':     'Background Tag',
    'del':      'delete from screen', 
    'enter':    'move to the front',
    'return':   'move to the front',   
    'shift':    'move back one ZValue', 
    'opt':      'drag Mouse to Clone', 
     '_/+':  'Rotate 1 deg',  
    '-/=':  'Rotate 15 deg',
    '[/]':  'Rotate 45 deg',
    '{/}':  'Rotate 90 deg',
    '</>':  'Toggle Size',  
}
          
bkgHelpKeys = {
    ' B ':      'Background Tracker',
    ' E ':      'Eye-Dropper',  
    ' F ':      'Flop It', 
    ' H ':      'This Help Menu',
    ' T ':      'Toggle Lock',
    ' \\ ':     'Background Tag',
    'del':      'delete from screen',  
    'enter':    'move to the front',
    'return':   'move to the front',    
    'shift':    'move to the back',
    'Shift-B':  'Mirror Background',
    'Option-B': 'Mirror/Flip Background',
    'Shift-U':  'UnLock All Screen Items',    
}

shadowKeys = {
    ' H ':      'This Help Menu',
    ' T ':      'Toggles Link', 
    ' / ':      'Refresh Shadow',
    ' \\ ':     'Background Tag',
    'del':      'Delete from screen', 
    'enter':    'Move to the front',
    'return':   'Move to the front',   
    'shift':    'Move back 3 zvalues',  ## otherwise it still covers the sprite
    'dblclk':   'Dbl-Click Toggles Outline',    
}

## avoids a circular reference -these are used by shadow 
SharedKeys = ('H','T','/','del','tag','shift','enter','return', 'dblclk') 

### --------------------- dotsHelpMonkey ------------------- 
''' classes: PixHelp, BkgHelp and ShadowHelp '''
### --------------------------------------------------------
    ## Animation Menu in pixWork
    ## Canvas and StoryBoard Menus in helpButtons
    ## Demos, Screens Menus in helpMenus 
    ## Frames and Flats Menu in frames and flats
    ## Matte Menu in bkgMatte    
    ## PathMaker Menu in pathWorks
    ## StoryHelp2 in helpDesk    
    ## Sprites, Background and Shadow Menus in helpMonkey
    ## Widgets for Pixitems, Backgrounds., in helpMaker    
### --------------------------------------------------------     
class PixHelp: 
### -------------------------------------------------------- 
    def __init__(self, parent, off=0, switch=''):
        super().__init__()  
   
        self.pixitem = parent  ## pixitem   
        self.canvas = self.pixitem.canvas
        
        self.switch = switch
                      
        self.table = TableWidgetSetUp(60, 180, len(pixKeys)+6)
        self.table.itemClicked.connect(self.clicked)    
    
        width, height = 247, 607
        self.table.setFixedSize(width, height)
                          
        self.table.setRow(0, 0, f'{"Sprite/PixItem Help Menu":<25}',QL,True, True, 2)
        
        row = 1
        for k, val in pixKeys.items():    
            if row == 10:
                self.table.setRow(row,      0, f'{"Additional KeyBoard Commands  "}',QC,True,True, 2) 
                self.table.setRow(row + 1,  0, f'{"if Sprites Are Selected "}',QC,True,True, 2) 
                row = 12          
            if row < 10:                 
                self.table.setRow(row, 0, k, '',True,True)
                self.table.setRow(row, 1, "  " + val,'','',True)    
            if row >= 12:
                self.table.setRow(row, 0, k, QL,True,True)
                self.table.setRow(row, 1, "  " + val, QL,'',True)
            row += 1
        
        self.table.setRow(row,      0, f'{"Hold Down Key - Click on Sprite ":<25}',QC,True, True,2) 
        self.table.setRow(row + 1,  0, f'{"Enter Key or Select From Above "}',QH,True,True, 2)     
        self.table.setRow(row + 2,  0,  f"{'Click Here to Close':<22}",'',True,True, 2)
    
        x, y = getVuCtr(self.pixitem.canvas)  ## need the 'y'        
                
        if self.switch != 'pix':
            if off != 0: x += off
            x = int(x - (width/2)) 
        else: 
            b = self.pixitem.boundingRect()
            width = int(b.width() + 20)
            x = int(off + width)
     
        y = int(y - (height/2))  ## default
     
        self.table.move(x, y)     
        self.table.show()  
      
    def clicked(self):
        if self.switch == '' or self.switch == 'pix':
            try:
                help = self.table.item(self.table.currentRow(), 0).text().strip()
                if help == '\\': 
                    help = 'tag'
                elif help == 'H':
                    self.closeMenu()        ## pixiitem has its own sharedkeys
                if help != 'H' and help in self.pixitem.sharedKeys:
                    QTimer.singleShot(25, partial(self.pixitem.shared, help))  
            except:
                None
        self.closeMenu()

    def closeMenu(self): 
        self.table.close()
        if self.switch != '' and self.switch != 'pix':
            self.canvas.setKeys('N')
  
### --------------------- dotsBkgHelp ----------------------       
class BkgHelp: 
### -------------------------------------------------------- 
    def __init__(self, parent, off=0, switch=''):
        super().__init__()  
        
        self.bkgItem = parent 
        self.canvas = self.bkgItem.canvas
        self.switch = switch 

        self.table = TableWidgetSetUp(65, 180, len(bkgHelpKeys)+4)
        self.table.itemClicked.connect(self.clicked)    
    
        width, height = 251, 517
        
        self.table.setFixedSize(width, height)  
        self.table.setRow(0, 0, f'{"Background Help Menu":<22}',QL,True,True,2)
    
        row = 1
        for k , val in bkgHelpKeys.items():
            self.table.setRow(row, 0, k,'',True,True)
            self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1

        self.table.setRow(row, 0, f"{'Arrow Keys Can Modify ScreenRates ':<15}",QC,True,True, 2)
        self.table.setRow(row + 1, 0, f'{" Hold Down Key - Click on Background ":<11}', QL,True, True, 2) 
        self.table.setRow(row + 2, 0, f"{'Click Here to Close':<22}",'',True,True, 2)

        x, y = getVuCtr(self.bkgItem.canvas)  
        if off != 0: x += off  
        
        self.table.move(int(x - (width /2)), int(y - (height /2))+10)    
        self.table.show()
  
    def clicked(self):
        if self.switch == '':
            try:
                help = self.table.item(self.table.currentRow(), 0).text().strip()
                if help == '\\': 
                    help = 'tag'    
                elif help == 'option':
                    help = 'opt'  
                if help != 'H' and help in self.bkgItem.sharedKeys:
                    QTimer.singleShot(25, partial(self.bkgItem.shared, help)) 
                elif help in ('Shift-B', 'Shift-U'):
                    self.canvas.view.sendIt(QKeySequence(help[-1]), Qt.KeyboardModifier.ShiftModifier)  
                elif help == 'Option-B':
                    self.canvas.view.sendIt(QKeySequence(help[-1]), Qt.KeyboardModifier.AltModifier)
            except:
                None
        self.closeMenu()
       
    def closeMenu(self):
        self.table.close()
        if self.switch != '':
            self.canvas.setKeys('N')
  
### ------------------- dotsShadowHelp ---------------------    
class ShadowHelp:  
### --------------------------------------------------------
    def __init__(self, parent, off=0, switch=''):
        super().__init__()  
        
        self.maker  = parent  
        self.canvas = self.maker.canvas
        self.switch = switch 
                            
        self.table = TableWidgetSetUp(50, 165, len(SharedKeys)+3)
        self.table.itemClicked.connect(self.clicked)   
 
        width, height = 221, 368
        self.table.setFixedSize(width, height)

        self.table.setRow(0, 0, f'{" Shadow Help Menu":<20}',QL,True,True, 2)

        row = 1
        for k , val in shadowKeys.items(): 
            if k == 'dblclk':
                self.table.setRow(row, 0, k, QC , True, True)
                self.table.setRow(row, 1, "  " + val, QC, '', True)      
            else:
                self.table.setRow(row, 0, k,'',True,True)
                self.table.setRow(row, 1, "  " + val,'','',True)
            row += 1
   
        self.table.setRow(row,     0, f'{"Hold Down - Click on Shadow ":<21}',QL,True, True,2)       
        self.table.setRow(row + 1, 0, f'{"Click Here to Close  ":<19}','',True, True, 2)
    
        x, y = getVuCtr(self.maker.canvas) 

        if self.switch != '':   ## help 
            if off != 0: x += off
            x = int(x - (width /2)) 
            y = int(y - (height /2)) 
        else:
            self.maker.shadow = parent.shadow
            x, _ = self.maker.getXY()  ## move it to the right one width +
            b = self.maker.shadow.boundingRect()
            width = int(b.width() + 20)
            x = int(x + width)       
            
            p = self.maker.shadow.pos(); y = int(p.y()) 
            p = self.canvas.mapToGlobal(QPoint(x ,y)) 
            y = int(p.y())
            
        self.table.move(x, y)          
        self.table.show() 
 
 
    def clicked(self):
        if self.switch == '':
            try:
                help = self.table.item(self.table.currentRow(), 0).text().strip()
                if help == '\\': 
                    help = 'tag'
                if help != 'H' and help in SharedKeys:
                    QTimer.singleShot(25, partial(self.maker.shadow.shared, help))
            except:
                None
        self.closeMenu()

    def closeMenu(self):   
        self.table.close()  
        if self.switch != '' and self.switch != 'pix':
            self.canvas.setKeys('N')  ## open help menus
         
### -------------------- dotsHelpMonkey -------------------- 

                


