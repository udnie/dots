
import os
import json

from PyQt6.QtCore       import pyqtSlot,QPointF
from PyQt6.QtGui        import QColor, QImage, QPixmap
from PyQt6.QtWidgets    import QGraphicsSimpleTextItem, QMessageBox, QGraphicsPixmapItem
                        
from dotsShared         import common, paths
from dotsSideGig        import MsgBox

showtime = {  ## trigger to add a new background based on number of pixels remaining in runway
    'snakes':   15,  ## also used by vertical 
    'left':     11, 
    'right':    15,  
    'vertical': 17,  ## trying this out 
}

### ------------------ dotsBkgScrollWrks ------------------- 
''' classes: Tracker, Flat, ScrollWrks (functions used for scrolling support) '''    
### -------------------------------------------------------- 
class Flat(QGraphicsPixmapItem):
### -------------------------------------------------------- 
    def __init__(self, color, parent, z=common['bkgZ']):
        super().__init__()

        self.bkgMaker = parent
        self.canvas   = self.bkgMaker.canvas 
        self.scene    = self.bkgMaker.scene
            
        self.fileName = 'flat'
        self.type    = 'flat'
        
        self.color = QColor(color)
        self.tag =  QColor(color)
      
        self.locked = True
        self.setZValue(z)
        
        self.id = 0   
        self.key = ''
        self.x, self.y = 0, 0

        p = QPixmap(common['ViewW'],common['ViewH'])
        p.fill(self.color)
        
        self.setPixmap(p)      
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        
### --------------------------------------------------------
    @pyqtSlot(str)  ## updated by storyboard
    def setPixKeys(self, key):
        self.key = key  

    def mousePressEvent(self, e):      
        if not self.canvas.pathMakerOn:     
            if self.key == 'del':     
                self.delete()
            elif self.key == '/':  ## to back
                self.bkgMaker.back(self)
            elif self.key in ('enter','return'):  
                self.setZValue(self.canvas.mapper.toFront())                       
        e.accept()
      
    def mouseReleaseEvent(self, e):
        if not self.canvas.pathMakerOn:
            self.key = ''       
        e.accept()
     
    def delete(self):  ## also called by widget
        self.bkgMaker.deleteBkg(self)
             
### --------------------------------------------------------  
class BkgScrollWrks:  ## mainly functions used for scrolling 
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()

        self.bkgItem  = parent     
        self.bkgMaker = self.bkgItem.bkgMaker
        self.dots     = self.bkgItem.dots
                                         
### -------------------------------------------------------- 
    def updateDictionary(self):
        if self.bkgItem.useThis == '':
            return  
        test = False
        rate = self.bkgMaker.screenrate[self.bkgItem.useThis][common['Screen']]  
         
        if self.bkgItem.direction == 'right' and rate[2] != self.bkgItem.rate:
            rate[2] = self.bkgItem.rate
            test = True
        elif self.bkgItem.direction == 'left' and rate[1] != self.bkgItem.rate:
            rate[1] = self.bkgItem.rate
            test = True 
              
        if test == False:
            MsgBox("Screen Rates Haven't Changed", 5)
            return   
    
        img = QImage(paths['spritePath'] + "doral.png")
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
            MsgBox(f'{self.bkgItem.useThis} Updated', 5)
        except:
            MsgBox(f'Error Updating Rates Dictionary {self.bkgItem.useThis}', 5)
        return 
     
### --------------------------------------------------------
    ## snakes need more time - the rest vary to build and position and comes before vertical  
    def setShowTime(self): 
        fileName = os.path.basename(self.bkgItem.fileName)  
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

    def setShowTimeTrackers(self):  ## used by resetSliders
        if self.bkgItem.scrollable:                                                               
            fileName = os.path.basename(self.bkgItem.fileName)    
            if self.bkgMaker.newTracker[fileName]:        
                self.bkgMaker.newTracker[fileName]['direction'] = self.bkgItem.direction 
                self.bkgMaker.newTracker[fileName]['showtime']  = self.bkgItem.showtime 
                             
### --------------------------------------------------------   
    def setTrackerFactor(self):
        if self.bkgItem.scrollable:                                                                 
            fileName = os.path.basename(self.bkgItem.fileName)  
            if self.bkgMaker.newTracker[fileName]:  
                self.bkgMaker.newTracker[fileName]['factor'] = self.bkgItem.factor          

    def setTrackerRate(self):
        if self.bkgItem.scrollable:                                                               
            fileName = os.path.basename(self.bkgItem.fileName)  
            if self.bkgMaker.newTracker[fileName]:
                self.bkgMaker.newTracker[fileName]['direction'] = self.bkgItem.direction
                self.bkgMaker.newTracker[fileName]['rate']      = self.bkgItem.rate 
                self.bkgMaker.newTracker[fileName]['useThis']   = self.bkgItem.useThis
                
    def getTrackerRate(self, bkg):  ## used only once - getScreenRate
        fileName = os.path.basename(bkg.fileName) 
        if rate := self.bkgMaker.newTracker[fileName]['rate']:  
            return rate
        return 0  
           
### --------------------------------------------------------    
    def setRunWay(self):      
        if not self.dots.Vertical:             
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
           
### --------------------------------------------------------
    def toggleBkgLocks(self):
        if self.bkgItem:
            if self.bkgItem.locked == False:
                self.bkgMaker.lockBkg(self.bkgItem) 
            else:
                self.bkgMaker.unlockBkg(self.bkgItem) 
                                                                                  
    def tagBkg(self, bkg, pos):
        self.bkgItem = bkg
        x, y = pos.x(), pos.y()
        z = self.bkgItem.zValue()
        text = QGraphicsSimpleTextItem() 
        if self.bkgItem.locked == True:
            text = 'Locked' 
        else:
            text = 'Unlocked'
        fileName = os.path.basename(bkg.fileName)
        tag = fileName + " " + text    
        if self.bkgItem.direction == ' left':
            tag = tag + ' Left'
        elif self.bkgItem.direction == 'right': 
            tag = tag + ' Right'            
        self.bkgItem.canvas.mapper.tagsAndPaths.TagItTwo('bkg', tag,  QColor('orange'), x, y, z, 'bkg')
             
    def filePixX(self, file, bkg):  ## also see dumpBkgs - shift 'B'
        fileName = os.path.basename(bkg.fileName)
        print(f'tracker {fileName}\t{bkg.direction}\t{bkg.mirroring}\t{bkg.rate}\t{bkg.factor}\t{bkg.zValue()}')
                                                                       
    def notScrollable(self):
        MsgBox('Not Scrollable and Unable to Fulfill your Request...', 6) 
        self.bkgItem.scrollable = False  
        return  
 
### --------------------------------------------------------
def addNewTracker(bkg):
    tmp = {
        "fileName":    os.path.basename(bkg.fileName),
        "direction":  bkg.direction,
        "mirroring":  bkg.mirroring,
        "factor":     bkg.factor,
        "rate":       bkg.rate,
        "showtime":   bkg.showtime,
        "useThis":    bkg.useThis,
        "path":       bkg.path,
        "scrollable": bkg.scrollable,
    }
    return tmp
 
### ------------------ dotsBkgScrollWrks -------------------                                                                                                     
             
             

