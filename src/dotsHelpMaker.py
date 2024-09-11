
from dotsShared         import paths  ## for background flat
from dotsSideGig        import *
from dotsTableModel     import TableWidgetSetUp, QL, QC, QH

from dotsBkgWidget      import BkgWidget
from dotsPathWidget     import PathWidget
from dotsPixWidget      import PixWidget
from dotsShadowWidget   import ShadowWidget

from dotsBkgMatte       import MatteHelp
from dotsFrameAndFlats  import FlatHelp

from dotsHelpButtons    import CanvasHelp, StoryHelp
from dotsHelpMenus      import DemoHelp, ScreenHelp
from dotsHelpMonkey     import BkgHelp, PixHelp, ShadowHelp

from dotsPathWorks      import PathHelp
from dotsPixWorks       import AnimationHelp

switchKeys = {  
    'buttons':  'Canvas, StoryBoard and PathMaker',     ## helpButtons and pathWorks
    'widgets':  'Widgets for Pixitems, Backgrounds...', ## helpMaker
    'demos':    'Demos, Screens and Animation Help',    ## helpMenus and pixWorks    
    'sprites':  'Sprites, Backgrounds and Shadows',     ## helpMonkey
    'flats':     'Frame, Flats and Matte Help',          ## in flat and frames and bkgMatte
}

SpinDrift = QColor('#73fcd6')

### -------------------- dotsHelpMaker --------------------- 
''' Home for the help menus - uses switch, either '' or 'on' '''
### --------------------------------------------------------     
class HelpMaker:  ## the help menus
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
   
    def menuHelp(self):
        self.canvas.clear()
        self.canvas.bkgMaker.setBkgColor(SpinDrift)
        self.switchHelp =  MainMenu(self.canvas)

### --------------------------------------------------------     
class  MainMenu: 
### --------------------------------------------------------
    def __init__(self, canvas):
        super().__init__()  
   
        self.canvas = canvas  
        self.scene = self.canvas.scene
             
        self.bkg = None

        self.table = TableWidgetSetUp(0, 260, len(switchKeys)+3)
        self.table.itemClicked.connect(self.clicked)                                      
        self.table.setRow(0, 0, f'{"Help Menus":<15}','',True,True,2) 
        
        row = 1;  self.fix = []
        for k, val in switchKeys.items():
            self.fix.append(k)
            self.table.setRow(row, 0, val,'', True, True, 2)
            row += 1
   
        self.table.setRow(row, 0,f'{"Select From Above":<20}',QL,True,True, 2)
        self.table.setRow(row + 1, 0,f'{"Click Here to Close":<20}','',True,True, 2)
     
        self.table.setFixedSize(266, 247)    
        x, y = getVuCtr(self.canvas)  
         
        if self.canvas.dots.Vertical:
            y = y - 60          
      
        self.table.move(x-137, y-100)                
        self.table.show() 
           
    def clicked(self):  
        p = self.table.currentRow() - 1 
        if p+1 <= len(switchKeys): 
            help = self.fix[p].strip()    
            if help == 'buttons':
                self.buttonHelp('on')
            elif help == 'sprites':
                self.screenitems('on') 
            elif help == 'demos':  
                self.makeDemoMenu()
            elif help == 'flats':  
                self.makeFlatMenu()
            elif help == 'widgets':  
                self.widgetsHelp()     
        else:
            self.table.close() 
            self.canvas.clear()   
                 
    def buttonHelp(self, str=''):
        self.canvas.clear()
        self.canvas.bkgMaker.setBkgColor(SpinDrift)
    
        self.canvasHelp = CanvasHelp(self, self.canvas, -350, str)
        self.storyHelp  = StoryHelp(self, self.canvas, 0, str)
        self.pathHelp   = PathHelp(self, self.canvas, 350, str)
 
    def widgetsHelp(self):
        self.canvas.clear()
        self.canvas.bkgMaker.setBkgColor(SpinDrift)
 
        bkg    = BkgWidget(self.canvas, None, 'on')
        pix    = PixWidget(self.canvas, 'on')
        path   = PathWidget(self.canvas, None, 'on')
        shadow = ShadowWidget(self.canvas, None, 'on')
               
    def makeDemoMenu(self):
        self.canvas.clear()
        self.canvas.bkgMaker.setBkgColor(SpinDrift)
      
        self.demoHelp   = DemoHelp(self.canvas, -325, 'on')
        self.screenHelp = ScreenHelp(self.canvas, 0, 'on')
        self.animeHelp  = AnimationHelp(self.canvas, QPoint(), 'on', 225)
             
    def screenitems(self, str=''): 
        self.canvas.clear()
        self.canvas.bkgMaker.setBkgColor(SpinDrift)
   
        self.bkgHelp    = BkgHelp(self.canvas,0, str)
        self.shadowHelp = ShadowHelp(self.canvas, 350, str)
        self.pixHelp    = PixHelp(self.canvas, -350, str)                
 
    def makeFlatMenu(self):
        self.canvas.clear()
        self.canvas.bkgMaker.setBkgColor(SpinDrift)
        
        self.flatHelp    = FlatHelp(self, self.canvas, -350, 'flat', 'on')
        self.matteHelp  = MatteHelp(self.canvas, None, 0, 'on')
        self.frameHelp  = FlatHelp(self, self.canvas, 350, 'frame', 'on')
    
### -------------------- dotsHelpMaker --------------------- 



