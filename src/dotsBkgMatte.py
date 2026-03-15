
import random

from functools          import partial

from PyQt6.QtCore       import Qt, QPoint, QTimer
from PyQt6.QtGui        import QColor, QPainter, QPainterPath, QBrush, QImage
from PyQt6.QtWidgets    import QWidget
   
from dotsShared         import common, paths
from dotsSideGig        import getVuCtr, MsgBox
from dotsTableModel     import TableWidgetSetUp, QC, QL, QH

matteKeys = {
    'B':    'Black Matte Color',  
    'C':    'Change Matte Color', 
    'delete':  'Delete Background',
    'G':    'Grey Matte Color',
    'H':    'Matte Help Menu',
    'P':    'Photo Background', 
    'Q':    'Close Matte', 
    'V':    'Vary Matte Height',
    'W':    'White',
    'X':    'Close Matte',  
    '+, >, ]':  'Scales Matte Up',
    '_, <, [':  'Scales Matte Down',
    'R':    'Run Animation',
    'SpaceBar': 'Pause/Resume',  
    'S':        'Stop Animation',
}

SharedKeys = ('B','C', 'del', 'G', 'H', 'P', 'Q', 'R', 'S', 'V', 'W', 'X', 'Space', '<', '>')

### --------------------- dotsBkgMatte ---------------------     
''' 
    '+, >, ]' scales the Matte up in both directions and '_, <, ['
    scales it down - square brackets require one finger.
    
    It seems Qt5 is alittle different as to how it works
    compared to Qt6 and required some additional changes - 
    that's why the '## 5' and '##-5' tokens.
'''
### --------------------------------------------------------      
class SkyNet(QWidget):  
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.type = 'widget' 
        self.setAccessibleName('widget')
   
        self.setWindowFlags(Qt.WindowType.Window|\
            Qt.WindowType.FramelessWindowHint|\
            Qt.WindowType.CustomizeWindowHint|\
            Qt.WindowType.NoDropShadowWindowHint)
    
        self.setStyleSheet('background-color: rgba(0,0,0,0)')
        self.resize(common['DotsW']+100, common['DotsH']+100) 
    
        p = parent.canvas.dots.pos() 
        self.move(p.x()-50, p.y()-25)
         
        self.show()
    
    def mousePressEvent(self, e):  ## doesn't work in qt5
        if e.button() == Qt.MouseButton.RightButton:
            self.parent.shared('H')
        e.accept() 
        
    def mouseReleaseEvent(self, e): 
        self.parent.setFocus() 
        e.accept()      

    def mouseDoubleClickEvent(self, e): 
        self.parent.shared('H')
        e.accept() 
        
### --------------------------------------------------------      
class Matte(QWidget):  ## opens itself
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.bkgItem  = parent
        self.bkgWorks = self.bkgItem.bkgWorks
        self.canvas   = self.bkgItem.canvas
        
        self.type = 'widget' 
        self.setAccessibleName('widget')
        
        self.setWindowFlags(Qt.WindowType.Window|\
            Qt.WindowType.FramelessWindowHint|\
            Qt.WindowType.CustomizeWindowHint|\
            Qt.WindowType.NoDropShadowWindowHint)## 5
            ##Qt.WindowType.WindowStaysOnTopHint)## 5
  
        self.setStyleSheet('background-color: rgba(0,0,0,0)')
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        
        self.skynet = SkyNet(self)

        p = self.canvas.mapToGlobal(QPoint())
        self.x = p.x()
        self.y = p.y()
    
        self.black = QBrush(QColor('black'))
        self.grey  = QBrush(QColor(150,150,150))
        self.white = QBrush(QColor(250,250,250))
        
        self.lst = [self.white, self.grey, self.black]
        
        self.pix = None
        self.img = QImage(paths['bkgPath'] + 'bluestone.jpg')  ## photo used by matte
    
        self.border = 30  ## inital
        self.step   = 27
        self.stop   = 50  ## min y.() - Max Headroom
        self.brush  = self.white  ## default   
          
        self.ratio = 1.0     ## see below
        self.altRatio = .77  ## less than (.55 of 16:9) 
        self.resize(common['ViewW']+100, common['ViewH']+100) 
        
        self.move(self.x, self.y)  ## 0,0 for canvas relative to actual screen format
        self.show()
      
        self.helpMenu = True      
        self.matteHelpMenu = MatteHelp(self.canvas, self) 
 
        self.grabKeyboard() 
         
        self.show()
                          
### --------------------------------------------------------
    def paintEvent(self, e):            
        qp = QPainter()
        qp.begin(self)
 
        path = QPainterPath() 

        viewW = int(common['ViewW']+(self.border*2))  ## inner
        viewH = int(common['ViewH']+(self.border*2)*self.ratio)
    
        self.resize(viewW, viewH) 
    
        path.addRect(0, 0, viewW, viewH)  ## outer
        path.addRect(self.border+2, int(self.border*self.ratio)+2, \
            common['ViewW']-4, int(common['ViewH'])-2)  ## inner
  
        if self.pix != None:  
            try: 
                self.pix = self.img.scaled(viewW, viewH,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)    
            except Exception.TypeError:
                MsgBox('Paint Error', 5) 
                return         
            self.brush = QBrush(self.pix)
      
        qp.setBrush(self.brush)  
        qp.drawPath(path)
 
        self.move(self.x-self.border, int(self.y-(self.border)*self.ratio))  
        qp.end()

### --------------------------------------------------------                  
    def mousePressEvent(self, e):  
        if e.button() == Qt.MouseButton.RightButton:
            self.shared('H')  
        e.accept()
                   
    def mouseReleaseEvent(self, e): 
        self.setFocus() 
        e.accept()             
                   
    def mouseDoubleClickEvent(self, e): 
        self.shared('H')  
        e.accept()
        
### --------------------------------------------------------
    def keyPressEvent(self, e):
        key = e.key() 
        mod = e.modifiers()   

        if key in ('E',  Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.matteHelpMenu.closeMenu()        
                        
        elif key == Qt.Key.Key_BracketRight or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Greater, Qt.Key.Key_Plus):
                self.shared('>')        
                
        elif key == Qt.Key.Key_BracketLeft or mod & Qt.KeyboardModifier.ShiftModifier \
            and key in (Qt.Key.Key_Less, Qt.Key.Key_Underscore):
                self.shared('<')         
                
        elif key == Qt.Key.Key_Space:
            self.shared('Space')    
            
        elif key == 16777219:  ## reading direct
            self.shared('del')  
    
        else: 
            try:
                key = chr(key) 
            except: 
                return   
            self.shared(key)   
         
    def shared(self, key):  
        if key != 'P' and self.pix != None:
            if key in SharedKeys:
                self.pix = None           
        match key: 
            case 'B':     
                self.brush = self.black        
            case 'C':      ## change color
                self.brush = self.lst[random.randint(0,2)]       
            case 'del':      ## delete background    
                QTimer.singleShot(50, self.bkgItem.closeMatteWidget)   
                self.bkgItem.bkgMaker.deleteBkg(self.bkgItem)                  
            case 'G':     
                self.brush = self.grey       
            case 'H': 
                if not self.helpMenu:  
                    self.matteHelpMenu = MatteHelp(self.canvas, self) 
                    self.helpMenu = True 
                elif self.helpMenu:   
                    self.matteHelpMenu.closeMenu() 
                    self.matteHelpMenu = None
                    self.helpMenu = False                        
            case 'P':
                if self.pix == None:    
                    self.pix = self.img  ## something to initialize it       
                elif self.pix != None: 
                    self.pix = None
                    self.brush = self.lst[random.randint(0,2)]                     
            case 'R': 
                 self.canvas.showbiz.showtime.run()       
            case 'Space':          
                self.canvas.showbiz.showtime.pause()     
            case 'S':  
                self.canvas.showbiz.showtime.stop()                          
            case 'V':      ## set screen format ratio to around .61 - midway between 16:9 and 3:2 
                self.ratio = self.altRatio if self.ratio == 1.0 else 1.0                
            case 'W':      
                self.brush = self.white     
            case '>':     
                self.scaleUp()                     
            case '<':             
                self.scaleDown()          
            case 'Q'|'X':
                self.bye()                                                                              
        self.update()
            
### --------------------------------------------------------
    def scaleUp(self):      
        border30 = self.border    ## self.border = 30  
        if self.border == 5:
            self.border = 12     
            
        elif self.border == 12: 
            self.border = self.step    ## self.step = 27
            
        elif self.border >= self.step:
            self.border += (self.step + 2)   
                            
        if self.y-(self.border*self.ratio) < self.stop-10:  ## self.stop = 50 = (min y.() - Max Headroom) 
            self.border = border30  ## back it off - top of screen display
            MsgBox('  Max Headroom  ', 5)  ## can vary 
                   
    def scaleDown(self):     
        border = (self.border - self.step) - 2          
        if self.border == self.step or border < self.step and \
            border > 5 or border == 1:  ## 30-2-27
                border = 12    
                 
        elif border <= 5:
            border = 5
        self.border = border
                    
    def bye(self):        
        if self.helpMenu: 
            self.matteHelpMenu.closeMenu()
        self.releaseKeyboard()
        QTimer.singleShot(50, self.bkgItem.closeMatteWidget)   
  
### --------------------------------------------------------     
class MatteHelp(QWidget):
### -------------------------------------------------------- 
    def __init__(self, parent, matte=None, off=0, switch=''): 
        super().__init__()  
        
        ''' these are necessary for qt5 - otherwise you can delete them '''       
        # self.setWindowFlags(Qt.WindowType.Window|\##-5
        #     Qt.WindowType.FramelessWindowHint|\##-5
        #     Qt.WindowType.CustomizeWindowHint|\##-5 
        #     Qt.WindowType.NoDropShadowWindowHint|\##-5 
        #     Qt.WindowType.WindowStaysOnTopHint)##-5
        
        self.canvas = parent
        self.matte  = matte 
        self.switch = switch
    
        if self.switch == '':
            self.matte.helpMenu = True  

        self.table = TableWidgetSetUp(75, 170, len(matteKeys)+4)
        self.table.itemClicked.connect(self.clicked) 
         
        width, height = 252, 576
        self.table.setFixedSize(width, height)

        self.table.setRow(0, 0, f"{' Matte KeyBoard Help ':<23}",QL,True,True,2)

        row = 1
        for k, val in matteKeys.items():
            if row < 13:
                self.table.setRow(row, 0, k, '', True,True)
                self.table.setRow(row, 1, "  " + val, '', '',True)      
                row += 1
            else:
                if row == 13:
                    self.table.setRow(row, 0, f"{' Keys for Running an Animation':<32}",QC,True,True,2)
                    row = 14
                self.table.setRow(row, 0, k, QL, True,True)  ## highlight
                self.table.setRow(row, 1, "  " + val, QL, False, True)                 
                row += 1
    
        self.table.setRow(row,     0, f'{"Enter A Key From Above "}',QH,True,True, 2) 
        self.table.setRow(row + 1, 0, f'{"Click Here to Close Menu  ":<26}' ,'',True,True, 2)
   
        x, y = getVuCtr(self.canvas)    
        
        self.table.move(int(x - (width/2)), int(y - (height/2)))
        self.table.show()
            
    def clicked(self):
        if self.switch == '':
            try:
                help = self.table.item(self.table.currentRow(), 0).text().strip() 
                match help: 
                    case 'SpaceBar':
                        help = 'Space'  
                    case '+, >, ]': 
                        help = '>'
                    case  '_, <, [':
                        help = '<'  
                    case 'delete':
                        help = 'del'
                if help != 'H' and help in SharedKeys:
                    QTimer.singleShot(50, partial(self.matte.shared, help))      
            except:
                None
        self.closeMenu() 
          
    def closeMenu(self): 
        if self.switch == '': 
            self.matte.helpMenu = False
        self.table.close()
        if self.switch != '':
            self.canvas.setKeys('N')
  
### -------------------- dotsBkgMatte ----------------------        

        

