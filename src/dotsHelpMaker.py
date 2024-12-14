

from dotsSideGig        import *
from dotsTableModel     import TableWidgetSetUp, QL, QC, QH

from dotsBkgWidget      import BkgWidget
from dotsPathWidget     import PathWidget
from dotsPixWidget      import PixWidget
from dotsShadowWidget   import ShadowWidget

from dotsHelpButtons    import CanvasHelp, StoryHelp
from dotsHelpMenus      import DemoHelp, ScreenHelp
from dotsHelpMonkey     import BkgHelp, PixHelp, ShadowHelp
from dotsHelpDesk       import StoryHelp2, PathHelp2

from dotsBkgMatte       import MatteHelp
from dotsFrameAndFlats  import FlatHelp
from dotsPathWorks      import PathHelp
from dotsPixWorks       import AnimationHelp

switchKeys = {  
    'buttons':  'Canvas, StoryBoard and PathMaker',     ## helpButtons and pathWorks
    'widgets':  'Widgets for Pixitems, Backgrounds...', ## helpMaker
    'demos':    'Demos, Screens and Animation Help',    ## helpMenus and pixWorks    
    'sprites':  'Sprites, Backgrounds and Shadows',     ## helpMonkey
    'flats':     'Frame, Flats and Matte Help',          ## in flat and frames and bkgMatte   
    'story':    'Sprite and StoryBoard Menus',  
    'path':     'PathMaker Widget and Menus',
}

SpinDrift = QColor('#73fcd6')

### -------------------- dotsHelpMaker --------------------- 
''' Home for the help menus - uses switch, either '' or 'on' '''
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
class HelpMaker:  ## the help menus
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
   
    def menuHelp(self):
        self.canvas.sideCar.clearWidgets()
        self.canvas.bkgMaker.setBkgColor(SpinDrift)
        self.switchHelp =  MainMenu(self.canvas)
        
        self.canvas.openPlayFile = 'menu'  ## blocks helpbutton and 'H' and 'M' keys
        self.canvas.btnHelp.setEnabled(False)  

### --------------------------------------------------------     
class  MainMenu: 
### --------------------------------------------------------
    def __init__(self, canvas):
        super().__init__()  
   
        self.canvas = canvas  
        self.scene = self.canvas.scene
        self.sideCar = self.canvas.sideCar
             
        self.table = TableWidgetSetUp(0, 260, len(switchKeys)+3)
        self.table.itemClicked.connect(self.clicked)                                      
        self.table.setRow(0, 0, f'{"Help Menus":<15}','',True,True,2) 
        
        row = 1; self.lst = []
        for k, val in switchKeys.items():
            self.lst.append(k)
            self.table.setRow(row, 0, val,'', True, True, 2)
            row += 1
   
        self.table.setRow(row, 0,f'{"Select From Above":<20}',QL,True,True, 2)
        self.table.setRow(row + 1, 0,f'{"Click Here to Close":<20}','',True,True, 2)
     
        self.table.setFixedSize(266, 305)    
        x, y = getVuCtr(self.canvas)  
         
        if self.canvas.dots.Vertical:
            y = y - 60          
      
        self.table.move(x-135, y-210)                
        self.table.show() 
           
    def clicked(self):  
        p = self.table.currentRow() - 1  ## position in lst to key   
        if p+1 <= len(switchKeys):       ## is it valid           
            help = self.lst[p].strip()    
            
            self.sideCar.clearWidgets()
            self.canvas.bkgMaker.setBkgColor(SpinDrift)  
            
            if help == 'buttons':
                self.canvasHelp = CanvasHelp(self, self.canvas, -350, 'on')
                self.storyHelp  = StoryHelp(self, self.canvas, 0, 'on')
                self.pathHelp   = PathHelp(self, self.canvas, 350, 'on')
                
            elif help == 'sprites': 
                self.bkgHelp    = BkgHelp(self.canvas,0, 'on')
                self.shadowHelp = ShadowHelp(self.canvas, 350, 'on')
                self.pixHelp    = PixHelp(self.canvas, -350, 'on')  
                
            elif help == 'demos':  
                self.demoHelp   = DemoHelp(self.canvas, -325, 'on')
                self.screenHelp = ScreenHelp(self.canvas, 0, 'on')
                self.animeHelp  = AnimationHelp(self.canvas, QPoint(), 'on', 225)
                
            elif help == 'flats':  
                self.flatHelp   = FlatHelp(self, self.canvas, -350, 'flat', 'on')
                self.matteHelp = MatteHelp(self.canvas, None, 0, 'on')
                self.frameHelp = FlatHelp(self, self.canvas, 350, 'frame', 'on')
                
            elif help == 'widgets': 
                bkg    = BkgWidget(self.canvas, None, 'on')
                pix    = PixWidget(self.canvas, 'on')
                path   = PathWidget(self.canvas, None, 'on')
                shadow = ShadowWidget(self.canvas, None, 'on')
                             
            elif help == 'bkg':   
                bkg = BkgWidget(self.canvas, 0, 'all')
                self.bkgHelp = BkgHelp(self.canvas, 250, 'all')
                
            elif help == 'shadow':   
                shadow = ShadowWidget(self.canvas, 0, 'all')
                self.shadowHelp = ShadowHelp(self.canvas, 200, 'all')
                    
            elif help == 'pix':  
                self.pixWidget = PixWidget(self.canvas, 'all')
                self.pixHelp   = PixHelp(self.canvas, 215, 'all') 
  
            elif help == 'story':  
                self.pixHelp    = PixHelp(self.canvas, -355, 'all') 
                self.storyHelp  = StoryHelp(self, self.canvas, 0, 'on') 
                self.storyHelp2 = StoryHelp2(self.canvas, 355, 'on')
                  
            elif help == 'path':
                self.pathWidget = PathWidget(self.canvas, '', 'all')
                self.pathHelp   = PathHelp(self, self.canvas, 25, 'all')   
                self.pathHelp2  = PathHelp2(self.canvas, 365, 'all')          
        else:
            self.table.close() 
            self.canvas.clear()   
                 
### -------------------- dotsHelpMaker --------------------- 



