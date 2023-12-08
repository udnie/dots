
import os.path
import math
import random

from PyQt6.QtCore       import Qt, QPoint
from PyQt6.QtGui        import QColor
from PyQt6.QtWidgets    import QGraphicsSimpleTextItem
                        
from dotsShared         import common
from dotsSideGig        import MsgBox, point
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
    def addTracker(self, bkg):  ## when loading a play file and adding from screen
        file = os.path.basename(bkg.fileName) 
        ## bkg.factor is set to 1.0  ## default - if it's running slow - lower it to .85 in bkgItem 
        ## if randomizing speed factor do this 
        
        # fact = float((random.randint(17,30) *5)/100)  ## .85-1.50
        # bkg.factor = fact  ## if using a random screen speed factor 
          
        if len(self.bkgMaker.trackers) == 0:
            x = Tracker(file, bkg.direction, bkg.mirroring, bkg.factor)
            self.bkgMaker.trackers.append(x)
            # self.filePixX(file, bkg, x)  ## for debug
            return True
        else:
            k = 0
            for p in self.bkgMaker.trackers:  ## see if it's already there
                if p.file == file:
                    k += 1
            if k == 0:  ## no others found - add it 
                x = Tracker(file, bkg.direction, bkg.mirroring, bkg.factor)
                self.bkgMaker.trackers.append(x) 
                # self.filePixX(file, bkg, x)
                return True
            else:
                return False  ## must be a duplicate, skip processing 
            
    def filePixX(self, file, bkg, x):
        print( f'tracker {file}\t{bkg.direction}\t{bkg.mirroring}\t{bkg.factor}\t{bkg.zValue()}')
              
    def delTracker(self, bkg):
        file = os.path.basename(bkg.fileName)  
        for item in self.bkgMaker.trackers:  ## see if it's already there
            if item.file == file:  
                self.bkgMaker.trackers.remove(item)
                break
                         
### --------------------------------------------------------                                                                                
    def setDirection(self, key):  ## from keybooard or widget - sets 'first'      
        if math.fabs(self.bkgItem.runway) < self.bkgItem.showtime:
            self.notScrollable()   
            return     
        if self.bkgItem.scrollable:  ## only place where scroller is set except demos 
            if self.dots.Vertical:   ## no direction equals 'not scrollable'
                self.bkgItem.direction = 'vertical'
            else:
                self.bkgItem.direction = key
            self.bkgItem.tag = 'scroller'    
            file = os.path.basename(self.bkgItem.fileName) 
            for p in self.bkgMaker.trackers:
                if p.file == file:
                    p.direction = self.bkgItem.direction 
                    break 
            self.bkgMaker.lockBkg()      
            self.setBtns()
                  
### -------------------------------------------------------- 
    def setMirroring(self):
        if self.bkgItem.scrollable:                                  
            if self.bkgItem.mirroring == True: 
                self.bkgItem.mirroring = False ## continuous
            else:
                self.bkgItem.mirroring = True  ## mirrored                               
        file = os.path.basename(self.bkgItem.fileName)  
        for p in self.bkgMaker.trackers:
            if p.file == file:
                p.mirroring = self.bkgItem.mirroring    
                break                                    
        self.setMirrorBtnText() 
               
    def setFactor(self):
        if self.bkgItem.scrollable:                                                               
            file = os.path.basename(self.bkgItem.fileName)  
            for p in self.bkgMaker.trackers:
                if p.file == file:
                    p.factor = self.bkgItem.factor
                    break

### --------------------------------------------------------
    def left(self, path, bkg, rate, which, fact):  ## which rate to use, 1 == rate[0] 
        if which == 'first':
            path.setDuration(int(common['ViewW'] * (rate[0]*fact)))  ## rate time equals time to clear   
            path.setStartValue(QPoint(0,0)) 
            path.setEndValue(QPoint(-int(bkg.width), 0))
        else:    
            rate_one = rate[1]
            path.setDuration(int(common['ViewW'] * (rate_one*fact)))    
            path.setStartValue(QPoint(common['ViewW'], 0))
            path.setEndValue(QPoint(int(-bkg.width), 0))
        return path

    def right(self, path, bkg, rate, which, fact):  ## which column to read from
        if which == 'first':        
            path.setDuration(int(common['ViewW'] * (rate[0]*fact)))
            path.setStartValue(QPoint(bkg.runway, 0))
            path.setEndValue(QPoint(int(common['ViewW']), 0))
        else:
            path.setDuration(int(common['ViewW'] * (rate[2]*fact)))  
            path.setStartValue(QPoint(-bkg.width, 0))
            path.setEndValue(QPoint(int(common['ViewW']), 0))
        return path
                     
    def vertical(self, path, bkg, rate, which, fact):                 
        if which == 'first': 
            path.setDuration(int(common['ViewH'] * (rate[0]*fact)))  ## rate time equals time to clear   
            path.setStartValue(QPoint(0, bkg.runway))
            path.setEndValue(QPoint(0, -bkg.height))
        else:    
            rate_one = rate[1]  
            # if 'snakes' in bkg.fileName:  ## early kludge  
            #     rate_one = rate_one + .2 
            path.setDuration(int(common['ViewH'] * (rate_one*fact))) 
            ## current kludge advances background into scene before starting - also doubled showtime 
            path.setStartValue(QPoint(0, common['ViewH']-int(bkg.showtime*.75)))
            path.setEndValue(QPoint(0, -bkg.height))
        return path       

### -------------------------------------------------------- 
    def restoreFromTrackers(self, bkg, where):  ## returns what gets lost on each reincarnation
        file = os.path.basename(bkg.fileName)  ## opposite of setMirroring
        for p in self.bkgMaker.trackers:
            if p.file == file:
                bkg.mirroring = p.mirroring   
                bkg.direction = p.direction 
                bkg.factor    = p.factor
                return bkg.factor
                    
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
            elif self.bkgItem.mirroring == False:
                self.bkgMaker.widget.mirrorBtn.setText('Continuous')         
            elif self.bkgItem.mirroring == True:
                self.bkgMaker.widget.mirrorBtn.setText('Mirrored')    
                                   
    def reset(self):
        file = os.path.basename(self.bkgItem.fileName)  ## opposite of setMirroring
        for p in self.bkgMaker.trackers:
            if p.file == file:
                p.direction = ''
                p.mirroring = self.bkgMaker.mirroring
                p.factor    = self.bkgMaker.factor
                break
        self.bkgItem.tag = ''   
        self.bkgItem.direction = ''             
        self.bkgItem.mirroring = self.bkgMaker.mirroring  
        self.bkgItem.factor    = self.bkgMaker.factor
        self.bkgMaker.widget.close()
        self.bkgMaker.addWidget(self.bkgItem)
              
    def centerBkg(self):
        if self.bkgItem != None and self.bkgItem.fileName != 'flat':  
            width = self.bkgItem.imgFile.width()
            height = self.bkgItem.imgFile.height()
            self.bkgItem.x = (common['ViewW']- width)/2
            self.bkgItem.y = (common['ViewH']- height)/2
            self.bkgItem.setPos(self.bkgItem.x, self.bkgItem.y) 
                                           
    def setMatte(self):
        self.bkgMaker.closeWidget()
        self.bkgMaker.matte = Matte(self.bkgItem)  
      
    def toggleBkgLock(self):
        if self.bkgItem:  
            if self.bkgItem.locked == False:
                self.bkgMaker.lockBkg()
            else:
                self.bkgMaker.unlockBkg()
                               
    def tagBkg(self, bkg, pos):
        self.bkgItem = bkg
        x, y = pos.x(), pos.y()
        z = self.bkgItem.zValue()
        file, direction, mirror, locked = self.canvas.sideCar.addBkgLabels(bkg)    
        tag = f'{file}\t{direction}\t{mirror}\t{locked}'       
        self.canvas.mapper.pathsAndTags.TagItTwo('bkg', tag,  QColor('orange'), x, y, z, 'bkg')
                                                          
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
        if imf.height() > self.bkgItem.ViewH:  ## its scrollable enough
            self.bkgItem.scrollable = True  
        del img 
        del imf
                                                                                    
### --------------------- dotsBkgWorks ---------------------


        