
from PyQt6.QtCore       import Qt
from PyQt6.QtGui        import QKeySequence

from dotsSideGig        import getVuCtr
from dotsTableModel     import TableWidgetSetUp, QC, QL, QH

storyKeys = {   ## storyHelp2
    'F':    'Flop Selected',
    'P':    'Toggle Paths - Animation',
    'T':    'ToggleTags - Animation',
    'Shift-H': 'Hide Selected Outlines',    
    'Shift-L': 'Toggle Sprite Locks',
    'Shift-R': 'Unlink, Unlock, UnSelect',
    'Shift-S': 'Toggle Shadow Links',  
    'Shift-T': 'Toggle Sprite Shadow Tags',
    'Shift-U': 'UnLock All Screen Items',  
    'Cmd':  'Drag to Select',
    'M':    'Move Selected off/on',
    'U':    'UnSelect - End',     
}

pathKeys = {     ## pathHelp2
    '>':    'Shift WayPts +5%',
    '<':    'Shift WayPts -5%',
    '!':    'Half Path Size',
    '@':    'Redistribute Pts',      
    '/':    'Path Color',    
    '}':    'Flop Path',
    '{':    'Flip Path',      
    ':/"': 'Scale X - Colon/Dbl-Quote',
    ";/'": 'Scale Y - Semi-Colon/Sgl-Quote',
    '_/+':  'Rotate 1 deg',  
    '-/=':  'Rotate 15 deg',
    '[/]':  'Rotate 45 deg',
    '</>':  'Toggle Size',  
}

PathStr = ('>', '<', '!', '@','/','{','}')  ## wired up

### --------------------- dotsHelpDesk --------------------- 
''' classes: StoryHelp2, PathHelp2,  '''
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
class StoryHelp2: 
### -------------------------------------------------------- 
    def __init__(self, parent, off=0, switch=''):
        super().__init__()  
     
        self.canvas = parent
        self.switch = switch

        self.table = TableWidgetSetUp(65, 185, len(storyKeys)+4)
        self.table.itemClicked.connect(self.clicked)    
    
        width, height = 257, 486
        self.table.setFixedSize(width, height)
     
        self.table.setRow(0, 0, f'{"   StoryBoard Help Menu 2":<30}',QL,True,True,2)
    
        row = 1  
        for k, val in storyKeys.items():
            if row < 10:
                self.table.setRow(row, 0, k, '', True,True)
                self.table.setRow(row, 1, "  " + val, '', '',True)      
                row += 1
            else:
                if row == 10:
                    self.table.setRow(row, 0, f"{' Keys for Rubberband Select':<32}",QC,True,True,2)
                    row = 11
                self.table.setRow(row, 0, k, QL, True,True)  ## highlight
                self.table.setRow(row, 1, "  " + val, QL, False, True)                 
                row += 1
 
        self.table.setRow(row,     0, f'{"Enter Key or Select From Above "}',QH,True,True, 2) 
        self.table.setRow(row + 1, 0, f"{'Click Here to Close':<22}",'',True,True, 2)
  
        x, y = getVuCtr(self.canvas)  
        if off != 0: x += off  
        
        self.table.move(int(x -(width /2)), int(y - (height /2)))
        self.table.show()
              
    def clicked(self):
        if self.switch == '':
            help = self.table.item(self.table.currentRow(), 0).text().strip()
            if help == 'F':
                self.canvas.view.sendIt(QKeySequence(help), None)
            elif  help == 'P':
                self.canvas.setKeys('P')
            else:  ## send last char and modifier
                self.canvas.view.sendIt(QKeySequence(help[-1]), Qt.KeyboardModifier.ShiftModifier)
        self.closeMenu()
       
    def closeMenu(self):  
        self.table.close()
        if self.switch != '':
            self.canvas.setKeys('N')
     
  ### --------------------------------------------------------     
class PathHelp2: 
### -------------------------------------------------------- 
    def __init__(self, parent, off=0, switch=''):
        super().__init__()  
 
        self.canvas = parent
        self.switch = switch
   
        self.maker = self.canvas.pathMaker

        self.table = TableWidgetSetUp(50, 200, len(pathKeys)+5, 0, 28)
        self.table.itemClicked.connect(self.clicked)    
    
        width, height = 256, 512
        self.table.setFixedSize(width, height)
     
        self.table.setRow(0, 0, f'{" PathMaker Help Menu 2":<27}',QL,True,True,2)
        
        row = 1
        for k , val in pathKeys.items():
            if row < 8:
                self.table.setRow(row, 0, k, '',True,True, 7)  ## highlight
                self.table.setRow(row, 1, "  " + val,'','',True)
                row += 1
            else:
                if row == 8:
                    self.table.setRow(row, 0, f'{"These Commands Require A Keyboard  ":<15}',QC,True,True, 2) 
                    row = 9
                self.table.setRow(row, 0, k, QL,True,True, 7)  ## highlight
                self.table.setRow(row, 1, "  " + val, QL,'','')                
                row += 1

        self.table.setRow(row,      0, f"{'Use Arrow Keys to Move Path':<15}",QC,True,True, 2)
        self.table.setRow(row + 1,  0, f'{"  Enter Key or Select From Above "}',QH,True,True, 2)
        self.table.setRow(row + 2,  0, f"{'Click Here to Close':<22}",'',True,True, 2)
  
        x, y = getVuCtr(self.canvas)  
        if off != 0: x = x + off  

        self.table.move(int(x - (width /2)), int(y - (height /2)))
        self.table.show()
   
    def clicked(self): 
        if self.switch == '':
            key = self.table.item(self.table.currentRow(), 0).text().strip()      
            if key in PathStr:
                self.canvas.setKeys(key)
        self.closeMenu()
       
    def closeMenu(self):  
        self.table.close()
        if self.switch != '':
            self.canvas.setKeys('N')
                      
### --------------------- dotsHelpDesk --------------------- 



