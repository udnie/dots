
import os
import json

from PyQt6.QtCore       import Qt, QPoint, QTimer
from PyQt6.QtGui        import QImage, QPixmap, QCursor
from PyQt6.QtWidgets    import QMessageBox
                    
from dotsShared         import common, paths                             
from dotsSideGig        import MsgBox, tagBkg

''' trigger a new scrolling background based on the number 
    of pixels remaining in runway '''
showtime = {   
    'snakes':   15,  ## also used by vertical 
    'left':     10, 
    'right':    10,  
    'vertical': 15,  ## trying this out 
}

''' screenrates not current - updated in ../plays/screenrates.dict
screenrates = {
    '800':  [10.0, 22.76,   0.0], 
    '900':  [10.0, 23.2,    0.0], 
    '912':  [10.0, 21.1,    0.0],
    '960':  [10.0, 16.75, 16.75], 
    '1080': [10.0, 17.57, 17.72], 
    '108O': [10.0, 16.79, 16.79],
    '1066': [10.0, 21.84,   0.0], 
    '1024': [10.0, 21.31,   0.0], 
    '1102': [10.0, 21.3,    0.0], 
    '1215': [10.0, 17.35, 17.40], 
    '1280': [10.0, 18.92, 19.07], 
    '1440': [10.0, 18.7,  18.82],  
} 

screenrates for hats demo - in ../demo with shadow-wrp.jpg 
shadows = { 
    "SQH":  [10.0, 13.20, 13.20],   ##  1:1  
    "960":  [10.0, 14.75, 14.75],   ##  4:3 
    "1080": [10.0, 14.75, 14.75],   ##  3:2
    "1280": [10.0, 15.60, 15.60],   ## 16:9
    "108O": [10.0, 14.25, 14.25],   ##  4:3
    "1215": [10.0, 14.75, 14.75],   ##  3:2
    "1440": [10.0, 15.65, 15.65],   ## 16:9
}  '''

''' use these to read and dump the current screen rates '''
# with open(paths['playPath'] +  "screenrates.dict", 'r') as fp:
#     screenrates = json.load(fp) 
# for k, vals in screenrates.items():
#     print( f'{k.rjust(5)} {str(vals[0]).rjust(6)}  {vals[1]:6.2f}  {vals[2]:5.2f} ') 

### ------------------ dotsBkgScrollWrks -------------------  
''' screen rates examples, updateDictionary, tracker and scrolling functions '''
### --------------------------------------------------------        
class BkgScrollWrks: 
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()

        self.bkgItem  = parent    
        self.canvas   = self.bkgItem.canvas 
        self.bkgMaker = self.bkgItem.bkgMaker
                                                                                                                                        
### -------------------------------------------------------- 
    def updateDictionary(self):
        test = False
        rate = self.bkgMaker.screenrate.get(common['Screen'])   
  
        if rate == None:
            MsgBox("Error Reading ScreenRates", 5)
            return   

        if self.bkgItem.direction == 'right' and rate[2] != self.bkgItem.rate:
            rate[2] = self.bkgItem.rate
            test = True
            
        elif self.bkgItem.direction == 'left' and rate[1] != self.bkgItem.rate:
            rate[1] = self.bkgItem.rate
            test = True      
              
        elif self.bkgItem.direction == 'vertical' and rate[1] != self.bkgItem.rate:
            rate[1] = self.bkgItem.rate
            test = True  
              
        if not test:
            MsgBox("Screen Rates Haven't Changed", 5)
            return   
    
        img = QImage(paths['spritePath'] + "doral.png")  ## icon .png
        img = img.scaled(60, 60,  ## keep it small
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)  
        pixmap = QPixmap(img)    
   
        msgbox = QMessageBox()
        msgbox.setIconPixmap(pixmap)
        msgbox.setText("Update the Screen Rate Value?")
        msgbox.setStandardButtons(msgbox.StandardButton.Yes |msgbox.StandardButton.No)
        answer = msgbox.exec()

        if answer == msgbox.StandardButton.No:
            return   
         
        if self.canvas.openPlayFile == 'hats':
            try:  
                with open(paths['demo'] +  "demorates.dict", 'w') as fp:
                    json.dump(self.bkgMaker.screenrate, fp)
            except:
                MsgBox('Error Updating Rates Dictionary', 5)
                return
        else:
            try:
                with open(paths['playPath'] +  "screenrates.dict", 'w') as fp:  
                    json.dump(self.bkgMaker.screenrate, fp)
            except:
                MsgBox('Error Updating Rates Dictionary', 5)
                return 
        MsgBox('Rates Dictionary Updated' ,5)
        return
       
### --------------------------------------------------------
    ## snakes need more time - the rest vary to build and position and comes before vertical  
    def setShowTime(self): 
        fileName = self.bkgItem.fileName
        if show := self.bkgMaker.newTracker[fileName]['showtime']:
            return show   
        show = 0
        if 'snakes' in self.bkgItem.fileName and self.bkgItem.direction != 'vertical':
            show = showtime['snakes']    
                 
        elif self.bkgItem.direction == 'vertical':  ## see vertical in bkgWorks - there's a kludge
            show = showtime['vertical']   ## uses 'snakes_912.jpg'
              
        elif self.bkgItem.direction == 'left':   
            show = showtime['left']
            
        elif self.bkgItem.direction == 'right':  
            show = showtime['right']                                             
        return show

### --------------------------------------------------------
    def setTrackerRate(self, bkg):
        if bkg.scrollable:                                                                          
            fileName = bkg.fileName   
            if self.bkgMaker.newTracker.get(fileName):
                self.bkgMaker.newTracker[fileName]['direction'] = bkg.direction
                self.bkgMaker.newTracker[fileName]['rate']      = bkg.rate 
              
    def setShowTimeTrackers(self, bkg):  ## used by resetSliders
        if bkg.scrollable:      
            fileName = bkg.fileName                                                            
            if self.bkgMaker.newTracker.get(fileName):  
                self.bkgMaker.newTracker[fileName]['direction'] = bkg.direction 
                self.bkgMaker.newTracker[fileName]['showtime']  = bkg.showtime 
                               
    def setTrackerFactor(self, bkg):
        if bkg.scrollable:   
            if self.bkgMaker.newTracker.get(bkg.fileName):
                self.bkgMaker.newTracker[bkg.fileName]['factor'] = bkg.factor          
            
    def getTrackerRate(self, bkg):  ## used only once - getScreenRate
        if rate := self.bkgMaker.newTracker[bkg.fileName]['rate']:  
            return rate
        return 0  
           
### --------------------------------------------------------    
    def setRunWay(self):      
        if not self.canvas.dots.Vertical:             
            self.bkgItem.runway = int(common['ViewW'] - self.bkgItem.width)  ## pixels outside of view
        else:
            self.bkgItem.runway = int(common['ViewH'] - self.bkgItem.height) 
   
    def setMirroring(self):
        if self.bkgItem.scrollable:                                  
            self.bkgItem.mirroring = False if self.bkgItem.mirroring \
                else True  ## it's mirrored   
                                                 
        fileName = self.bkgItem.fileName         
             
        if self.bkgMaker.newTracker[fileName]:  
            self.bkgMaker.newTracker[fileName]['mirroring'] = self.bkgItem.mirroring                            
            self.setMirrorBtnText(self.bkgItem, self.bkgMaker.widget) 
                            
    def setLeft(self):     
        self.bkgItem.bkgWorks.setDirection('left') if self.bkgItem.isScrollable()\
            else self.bkgItem.notScrollable()  

    def setRight(self): 
        self.bkgItem.bkgWorks.setDirection('right') if self.bkgItem.isScrollable()\
            else self.bkgItem.notScrollable()  
                    
    def setWidthHeight(self, img):     
        if img == None:
            return   
        img = img.scaledToHeight(self.bkgItem.ViewH, Qt.TransformationMode.SmoothTransformation) 
        if img.width() > (self.bkgItem.ViewW + 10):  ## isScrollable doesn't work here
            self.bkgItem.imgFile = img  ## width and height haven't been set yet - based on img.size
        else:  
            try:
                self.bkgItem.imgFile = img.scaled(  ## fill to width or height
                    self.bkgItem.ViewW, 
                    self.bkgItem.ViewH,
                    Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            except:
                self.clearBkgScrolling() 
                return None
        del img
              
    def setVertical(self, img):  
        if img == None:
            return
        try:
            img = img.scaledToWidth(self.bkgItem.ViewW, Qt.TransformationMode.SmoothTransformation)
            self.bkgItem.imgFile = img     
            if img.height() < (self.bkgItem.ViewH+10):  ## isScrollable won't work here - see above
                self.clearBkgScrolling()   
        except:
            self.clearBkgScrolling() 
            return None
        del img 
   
    def clearBkgScrolling(self):
        self.bkgItem.scrollable = False 
        self.bkgItem.tag = ''
        self.bkgItem.direction = ''
        self.bkgItem.rate = 0
        self.bkgItem.showtime = 0
        if self.bkgMaker.newTracker.get(self.bkgItem.fileName):
            self.bkgMaker.newTracker[self.bkgItem.fileName]['direction'] = 0
            self.bkgMaker.newTracker[self.bkgItem.fileName]['rate'] = 0
                
### --------------------------------------------------------
    def toggleBkgLocks(self):
        if self.bkgItem:
            self.bkgMaker.lockBkg(self.bkgItem) if not self.bkgItem.locked else\
                self.bkgMaker.unlockBkg(self.bkgItem)  
                
            if self.bkgMaker.widget != None:     
                p = self.canvas.mapFromGlobal(QCursor.pos())  
                tagBkg(self.bkgItem, QPoint(int(p.x())+200,int(p.y())+50))
                QTimer.singleShot(3000, self.canvas.mapper.clearTagGroup)
                                                                                               
    def filePixX(self, file, bkg):  ## also see dumpTrackers
        print(f'tracker {bkg.fileName}\t{bkg.direction}\t{bkg.mirroring}\t{bkg.rate}\t{bkg.factor}\t{bkg.zValue()}')
                                                                                   
    def setMirrorBtnText(self, bkg, widget):  ## if added - from bkgMaker widget
        if bkg:  ## shouldn't need this but - could have just started to clear        
            if not self.canvas.dots.Vertical and bkg.imgFile.width() >= bkg.showtime + bkg.ViewW or \
                self.canvas.dots.Vertical and bkg.imgFile.height() >= bkg.showtime + bkg.ViewH:  
                bkg.scrollable = True    
                                                  
            if not bkg.isScrollable():
                widget.mirrorBtn.setText('Not Scrollable')  
                self.clearBkgScrolling()
                          
            widget.mirrorBtn.setText('Continuous') if not bkg.mirroring else \
                widget.mirrorBtn.setText('Mirrored')
              
### ------------------ dotsBkgScrollWrks -------------------                                                                                                     
             
             




