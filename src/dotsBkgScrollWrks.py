
import os
import json
import random

from PyQt6.QtCore       import Qt, QPoint, QTimer
from PyQt6.QtGui        import QImage, QPixmap, QCursor
from PyQt6.QtWidgets    import QMessageBox, QWidget, QAbstractItemView, \
                                QTableWidget, QPushButton, QVBoxLayout, QTableWidgetItem
                        
from dotsShared         import common, paths
from dotsSideGig        import MsgBox, getVuCtr, tagBkg

showtime = {  ## trigger to add a new background based on number of pixels remaining in runway
    'snakes':   15,  ## also used by vertical 
    'left':     11, 
    'right':    15,  
    'vertical': 17,  ## trying this out 
}

RowHt = 30
### -------------------------------------------------------- 
class Trackers(QWidget): 
### -------------------------------------------------------- 
    def __init__(self, parent, dump): 
        super().__init__() 

        self.canvas = parent
        self.setWindowTitle('trackers') 
        
        self.type = 'widget'
        self.setAccessibleName('widget')

        self.tableWidget = QTableWidget() 
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) 

        self.tableWidget.setColumnCount(len(dump[0]))
        self.tableWidget.setRowCount(len(dump))

        self.width, self.height = 820, (len(dump)+1) * RowHt
        self.tableWidget.setFixedSize(self.width, self.height)

        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
   
        self.tableWidget.setHorizontalHeaderLabels(
            ["filename", "zvalue",  "direction", "mirrored", "rate", "showtime", "screenrate", "directory"]) 
        self.tableWidget.horizontalHeader().setStyleSheet('QHeaderView::section{\n'
            'background-color: rgb(115,225,225)}')	 
            
        self.closeBtn = QPushButton("Use Button to Close")
        self.closeBtn.clicked.connect(self.bye)
        self.closeBtn.setMinimumWidth(200)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.layout.addWidget(self.closeBtn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)
        
        x, y = getVuCtr(self.canvas)
        pos = QPoint(x, int(y - (self.height/2)))
        
        self.move(int(pos.x()-self.width/2), int(pos.y())-50)

        self.createTable(dump)

    def createTable(self, dump): 
        for row, val in enumerate(dump):
            for col, v in enumerate(val):
                item = QTableWidgetItem(v)
                if col in (1,4,5):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  
                self.tableWidget.setItem(row, col, item)
		
    def bye(self):
        if self.tableWidget != None:
            self.tableWidget.close()
            self.tableWidget = None
            self.canvas.sideCar2.tracker = None
            self.close()          
  
### ------------------ dotsBkgScrollWrks -------------------           
class BkgScrollWrks:  ## mainly functions used for scrolling 
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()

        self.bkgItem  = parent    
        self.canvas   = self.bkgItem.canvas 
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
            MsgBox(f'{self.bkgItem.useThis} Updated', 5)
        except:
            MsgBox(f'Error Updating Rates Dictionary {self.bkgItem.useThis}', 5)
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
                self.bkgMaker.newTracker[fileName]['useThis']   = bkg.useThis
                
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

### --------------------------------------------------------             
    def getTrackerRate(self, bkg):  ## used only once - getScreenRate
        if rate := self.bkgMaker.newTracker[bkg.fileName]['rate']:  
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
             
             

