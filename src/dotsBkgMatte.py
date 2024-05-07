
from PyQt6.QtCore       import Qt, QPoint, QPointF, QTimer
from PyQt6.QtGui        import QColor, QPainter, QPainterPath, QBrush, QImage
from PyQt6.QtWidgets    import QWidget, QMenu
   
from dotsShared         import common, paths
from dotsSideGig        import getVuCtr

## these keys + shift - replace the run, (pause, resume), and stop buttons if covered by the matte 
ShiftKeys = (Qt.Key.Key_R, Qt.Key.Key_P, Qt.Key.Key_S) 

helpKeys = {
    '>':    'Expand Matte Size',
    '<':    'Reduce Matte Size',
    'B':    'Black Matte Color',  
    'C':    'Change Matte Color', 
    'E':    'E/Enter to Close Menu',
    'G':    'Grey Matte Color',
    'H':    'Matte Help Menu',
    'P':    'Photo Background', 
    'Q':    'Close Matte', 
    'R':    'Resize Matte by Height',
    'W':    'White',
    'X':    'Close Matte', 
}
  
### --------------------- dotsBkgMatte ---------------------           
class Matte(QWidget):
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.canvas   = parent 
        self.view     = self.canvas.view  
        self.bkgMaker = self.canvas.bkgMaker
            
        self.type = 'widget'       
        self.save = QPointF()
     
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.FramelessWindowHint|\
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.NoDropShadowWindowHint|\
            Qt.WindowType.WindowStaysOnTopHint) 

        self.setAccessibleName('widget')
        self.setStyleSheet('background-color: rgba(0,0,0,0)')
        
        p = self.canvas.mapToGlobal(QPoint())
        
        self.x = p.x()
        self.y = p.y()
    
        self.black = QBrush(QColor('black'))
        self.grey  = QBrush(QColor(150,150,150))
        self.white = QBrush(QColor(250,250,250))
        self.pix   = None
        
        self.img = QImage(paths['bkgPath'] + 'bluestone.jpg')  ## photo matte
    
        self.border = 100  ## inital
        self.step   = 27
        self.stop   = 50  ## min y.() - Max Headroom
        self.brush  = self.white  ## default   
          
        self.ratio = 1.0    
        self.altRatio = .77 ##.55 = 16:9 # .77  
        self.resize(common['ViewW']+100, common['ViewH']+100) 
        
        self.move(self.x, self.y) 
        
        self.helpMenu = None
        self.helpMenu = HelpMenu(self)
        
        self.help = False
        QTimer.singleShot(200, self.helpMenu.openHelpMenu)
         
        self.show()
                
        self.grabKeyboard()  ## note !!!
         
### --------------------------------------------------------
    def paintEvent(self, e):            
        qp = QPainter()
        qp.begin(self)
 
        path = QPainterPath() 
    
        viewW = int(common['ViewW']+(self.border*2))
        viewH = int(common['ViewH']+(self.border*2)*self.ratio)
    
        self.resize(viewW, viewH) 
    
        path.addRect(0, 0, viewW, viewH)  ## outer
        path.addRect(self.border+2, int(self.border*self.ratio)+2, common['ViewW']-4, int(common['ViewH'])-2)  ## inner
  
        if self.pix != None:   
            self.pix= self.img.scaled(viewW, viewH,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation)      
            self.brush = QBrush(self.pix)
      
        qp.setBrush(self.brush)  
        qp.drawPath(path)
        
        self.move(self.x-self.border, int(self.y-(self.border)*self.ratio))
                
        qp.end()
        
### --------------------------------------------------------
    def keyPressEvent(self, e):
        key = e.key()   
        mod = e.modifiers()
   
        if key in ShiftKeys and mod & Qt.KeyboardModifier.ShiftModifier:  
            if key == Qt.Key.Key_R: 
                self.canvas.showtime.run()
            elif key == Qt.Key.Key_P: 
                self.canvas.showtime.pause()
            else:
                self.canvas.showtime.stop()
                
        elif key == Qt.Key.Key_Space:          
            self.canvas.showtime.pause() 
                
        elif key == Qt.Key.Key_Greater:  ## scale up  
            self.scaleThis(key)       
            if self.y-(self.border*self.ratio) <= self.stop:
                self.border -= self.step ## back it off - top of screen display
                
        elif key == Qt.Key.Key_Less:  ## scale down
            self.scaleThis(key)   
                   
        elif key in (Qt.Key.Key_Q, Qt.Key.Key_X):
            if self.help == True:      
                self.helpMenu.closeHelpMenu() 
                
            self.bkgMaker.matte = None      
            self.view.grabKeyboard()       
            self.close()   
                 
        elif key == Qt.Key.Key_H: 
            self.helpMenu.openHelpMenu() if self.help == False else \
                self.helpMenu.closeHelpMenu()
                 
        elif key in (Qt.Key.Key_E, Qt.Key.Key_Enter, Qt.Key.Key_Return):
            if self.help == True:      
                self.helpMenu.closeHelpMenu() 
        
        elif key == Qt.Key.Key_C:  ## change color
            if self.pix != None:
                self.pix = None
                self.brush = self.white
            elif self.brush == self.white:
                self.brush = self.grey
            elif self.brush == self.grey:
                self.brush = self.black
            elif self.brush == self.black:
                self.brush = self.white  
                
        elif key == Qt.Key.Key_B:  ## change color  
            self.brush = self.black  
        
        elif key == Qt.Key.Key_G:  ## change color  
            self.brush = self.grey        
                                
        elif key == Qt.Key.Key_P:  ## use pix 
            if self.pix == None:    
                self.pix = self.img  ## something to initialize it  
            else:
                self.pix = None
                self.brush = self.grey      
                
        elif key == Qt.Key.Key_W:  ## change color  
            self.brush = self.white  
             
        ## set screen format ratio to around .61 - midway between 16:9 and 3:2         
        elif key == Qt.Key.Key_R: 
            self.ratio = self.altRatio if self.ratio == 1.0 else 1.0    
                
        self.update()
        e.accept()
        
### --------------------------------------------------------   
    def scaleThis(self, key):
        if key == Qt.Key.Key_Greater:
            wuf = self.border
            if self.border == 5:
                self.border = 12     
            elif self.border == 12: 
                self.border = self.step  
            elif self.border >= self.step:
                self.border += self.step + 2
            if self.border == wuf: self.border = 12  ## stuck, next size up      
        else:    
            if self.border == self.step: 
                self.border = 12  
            elif self.border == 12:
                self.border = 5
            elif self.border > self.step:
                self.border -= self.step - 2
                    
    def mousePressEvent(self, e):
        self.save = e.globalPosition()
        e.accept()

    def mouseMoveEvent(self, e):
        self.moveThis(e)
        e.accept()
        
    def mouseReleaseEvent(self, e):
        self.moveThis(e)
        e.accept()
                      
    def moveThis(self, e):
        dif = e.globalPosition() - self.save      
        self.move(self.pos() + QPoint(int(dif.x()), int(dif.y())))
        self.save = e.globalPosition()
      
### --------------------------------------------------------     
class HelpMenu:  ## for canvas - one key commands
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()  
   
        self.matte = parent 
        self.canvas = self.matte.canvas

        self.helpMenu = self.matte.helpMenu
        
### --------------------------------------------------------                     
    def openHelpMenu(self):
        self.closeHelpMenu()    
        self.helpMenu = QMenu(self.canvas)    
        self.helpMenu.addAction(' Matte KeyBoard Help '.rjust(27,' '))
        self.helpMenu.addSeparator()
        
        for help, demo in helpKeys.items():   
            action = self.helpMenu.addAction(f'{help:<3}- {demo:<30}')
            self.helpMenu.addSeparator()
            action.triggered.connect(lambda chk, help=help: self.clicked(help))
             
        self.helpMenu.addSeparator()
        self.helpMenu.addAction('Shift-R - Run Animation')
        self.helpMenu.addSeparator()
        self.helpMenu.addAction('Shift-P - Pause/Resume Animation')
        self.helpMenu.addSeparator()
        self.helpMenu.addAction('Shift-S - Stop Animation')
        self.helpMenu.addSeparator()
        self.helpMenu.addAction("Use 'H' to Close Menu  ".rjust(32,' '))
         
        x, y = getVuCtr(self)
        
        self.helpMenu.setFixedSize(250, 528)       
        self.helpMenu.move(x-125, y-250)  
        self.helpMenu.show()
        
        self.matte.help = True
    
    def clicked(self, help):  
        self.closeHelpMenu()
            
    def closeHelpMenu(self):   
        if self.helpMenu:
            self.helpMenu.close()
        self.helpMenu = None
        self.matte.help = False
   
### -------------------- dotsBkgMatte ----------------------        

        
