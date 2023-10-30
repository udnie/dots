
import os.path
import math
import random

from PyQt6.QtCore       import Qt, QPoint
from PyQt6.QtGui        import QPixmap
from PyQt6.QtWidgets    import QGraphicsPixmapItem
                        
from dotsShared         import common
from dotsSideGig        import MsgBox
from dotsBkgMatte       import Matte

### --------------------- dotsBkgWorks --------------------- 
''' classes: Tracker, BkgWorks, Flat -- mostly scrolling except for Flat'''    
### --------------------------------------------------------
class Tracker:  ## should be one for each (scrolling) background 
### --------------------------------------------------------
    def __init__(self, file, direction, mirroring, fact):
        super().__init__()

        self.file = file
        self.direction = direction
        self.mirroring = mirroring
        self.factor    = fact
        
### --------------------------------------------------------  
class BkgWorks:  
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()

        self.bkgItem  = parent     
        self.bkgMaker = self.bkgItem.bkgMaker
        self.canvas   = self.bkgItem.canvas
        self.dots     = self.bkgItem.dots
 
### -------------------------------------------------------- 
    def addTracker(self, pix):  ## when loading a play file and adding from screen
        file = os.path.basename(pix.fileName)    
        # fact = float((random.randint(17,30) *5)/100)  ## .85-1.50
        fact = 1.0  ## default
        if len(self.bkgMaker.directions) == 0:
            x = Tracker(file, pix.direction, pix.mirroring, fact)
            self.bkgMaker.directions.append(x)
            # print( f'inital  {file}\t{pix.direction}\t{pix.mirroring}\t{x.factor}\t{pix.zValue()}')
            return True
        else:
            k = 0
            for p in self.bkgMaker.directions:  ## see if it's already there
                if p.file == file:
                    k += 1
            if k == 0:  ## no others found - add it 
                x = Tracker(file, pix.direction, pix.mirroring, fact)
                self.bkgMaker.directions.append(x) 
                # print( f'adding  {file}\t{pix.direction}\t{pix.mirroring}\t{x.factor}\t{pix.zValue()}')
                return True
            else:
                return False  ## must be a duplicate, skip processing 
            
### --------------------------------------------------------                                                                                
    def setDirection(self, key):  ## from keybooard or widget - sets 'first'      
        if math.fabs(self.bkgItem.runway) < self.bkgItem.showtime:
            self.notScrollable()   
            return   
        
        if self.bkgItem.scrollable:  ## only place where scroller is set except demos 
            if self.dots.Vertical: 
                key = 'vertical'        
            self.bkgItem.direction = key  
            self.bkgItem.tag = 'scroller'
                 
            file = os.path.basename(self.bkgItem.fileName)  
            for p in self.bkgMaker.directions:
                if p.file == file:
                    p.direction = self.bkgItem.direction 
                    
            self.bkgMaker.lockBkg()
                
            self.setBtns()
                  
### -------------------------------------------------------- 
    def setMirroring(self):
        if self.bkgItem.scrollable:                                  
            if self.bkgItem.mirroring == True: 
                self.bkgItem.mirroring = False
            else:
                self.bkgItem.mirroring = True  
                                   
        file = os.path.basename(self.bkgItem.fileName)  
        for p in self.bkgMaker.directions:
            if p.file == file:
                p.mirroring = self.bkgItem.mirroring 
                                            
        self.setMirrorBtnText() 

### -------------------------------------------------------- 
    def restoreDirections(self, pix, where):  ## returns what gets lost on each reincarnation
        file = os.path.basename(pix.fileName)  ## opposite of setMirroring
        for p in self.bkgMaker.directions:
            if p.file == file:
                pix.mirroring = p.mirroring   
                pix.direction = p.direction 
                return p.factor
       
    def setLeft(self):
        if self.bkgItem.scrollable:
            self.setDirection('left')      
        else:
            self.notScrollable() 
               
    def setRight(self):
        if self.bkgItem.scrollable: 
            self.setDirection('right')             
        else:
            self.notScrollable() 

### -------------------------------------------------------- 
    def setBtns(self):
        if self.bkgItem:
            if self.bkgItem.direction == 'right': 
                self.bkgMaker.widget.rightBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                self.bkgMaker.widget.leftBtn.setStyleSheet(
                    'background-color: None')            
            elif self.bkgItem.direction == 'left': 
                self.bkgMaker.widget.leftBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                self.bkgMaker.widget.rightBtn.setStyleSheet(
                    'background-color: None')
            elif self.bkgItem.direction == 'vertical':
                self.bkgMaker.widget.leftBtn.setText('Vertical')   
                self.bkgMaker.widget.leftBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                                                  
    def setMirrorBtnText(self):  ## if added 
        if self.bkgItem:  ## shouldn't need this but - could have just started to clear                         
            if self.bkgItem.scrollable == False:
                self.bkgMaker.widget.mirrorBtn.setText('Not Scrollable')         
            elif self.bkgItem.mirroring == True:
                self.bkgMaker.widget.mirrorBtn.setText('Mirroring On')         
            elif self.bkgItem.mirroring == False:
                self.bkgMaker.widget.mirrorBtn.setText('Mirroring Off')    
                                   
    def reset(self):
        file = os.path.basename(self.bkgItem.fileName)  ## opposite of setMirroring
        for p in self.bkgMaker.directions:
            if p.file == file:
                p.direction = ''
                p.mirroring = True
        self.bkgItem.tag = ''                
        self.bkgItem.mirroring = True   
        self.bkgItem.direction = ''
        self.bkgMaker.widget.close()
        self.bkgMaker.addWidget(self.bkgItem)
                                     
    def setMatte(self):
        self.bkgMaker.closeWidget()
        self.bkgMaker.matte = Matte(self.bkgItem)  
                                          
### --------------------------------------------------------                
    def left(self, path, pix, rate, which, fact):  ## which rate to use, 1 == rate[0] 
        if which == 'first':
            path.setDuration(int(common['ViewW'] * (rate[0]*fact)))  ## rate time equals time to clear   
            path.setStartValue(QPoint(0,0)) 
            path.setEndValue(QPoint(-int(pix.width), 0))
        else:    
            rate_one = rate[1]
            # if 'snakes' in pix.fileName:  ## looks better and not another dictionary to maintain
            #     rate_one = rate_one + .2
            path.setDuration(int(common['ViewW'] * (rate_one*fact)))    
            path.setStartValue(QPoint(common['ViewW'], 0))
            path.setEndValue(QPoint(int(-pix.width), 0))
        return path
    
    def right(self, path, pix, rate, which, fact):  ## which column to read from
        if which == 'first':        
            path.setDuration(int(common['ViewW'] * (rate[0]*fact)))
            path.setStartValue(QPoint(self.bkgItem.runway, 0))
            path.setEndValue(QPoint(int(common['ViewW']), 0))
        else:
            path.setDuration(int(common['ViewW'] * (rate[2]*fact)))  
            path.setStartValue(QPoint(-self.bkgItem.width, 0))
            path.setEndValue(QPoint(int(common['ViewW']), 0))
        return path
                     
    def vertical(self, path, pix, rate, which, fact):       
        if which == 'first': 
            path.setDuration(int(common['ViewH'] * (rate[0]*fact)))  ## rate time equals time to clear   
            path.setStartValue(QPoint(0, self.bkgItem.runway+self.bkgItem.showtime))
            path.setEndValue(QPoint(0, -self.bkgItem.height))
        else:    
            rate_one = rate[1]
            if 'snakes' in pix.fileName:  
                rate_one = rate_one + .2
            path.setDuration(int(common['ViewH'] * (rate_one*fact)))    
            path.setStartValue(QPoint(0, self.bkgItem.height+self.bkgItem.runway))
            path.setEndValue(QPoint(0, -self.bkgItem.height))
        return path       
   
### --------------------------------------------------------                    
    def notScrollable(self):
        MsgBox('Not Scrollable and Unable to Fulfill your Request...', 6) 
        self.bkgItem.scrollable = False  
        return  
           
    def setStatusBar(self):
        self.dots.statusBar.showMessage(os.path.basename(self.bkgItem.fileName) + '    ' + \
            'Width:   '  + '  ' + str(self.bkgItem.width)       + '    ' +\
            'Runway:   ' + '  ' + str(abs(self.bkgItem.runway)) + '    ' +\
            'ShowTime: ' + '  ' + str(self.bkgItem.showtime)    + '    ' +\
            'Ratio: '    + '  ' + str(self.bkgItem.ratio)+ ':9')
  
    def setWidthHeight(self, img):              
        imf = img.scaledToHeight(self.bkgItem.ViewH, Qt.TransformationMode.SmoothTransformation)
        if imf.width() > self.bkgItem.ViewW:  ## its scrollable enough
            self.bkgItem.imgFile = imf
            self.bkgItem.scrollable = True               
        else:   
            self.bkgItem.imgFile = img.scaled(  ## fill to width or height
                self.bkgItem.ViewW, 
                self.bkgItem.ViewH,
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        del img
        del imf
        
    def setVertical(self, img):  
        imf = img.scaledToWidth(self.bkgItem.ViewW, Qt.TransformationMode.SmoothTransformation)
        self.bkgItem.imgFile = imf
        self.bkgItem.scrollable = True   
        del img 
        del imf
    
 ### -------------------------------------------------------- 
class Flat(QGraphicsPixmapItem):
### --------------------------------------------------------   
    def __init__(self, color, canvas, z=common['bkgZ']):
        super().__init__()

        self.canvas   = canvas
        self.scene    = canvas.scene
        self.bkgMaker = self.canvas.bkgMaker
        
        self.type = 'bkg'
        self.color = color
        
        self.fileName = 'flat'
        self.locked = False
        
        self.tag = ''
        self.id = 0   

        p = QPixmap(common['ViewW'],common['ViewH'])
        p.fill(self.color)
        
        self.setPixmap(p)
        self.setZValue(z)
   
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        
### --------------------------------------------------------
    def mousePressEvent(self, e):      
        if not self.canvas.pathMakerOn:
            if e.button() == Qt.MouseButton.RightButton:    
                self.bkgMaker.addWidget(self)        
            elif self.canvas.key == 'del':     
                self.delete()
            elif self.canvas.key == '/':  ## to back
                self.bkgMaker.back(self)
            elif self.canvas.key in ('enter','return'):  
                self.bkgMaker.front(self)                             
        e.accept()
      
    def mouseReleaseEvent(self, e):
        if not self.canvas.pathMakerOn:
            self.canvas.key = ''       
        e.accept()
     
    def delete(self):  ## also called by widget
        self.bkgMaker.deleteBkg(self)
                                                                                
### --------------------- dotsBkgWorks ---------------------


        