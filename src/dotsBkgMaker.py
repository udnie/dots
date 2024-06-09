
import os 
import os.path
import json
       
from PyQt6.QtCore       import Qt, QPoint, QPointF, QRect
from PyQt6.QtGui        import QColor, QCursor
from PyQt6.QtWidgets    import QWidget, QFileDialog, QGraphicsPixmapItem, \
                                QColorDialog

from dotsSideGig        import MsgBox
from dotsShared         import common, paths, ControlKeys
from dotsBkgWidget      import BkgWidget
from dotsBkgItem        import BkgItem
from dotsScreens        import *
from dotsFrameAndFlats  import Flat

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
           
        self.init()
    
    def init(self):
        self.flat    = None
        self.matte  = None
        self.widget = None  ## there is only one
        
        self.factor = 1.0  ## sets the factor and mirroring defaults in bkgItem
        self.mirroring = False
          
        self.screenrate = {}
        self.newTracker = {}
   
### --------------------------------------------------------
    def openBkgFiles(self):  ## opens both background and flats - needs to be in /backgrounds
        if self.canvas.control in ControlKeys:
            return
        Q = QFileDialog()
        Q.Option.DontUseNativeDialog
        file, _ = Q.getOpenFileName(self.canvas,
            'Choose an image file to open', paths['bkgPath'],
            'Images Files(*.bmp *.jpg *.png *.bkg *.JPG *.PNG)')
        if file:  ## it's either a flat or an jpg/png
            file = paths['bkgPath'] + os.path.basename(file) 
            self.openFlatFile(file) if file.endswith('.bkg') else self.addBkg(file)
        Q.accept()
          
### --------------------------------------------------------              
    def addBkg(self, file, flopped=False):  ## background from jpg/png
        if self.canvas.pathMakerOn == False:
            if self.mapper.isMapSet():
                self.mapper.removeMap()

        bkg = BkgItem(file, self.canvas) 
        if bkg == None:
            return
        
        bkg.setZValue(common['bkgZ'])  ## always on top              
        self.scene.addItem(bkg)    
   
        self.updateZvals(bkg)  ## update other bkg zvalues 
        self.setXY(bkg)
            
        bkg.bkgWorks.addTracker(bkg)  ## always - even if not a scroller   
        self.lockBkg(bkg)
                        
        if self.canvas.pathMakerOn:
            bkg.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False) 
                               
### --------------------------------------------------------
    def openFlatFile(self, file):  ## read from .bkg file - a 'flat'
        try:
            with open(file, 'r') as fp:
                self.setBkgColor(QColor(fp.readline()))
        except IOError:
            MsgBox('openFlatFile: Error reading file', 5)
            return

    def bkgColor(self):  ## from button or widget   
        if self.canvas.control in ControlKeys:  ## running animation
            return
        self.setBkgColor(QColorDialog.getColor())

    def setBkgColor(self, color, bkz=common['bkgZ']):  ## add a flat color to canvas
        if color.isValid():
            self.flat = Flat(color, self, bkz) 
            self.scene.addItem(self.flat)
            self.updateZvals(self.flat)

    def saveFlat(self):  ## saves a color 'flat' file - from bkg save button
        if self.flat != None and self.flat.type == 'flat':
            if self.flat.zValue() == self.mapper.toFront():  ## top most screen item   
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
                    fp.write(self.flat.color.name())
            except IOError:
                MsgBox('saveBkgColor: Error saving file', 5)
            self.flat = None
                                                                            
### -------------------------------------------------------- 
    def addWidget(self, bkg):  ## background widget
        self.closeWidget()      
        if bkg.type == 'flat':
            return           
        self.widget = BkgWidget(bkg, self) 
        self.lockBkg(bkg)
        p = common['widgetXY']
        p = self.canvas.mapToGlobal(QPoint(p[0], p[1]))       
        self.widget.save = QPointF(p.x(), p.y())
        self.widget.setGeometry(p.x(), p.y(), int(self.widget.WidgetW), \
            int(self.widget.WidgetH))
        bkg.bkgWorks.restoreFromTrackers(bkg)
        self.resetSliders(bkg)
        self.updateWidget(bkg)
                                     
    def closeWidget(self):
        if self.widget != None:
            self.widget.close()
            self.widget = None
            self.view.grabKeyboard()

    def updateWidget(self, bkg):
        self.setMirrorBtnText(bkg)
        self.setBtns(bkg)
        self.setLocksText(bkg) 
        
### --------------------------------------------------------
    def resetSliders(self, bkg):
        if bkg != None and bkg.type == 'bkg':                                
            self.widget.factorDial.setValue(int(bkg.factor*100))
            self.widget.factorValue.setText(f'{bkg.factor:.2f}')
            
            self.widget.rateSlider.setValue(int(bkg.rate*100))
            self.widget.rateValue.setText(f'{bkg.rate:.2f}')
            
            self.widget.showtimeSlider.setValue(bkg.showtime)
            self.widget.showtimeValue.setText(f'{bkg.showtime:3}')

    def setMirrorBtnText(self, bkg):  ## if added 
        if bkg:  ## shouldn't need this but - could have just started to clear        
            if self.dots.Vertical == False and bkg.imgFile.width() >= bkg.showtime + bkg.ViewW or \
                self.dots.Vertical == True and bkg.imgFile.height() >= bkg.showtime + bkg.ViewH:  
                bkg.scrollable = True     
                                          
            if bkg.scrollable == False:
                self.widget.mirrorBtn.setText('Not Scrollable')  
                bkg.direction = ''
                       
            if bkg.mirroring == False:
                self.widget.mirrorBtn.setText('Continuous')         
            elif bkg.mirroring == True:
                self.widget.mirrorBtn.setText('Mirrored')

    def setBtns(self, bkg):
        if bkg:
            if bkg.direction == 'right': 
                self.widget.rightBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                self.widget.leftBtn.setStyleSheet(
                    'background-color: None')            
            elif bkg.direction == 'left': 
                self.widget.leftBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                self.widget.rightBtn.setStyleSheet(
                    'background-color: None')
            elif bkg.direction == 'vertical':
                self.widget.leftBtn.setText('Vertical')   
                self.widget.leftBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                                                     
    def setLocksText(self, bkg):
        if bkg == None:
            return
        self.widget.lockBtn.setText('UnLocked') if bkg.locked == False \
            else self.widget.lockBtn.setText('Locked')         
                                     
### --------------------------------------------------------                                           
    def deleteBkg(self, bkg, where=''):  ## delete tracker as well               
        if where == '' and bkg.type == 'bkg':
            bkg.bkgWorks.delTracker(bkg)
        if self.widget:
            self.closeWidget() 
        self.scene.removeItem(bkg)
        bkg = None
        self.canvas.btnAddBkg.setEnabled(True)
                                                     
    def lockBkg(self, bkg):
        if bkg and bkg.type == 'bkg':  
            bkg.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            bkg.locked = True
            if self.widget: self.widget.lockBtn.setText('Locked')
                            
    def unlockBkg(self, bkg):
        if bkg and bkg.type == 'bkg':  
            bkg.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
            bkg.locked = False
            if self.widget: self.widget.lockBtn.setText('UnLocked')
  
### --------------------------------------------------------            
    def showtime(self, bkg):  ## 'run' from widget button
        if bkg.useThis == '':
            return  
        self.closeWidget()
        p = QCursor.pos()
        QCursor.setPos(int(p.x()+220), int(p.y()+650.0))  ## works for 720
        self.canvas.showtime.run()
     
    def flopIt(self, bkg):  ## used by widget 
        if bkg and bkg.type == 'bkg':  
            bkg.setMirrored(False) if bkg.flopped \
                else bkg.setMirrored(True)
                                                                             
    def front(self, bkg):
        bkg.setZValue(common['bkgZ'])
        self.updateZvals(bkg)
        self.lockBkg(bkg) 
        self.closeWidget()
        
    def back(self, bkg): 
        bkg.setZValue(self.mapper.lastZval('flat')-1) if bkg.type == 'flat' \
            else bkg.setZValue(self.mapper.lastZval('bkg')-1)  
        self.lockBkg(bkg)   
        self.closeWidget()
        
    def backOne(self, bkg):    
        bkg.setZValue(bkg.zValue()-1)
        self.lockBkg(bkg)   
        self.closeWidget()
        
    def upOne(self, bkg):    
        bkg.setZValue(bkg.zValue()+1)
        self.lockBkg(bkg)   
        self.closeWidget()
                
    def updateZvals(self, bkg):  ## move the rest back one Z and lock them
        for itm in self.scene.items():
            if itm.type == 'bkg' and itm.zValue() <= bkg.zValue():
                if itm != bkg:
                    itm.setZValue(itm.zValue()-1) 
     
    def showZVals(self):
        for itm in self.scene.items(Qt.SortOrder.AscendingOrder):
            if itm.type == 'bkg':
                print(itm.zValue())  ## show zvals
                                
    def setXY(self, bkg):
        p = bkg.sceneBoundingRect()
        bkg.setPos(p.x() , p.y())
        self.x, self.y = p.x() , p.y()     
                                                 
### --------------------- dotsBkgMaker ---------------------

    # def bkgTag(self, bkg, which=''):
    #     file = bkg.fileName
    #     if which != '':
    #         file = which + ': ' + file
    #     return f'{file}\t{bkg.direction}\t{bkg.rate}\t{bkg.factor}\t{bkg.showtime}'
                                    
                                    
                                    
                                    
