
import json
import time

from PyQt6.QtCore       import Qt, QPoint, QTimer
from PyQt6.QtGui        import QCursor
                
from dotsShared         import common, paths                          
from dotsSideGig        import tagBkg, MsgBox

''' Settings for scrolling Backgrounds, Tracker and scrolling functions 
    '''

BackUp = {  ## original settings in case you need to reset
    'ShowTime':   4,
    'RunWay':    44,
    'OffSet':   105,
}

### ------------------ dotsBkgScrollWrks -------------------      
class BkgScrollWrks: 
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()

        self.bkgItem  = parent    
        self.canvas   = self.bkgItem.canvas 
        self.bkgMaker = self.bkgItem.bkgMaker
      
        self.fromBackUp = False
        self.settings = self.getSettings()  
        if self.fromBackUp:  
            self.update()
            
### --------------------------------------------------------  
    def updWrks(self, settings):  ## settings and scrollWidget
        self.settings = settings
 
    def getSettings(self):  
        try:  
            with open(paths['playPath'] +  "settings.json", 'r') as fp: 
                return json.load(fp)    
        except:
            self.settings = BackUp 
            self.fromBackUp = True
        return self.settings
  
    def update(self):
        try:
            with open(paths['playPath'] +  "settings.json", 'w') as fp:  
                json.dump(self.settings, fp)
        except:
            MsgBox('Error writing settings file', 5)
            return
        time.sleep(.05)
        if not self.fromBackUp:
            self.canvas.sideCar2.scrollingUpdates(self.bkgItem)
        
    def closeScrollWidget(self):
        if self.bkgItem.scrollWidget:
            self.bkgItem.scrollWidget.close()
            self.bkgItem.scrollWidget = None

### --------------------------------------------------------                    
    def setRunWay(self):  ## set in add.bkgItem       
        if not self.canvas.dots.Vertical:             
            self.bkgItem.runWay = int(common['ViewW'] - self.bkgItem.width)  ## pixels outside of view
        else:
            self.bkgItem.runWay = int(common['ViewH'] - self.bkgItem.height)        
            
    def setTrackerRate(self, bkg):
        if bkg.scrollable:                                                                          
            fileName = bkg.fileName   
            if self.bkgMaker.newTracker.get(fileName):
                self.bkgMaker.newTracker[fileName]['direction'] = bkg.direction
                self.bkgMaker.newTracker[fileName]['rate']      = bkg.rate 
                                         
    def setTrackerFactor(self, bkg):
        if bkg.scrollable:   
            if self.bkgMaker.newTracker.get(bkg.fileName):
                self.bkgMaker.newTracker[bkg.fileName]['factor'] = bkg.factor          
            
    def getTrackerRate(self, bkg):  ## used only once - getScreenRate
        if rate := self.bkgMaker.newTracker[bkg.fileName]['rate']:  
            return rate
        return 0  

### -------------------------------------------------------- 
    def setMirroring(self):
        if self.bkgItem.scrollable:                                  
            self.bkgItem.mirroring = False if self.bkgItem.mirroring \
                else True  ## it's mirrored   
                                                 
        fileName = self.bkgItem.fileName           
        if self.bkgMaker.newTracker[fileName]:  
            self.bkgMaker.newTracker[fileName]['mirroring'] = self.bkgItem.mirroring                            
            self.setMirrorBtnText(self.bkgItem, self.bkgMaker.widget) 
                            
    def setLeft(self):     
        self.bkgItem.bkgWorks.setDirection('left') if self.bkgItem.isScrollable() \
            else self.bkgItem.notScrollable()  

    def setRight(self): 
        self.bkgItem.bkgWorks.setDirection('right') if self.bkgItem.isScrollable() \
            else self.bkgItem.notScrollable()  

### --------------------------------------------------------                     
    def setWidthHeight(self, img):     
        if img == None:
            return   
        img = img.scaledToHeight(common['ViewH'], Qt.TransformationMode.SmoothTransformation) 
        if img.width() > (common['ViewW'] + 10):  ## isScrollable doesn't work here
            self.bkgItem.imgFile = img  ## width and height haven't been set yet - based on img.size
        else:  
            try:
                self.bkgItem.imgFile = img.scaled(  ## fill to width or height
                    common['ViewW'], 
                    common['ViewH'],
                    Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            except:
                self.clearBkgScrolling() 
                return None
        img = None
              
    def setVertical(self, img):  
        if img == None:
            return
        try:
            img = img.scaledToWidth(common['ViewW'], Qt.TransformationMode.SmoothTransformation)
            self.bkgItem.imgFile = img     
            if img.height() < (common['ViewH']+10):  ## isScrollable won't work here - see above
                self.clearBkgScrolling()   
        except:
            self.clearBkgScrolling() 
            return None
        img = None 
   
    def clearBkgScrolling(self):
        self.bkgItem.scrollable = False 
        self.bkgItem.tag = ''
        self.bkgItem.direction = ''
        self.bkgItem.rate = 0
        if self.bkgMaker.newTracker.get(self.bkgItem.fileName):
            self.bkgMaker.newTracker[self.bkgItem.fileName]['direction'] = 0
            self.bkgMaker.newTracker[self.bkgItem.fileName]['rate'] = 0
                
### --------------------------------------------------------
    def toggleBkgLocks(self):
        if self.bkgItem:
            self.bkgMaker.lockBkg(self.bkgItem) if not self.bkgItem.locked else \
                self.bkgMaker.unlockBkg(self.bkgItem)  
                
            if self.bkgMaker.widget != None:     
                p = self.canvas.mapFromGlobal(QCursor.pos())  
                tagBkg(self.bkgItem, QPoint(int(p.x())+200,int(p.y())+50))
                QTimer.singleShot(3000, self.canvas.mapper.clearTagGroup)
                                                                                               
    def filePixX(self, file, bkg):  ## also see dumpTrackers
        print(f'tracker {bkg.fileName}\t{bkg.direction}\t{bkg.mirroring}\t{bkg.rate}\t{bkg.factor}\t{bkg.zValue()}')
                                                                                   
    def setMirrorBtnText(self, bkg, widget):  ## if added - from bkgMaker widget
        if bkg:  ## shouldn't need this but - could have just started to clear        
            if not self.canvas.dots.Vertical and bkg.imgFile.width() >= common['ViewW'] or \
                self.canvas.dots.Vertical and bkg.imgFile.height() >= common['ViewH']:
                bkg.scrollable = True    
                                                  
            if not bkg.isScrollable():
                widget.mirrorBtn.setText('Not Scrollable')  
                self.clearBkgScrolling()
                          
            widget.mirrorBtn.setText('Continuous') if not bkg.mirroring else \
                widget.mirrorBtn.setText('Mirrored')
              
### ------------------ dotsBkgScrollWrks -------------------                                                                                                     
             
             


