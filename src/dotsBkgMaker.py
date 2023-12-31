
import os 
import os.path
       
from PyQt6.QtCore       import Qt, QPoint, QPointF, QRect
from PyQt6.QtGui        import QColor, QCursor
from PyQt6.QtWidgets    import QWidget, QFileDialog, QGraphicsPixmapItem, \
                                QColorDialog

from dotsSideGig        import MsgBox
from dotsShared         import common, paths, PlayKeys
from dotsBkgWidget      import BkgWidget
from dotsBkgItem        import BkgItem
from dotsScreens        import *
from dotsBkgMatte       import Flat

### --------------------- dotsBkgMaker ---------------------
''' class: BkgMaker - creates and supports BkgItem '''       
### --------------------------------------------------------
class BkgMaker(QWidget):  
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
        
        self.canvas = parent
        self.dots   = self.canvas.dots
        self.scene  = self.canvas.scene
        self.view   = self.canvas.view  
        self.mapper = self.canvas.mapper
   
        self.widget  = None
        self.bkgItem = None 
        self.matte   = None 

        self.factor    = 1.0  ## sets the factor and mirroring defaults in bkgItem
        self.mirroring = False  
        self.trackers  = []  ## tracks backgrounds and holds state of direction, mirroring  
        
### --------------------------------------------------------
    def openBkgFiles(self):  ## opens both background and flats
        if self.canvas.control in PlayKeys:
            return
        Q = QFileDialog()
        Q.Option.DontUseNativeDialog
        file, _ = Q.getOpenFileName(self.canvas,
            'Choose an image file to open', paths['bkgPath'],
            'Images Files(*.bmp *.jpg *.png *.bkg)')
        if file:  ## it's either a flat or an jpg/png
            self.openFlatFile(file) if file.endswith('.bkg') else self.addBkg(file)
        Q.accept()
          
### --------------------------------------------------------              
    def addBkg(self, file, flopped=False):  ## background from jpg/png
        if self.canvas.pathMakerOn == False:
            if self.mapper.isMapSet():
                self.mapper.removeMap()
                                
        self.bkgItem = BkgItem(file, self.canvas)
        self.bkgItem.setZValue(common['bkgZ'])  ## always on top
                 
        self.scene.addItem(self.bkgItem)      
        self.updateZvals(self.bkgItem)  ## update other bkg zvalues
        self.x, self.y = self.setXY(self.bkgItem)
            
        self.bkgItem.bkgWorks.addTracker(self.bkgItem)  ## always - even if not a scroller 
        self.lockBkg()
                   
        if self.canvas.pathMakerOn:
            self.bkgItem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False) 
                             
### --------------------------------------------------------
    def openFlatFile(self, file):  ## read from .bkg file - a 'flat'
        try:
            with open(file, 'r') as fp:
                self.setBkgColor(QColor(fp.readline()))
        except IOError:
            MsgBox('openFlatFile: Error reading file', 5)
            return

    def bkgColor(self):  ## from button or widget   
        if self.canvas.control in PlayKeys:  ## running animation
            return
        self.setBkgColor(QColorDialog.getColor())

    def setBkgColor(self, color, bkz=common['bkgZ']):  ## add a flat color to canvas
        if color.isValid():
            self.bkgItem = Flat(color, self.canvas, bkz)    
            self.scene.addItem(self.bkgItem)
            self.updateZvals(self.bkgItem)

    def saveFlat(self):  ## saves a color 'flat' file
        if self.bkgItem != None and self.bkgItem.type == 'flat':
            self.saveBkgColor()  
            return  

    def saveBkgColor(self):  ## write to .bkg file
        Q = QFileDialog()
        Q.Option.DontUseNativeDialog
        Q.setDirectory(paths['bkgPath'])
        f = Q.getSaveFileName(self.canvas, paths['bkgPath'],  
            paths['bkgPath'] + 'tmp.bkg')  
        Q.accept()       
        if not f[0]: 
            return
        if not f[0].lower().endswith('.bkg'):
            MsgBox("Save Background Color: Wrong file extention - use '.bkg'", 5)  
            return
        else:
            try:
                with open(f[0], 'w') as fp:
                    fp.write(self.bkgItem.color.name())
            except IOError:
                MsgBox('saveBkgColor: Error saving file', 5)
            self.bkgItem = None
                                                                            
### -------------------------------------------------------- 
    def addWidget(self, item):  ## background widget
        self.closeWidget()       
        if item.type == 'flat':
            return  
            
        self.bkgItem = item             
        self.widget = BkgWidget(self.bkgItem, self) 
        self.lockBkg(item)
        
        p = common['widgetXY']
        p = self.canvas.mapToGlobal(QPoint(p[0], p[1]))       
        self.widget.save = QPointF(p.x(), p.y())
        self.widget.setGeometry(p.x(), p.y(), int(self.widget.WidgetW), \
            int(self.widget.WidgetH))
        
        self.bkgItem.bkgWorks.restoreFromTrackers(self.bkgItem)
        self.resetSliders()
        self.updateWidget()
                                     
    def closeWidget(self):
        if self.widget != None:
            self.widget.close()
            self.widget = None

    def updateWidget(self):
        self.setMirrorBtnText()
        self.setBtns()
        self.setLocksText() 
        
### --------------------------------------------------------
    def resetSliders(self):
        if self.bkgItem != None and self.bkgItem.type == 'bkg':                                
            self.widget.factorDial.setValue(int(self.bkgItem.factor*100))
            self.widget.factorValue.setText('{0:.2f}'.format(self.bkgItem.factor))
            
            self.widget.rateSlider.setValue(int(self.bkgItem.rate*100))
            self.widget.rateValue.setText('{0:.2f}'.format(self.bkgItem.rate))
            
            self.widget.showtimeSlider.setValue(self.bkgItem.showtime)
            self.widget.showtimeValue.setText('{0:3d}'.format(self.bkgItem.showtime))

    def setMirrorBtnText(self):  ## if added 
        if self.bkgItem:  ## shouldn't need this but - could have just started to clear                         
            if self.bkgItem.scrollable == False:
                self.widget.mirrorBtn.setText('Not Scrollable')         
            elif self.bkgItem.mirroring == False:
                self.widget.mirrorBtn.setText('Continuous')         
            elif self.bkgItem.mirroring == True:
                self.widget.mirrorBtn.setText('Mirrored')

    def setBtns(self):
        if self.bkgItem:
            if self.bkgItem.direction == 'right': 
                self.widget.rightBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                self.widget.leftBtn.setStyleSheet(
                    'background-color: None')            
            elif self.bkgItem.direction == 'left': 
                self.widget.leftBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                self.widget.rightBtn.setStyleSheet(
                    'background-color: None')
            elif self.bkgItem.direction == 'vertical':
                self.widget.leftBtn.setText('Vertical')   
                self.widget.leftBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                                                     
    def setLocksText(self):
        if self.bkgItem:  ## shouldn't need this but - could have just started to clear
            if self.bkgItem.locked == False:
                self.widget.lockBtn.setText('UnLocked')
            else:
                self.widget.lockBtn.setText('Locked')
                                      
### --------------------------------------------------------                                           
    def deleteBkg(self, bkg):
        self.scene.removeItem(bkg)
        bkg = None
        if self.widget:
            self.closeWidget()  
        self.canvas.btnAddBkg.setEnabled(True)
                                                     
    def lockBkg(self, bkg=''):
        if bkg != '':
            self.bkgItem = bkg
        if self.bkgItem and self.bkgItem.type == 'bkg':  
            self.bkgItem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            self.bkgItem.locked = True
            if self.widget: self.widget.lockBtn.setText('Locked')
                            
    def unlockBkg(self, bkg=''):
        if bkg != '':
            self.bkgItem = bkg
        if self.bkgItem and self.bkgItem.type == 'bkg':  
            self.bkgItem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
            self.bkgItem.locked = False
            if self.widget: self.widget.lockBtn.setText('UnLocked')
  
### --------------------------------------------------------            
    def showtime(self):  ## 'run' from widget button
        self.closeWidget()
        p = QCursor.pos()
        QCursor.setPos(int(p.x()+220), int(p.y()+650.0))  ## works for 720
        self.canvas.showtime.run()
     
    def flopIt(self):  ## used by widget 
        if self.bkgItem and self.bkgItem.type == 'bkg':  
            self.bkgItem.setMirrored(False) if self.bkgItem.flopped \
                else self.bkgItem.setMirrored(True)
                                                                             
    def front(self, bkg):
        bkg.setZValue(common['bkgZ'])
        self.updateZvals(bkg)
        self.lockBkg()  
        self.closeWidget() 
        
    def back(self, bkg):    
        bkg.setZValue(self.mapper.lastZval('bkg')-1)  
        self.lockBkg()   
        self.closeWidget() 
        
    def backOne(self, bkg):    
        bkg.setZValue(bkg.zValue()-1)
        self.lockBkg()   
        self.closeWidget()
        
    def upOne(self, bkg):    
        bkg.setZValue(bkg.zValue()+1)
        self.lockBkg()   
        self.closeWidget()
                
    def updateZvals(self, bkg):  ## move the rest back one Z and lock them
        for itm in self.scene.items():
            if itm.type == 'bkg' and itm.zValue() <= bkg.zValue():
                if itm != bkg:
                    itm.setZValue(itm.zValue()-1) 
     
    def showZVals(self):
        for itm in self.scene.items(Qt.SortOrder.AscendingOrder):
            if itm.type == 'bkg':
                print(itm.zValue())
                                
    def settingBkgMsg(self):
        if self.bkgItem.type == 'bkg':  
            txt = os.path.basename(self.bkgItem.fileName)
            MsgBox(txt + ' ' +  'set to background', 4) 
     
    def setXY(self, bkg):
        p = bkg.sceneBoundingRect()
        bkg.setPos(p.x() , p.y())
        return p.x() , p.y()     
                    
    def bkgTag(self, bkg, which=''):
        file = os.path.basename(bkg.fileName) 
        if which != '':
            file = which + ': ' + file
        return f'{file}\t{bkg.direction}\t{bkg.rate}\t{bkg.factor}\t{bkg.showtime}'
                             
### --------------------- dotsBkgMaker ---------------------
                                    
                                    
