
import os 
import os.path

from functools          import partial
       
from PyQt6.QtCore       import Qt, QPoint, QPointF, QTimer, QRect
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

        self.mirroring = False  ## set in bkgItem
        self.directions = []  ## tracks backgrounds and holds state of direction, mirroring  
            
### --------------------------------------------------------
    def openBkgFiles(self):
        if self.canvas.control in PlayKeys:
            return
        Q = QFileDialog()
        Q.Option.DontUseNativeDialog
        file, _ = Q.getOpenFileName(self.canvas,
            'Choose an image file to open', paths['bkgPath'],
            'Images Files(*.bmp *.jpg *.png *.bkg)')
        if file:  ## it's a 'flat'
            self.openBkgFile(file) if file.endswith('.bkg') else self.addBkg(file)
        Q.accept()
        
    def openBkgFile(self, file):  ## read from .bkg file - a 'flat'
        try:
            with open(file, 'r') as fp:
                self.setBkgColor(QColor(fp.readline()))
        except IOError:
            MsgBox('openBkgFile: Error reading file', 5)
            return
  
### --------------------------------------------------------              
    def addBkg(self, file, flopped=False):  ## also used by saveBkg 
        if self.canvas.pathMakerOn == False:
            if self.mapper.isMapSet():
                self.mapper.removeMap()
                                
        self.bkgItem = BkgItem(file, self.canvas)
        self.bkgItem.setZValue(common['bkgZ'])  ## always on top
                 
        self.scene.addItem(self.bkgItem)      
        self.updateZvals(self.bkgItem)  ## update other bkg zvalues
        self.x, self.y = self.setXY(self.bkgItem)

        self.canvas.btnAddBkg.setEnabled(False)
        self.enableBkgBtns(True)  ## hasn't been set 
            
        self.bkgItem.bkgWorks.addTracker(self.bkgItem)  ## always - even if not a scroller
        
        if self.canvas.pathMakerOn:
            self.bkgItem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            
        if self.widget: QTimer.singleShot(0, partial(self.widget.resetSliders, self.bkgItem))

    def saveBkg(self):  ## saves a color 'flat' file
        if self.bkgItem != None and self.bkgItem.fileName == 'flat':
            self.saveBkgColor()  
            return  
 
### --------------------------------------------------------
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
                                                                       
    def bkgColor(self):  ## from button or widget   
        if self.canvas.control in PlayKeys:
            return
        self.setBkgColor(QColorDialog.getColor())

    def setBkgColor(self, color, bkz=common['bkgZ']):  ## add a flat color to canvas
        if color.isValid():
            self.bkgItem = Flat(color, self.canvas, bkz)    
            self.scene.addItem(self.bkgItem)
            self.updateZvals(self.bkgItem)
    
    def delScroller(self, bkg):
        self.scene.removeItem(bkg)
        del bkg
 
### -------------------------------------------------------- 
    def addWidget(self, item):  ## background widget
        self.closeWidget()       
        if item.fileName == 'flat':
            return      
        self.bkgItem = item            
        self.lockBkg() if self.bkgItem.locked else self.unlockBkg()         
        self.widget = BkgWidget(self.bkgItem, self) 
        p = common['widgetXY']
        p = self.canvas.mapToGlobal(QPoint(p[0], p[1]))       
        self.widget.save = QPointF(p.x(), p.y())
        self.bkgItem.bkgWorks.restoreDirections(self.bkgItem, 'wid')
        self.widget.setGeometry(p.x(), p.y(), int(self.widget.WidgetW), \
            int(self.widget.WidgetH))
        self.widget.resetSliders(self.bkgItem)
        self.dots.statusBar.showMessage(os.path.basename(self.bkgItem.fileName))
                                     
    def closeWidget(self):
        if self.widget != None:
            self.widget.close()
            self.widget = None
                                       
    def setBkg(self):  ## from widget or button   
        if self.bkgItem != None:       
            self.lockBkg()
            self.disableSetBkg()  ## turn off setting it again 
            return
        else:
            MsgBox('Already set to background', 5)
            
    def deleteBkg(self, bkg):
        self.scene.removeItem(bkg)
        self.bkgItem = None
        self.closeWidget()  
        self.disableBkgBtns()
        self.canvas.btnAddBkg.setEnabled(True)
                     
### --------------------------------------------------------     
    def setXY(self, bkg):
        p = bkg.sceneBoundingRect()
        bkg.setPos(p.x() , p.y())
        return p.x() , p.y()
                                      
    def toggleBkgLocks(self, bkg, str=''):
        self.bkgItem = bkg
        if str == '':
            if self.bkgItem.locked == False:
                self.lockBkg()
            else:
                self.unlockBkg()
        elif str == 'unlock':
            self.unlockBkg()
                                                                                  
    def lockBkg(self, bkg=''):
        if bkg != '':
            self.bkgItem = bkg
        if self.bkgItem and self.bkgItem.fileName != 'flat':
            self.bkgItem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            self.bkgItem.locked = True
            if self.widget: self.widget.lockBtn.setText('Locked')
                              
    def unlockBkg(self):
        if self.bkgItem and self.bkgItem.fileName != 'flat':
            self.bkgItem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
            self.bkgItem.locked = False
            if self.widget: self.widget.lockBtn.setText('UnLocked')
       
    def showtime(self):
        self.closeWidget()
        p = QCursor.pos()
        QCursor.setPos(int(p.x()+220), int(p.y()+650.0))  ## works for 720
        self.canvas.showtime.run()
     
    def flopIt(self):  ## used by widget 
        if self.bkgItem and self.bkgItem.fileName != 'flat':
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
        self.disableSetBkg()
    
    def showZVals(self):
        for itm in self.scene.items(Qt.SortOrder.AscendingOrder):
            if itm.type == 'bkg':
                print(itm.zValue())
                                
    def settingBkgMsg(self):
        if self.bkgItem.fileName != 'flat':
            txt = os.path.basename(self.bkgItem.fileName)
            MsgBox(txt + ' ' +  'set to background', 4) 
            
### ------------------- background buttons -----------------
    def enableBkgBtns(self, bool):
        if not self.dots.Vertical:  ## check vertical
            pass
            # self.canvas.btnSetBkg.setEnabled(bool)
            # self.canvas.btnSaveBkg.setEnabled(bool)

    def disableBkgBtns(self):
        if not self.dots.Vertical:
            self.enableBkgBtns(False)

    def disableSetBkg(self):
        if not self.dots.Vertical:
            self.canvas.btnAddBkg.setEnabled(True)  ## in docks
       
### --------------------- dotsBkgMaker ---------------------
                                    
                                    
