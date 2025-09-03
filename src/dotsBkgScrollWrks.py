
import os
import json

from PyQt6.QtCore       import Qt, QPoint, QTimer
from PyQt6.QtGui        import QImage, QPixmap, QCursor
from PyQt6.QtWidgets    import QMessageBox
                    
from dotsShared         import common, paths                             
from dotsSideGig        import MsgBox, tagBkg


showtime = {   ## trigger a new background based on the number of pixels left in runway
    'snakes':   15,  ## also used by vertical 
    'left':     11, 
    'right':    15,  
    'vertical': 17,  ## trying this out 
}

# screentimes = {  ## may not be current
#     '800': [10.0, 22.76, 0.0], 
#     '900': [10.0, 23.2, 0.0], 
#     '912': [10.0, 21.1, 0.0],
#     '960': [10.0, 16.75, 16.75], 
#     '1080': [10.0, 17.57, 17.72], 
#     '108O': [10.0, 16.79, 16.79],
#     '1066': [10.0, 21.84, 0.0], 
#     '1024': [10.0, 21.31, 0.0], 
#     '1102': [10.0, 21.3, 0.0], 
#     '1215': [10.0, 17.35, 17.4], 
#     '1280': [10.0, 18.92, 19.07], 
#     '1296': [10.0, 17.5, 17.45],
#     '1440': [10.0, 18.7, 18.82],  
#     '1536': [10.0, 18.65, 18.92], 
# }

## read and dump the current screen rates
# with open(paths['playPath'] +  "screenrates.dict", 'r') as fp:
#     screenrate = json.load(fp) 

# for k, vals in screenrate.items():
#     print( f'{k.rjust(5)} {str(vals[0]).rjust(6)}  {vals[1]:6.2f}  {vals[2]:5.2f} ') 
 
### ------------------ dotsBkgScrollWrks -------------------  
''' updateDictionary, tracker and scrolling functions '''
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
         
        if self.bkgItem.direction == 'right' and rate[2] != self.bkgItem.rate:
            rate[2] = self.bkgItem.rate
            test = True
        elif self.bkgItem.direction == 'left' and rate[1] != self.bkgItem.rate:
            rate[1] = self.bkgItem.rate
            test = True        
        elif self.bkgItem.direction == 'vertical' and rate[1] != self.bkgItem.rate:
            rate[1] = self.bkgItem.rate
            test = True  
              
        if test == False:
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
        try:
            with open(paths['playPath'] +  "screenrates.dict", 'w') as fp:  
                json.dump(self.bkgMaker.screenrate, fp)
            MsgBox('Rates Dictionary Updated' ,5)
        except:
            MsgBox('Error Updating Rates Dictionary', 5)
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
            show = showtime['vertical']       
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
                   
    def setLeft(self):
        if self.bkgItem.scrollable:
            self.bkgItem.bkgWorks.setDirection('left')      
        else:
            self.notScrollable() 
               
    def setRight(self):
        if self.bkgItem.scrollable: 
            self.bkgItem.bkgWorks.setDirection('right')             
        else:
            self.notScrollable()
    
    def setWidthHeight(self, img):     
        if img == None:
            return   
        imf = img.scaledToHeight(self.bkgItem.ViewH, Qt.TransformationMode.SmoothTransformation) 
        if imf.width() > self.bkgItem.ViewW:  ## its scrollable enough
            self.bkgItem.imgFile = imf
            self.bkgItem.scrollable = True               
        else:   
            try:
                self.bkgItem.imgFile = img.scaled(  ## fill to width or height
                    self.bkgItem.ViewW, 
                    self.bkgItem.ViewH,
                    Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            except:
                del img
                del imf
                 
    def setVertical(self, img):  
        if img == None:
            return
        imf = img.scaledToWidth(self.bkgItem.ViewW, Qt.TransformationMode.SmoothTransformation)
        self.bkgItem.imgFile = imf       
        if imf.height() > self.bkgItem.ViewH:  ## its scrollable enough
            self.bkgItem.scrollable = True  
        del img 
        del imf
                
### --------------------------------------------------------
    def toggleBkgLocks(self):
        if self.bkgItem:
            if self.bkgItem.locked == False:
                self.bkgMaker.lockBkg(self.bkgItem) 
            else:
                self.bkgMaker.unlockBkg(self.bkgItem)  
            if self.bkgMaker.widget != None:     
                p = self.canvas.mapFromGlobal(QCursor.pos())  
                tagBkg(self.bkgItem, QPoint(int(p.x())+200,int(p.y())+50))
                QTimer.singleShot(3000, self.canvas.mapper.clearTagGroup)
                                                                                               
    def filePixX(self, file, bkg):  ## also see dumpTrackers
        print(f'tracker {bkg.fileName}\t{bkg.direction}\t{bkg.mirroring}\t{bkg.rate}\t{bkg.factor}\t{bkg.zValue()}')
                                                                       
    def notScrollable(self):
        MsgBox('Not Scrollable and Unable to Fulfill your Request...', 6) 
        self.bkgItem.scrollable = False  
        return  
            
### ------------------ dotsBkgScrollWrks -------------------                                                                                                     
             
             




