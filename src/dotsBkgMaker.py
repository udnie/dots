
import os 
import os.path
import gc

from functools          import partial
       
from PyQt6.QtCore       import Qt, QPoint, QRect, QTimer, QSize
from PyQt6.QtGui        import QColor
from PyQt6.QtWidgets    import QWidget, QFileDialog, QGraphicsPixmapItem, \
                                QColorDialog

from dotsSideGig        import MsgBox, getCtr
from dotsShared         import common, paths, PlayKeys
from dotsBkgWidget      import BkgWidget, Flat
from dotsBkgItem        import BkgItem
from dotsScreens        import *

### --------------------- dotsBkgMaker ---------------------              
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
       
        self.widgetX = 400  ## position widget
        self.widgetY = 300 
        
        self.last = ''
        self.key = ''
        self.num  = 0
                
        self.save = QPoint(self.widgetX, self.widgetY)
        
### --------------------------------------------------------
    def openBkgFiles(self):
        if self.canvas.control in PlayKeys:
            return
        Q = QFileDialog()
        Q.Option.DontUseNativeDialog
        file, _ = Q.getOpenFileName(self.canvas,
            'Choose an image file to open', paths['bkgPath'],
            'Images Files(*.bmp *.jpg *.png *.bkg)')
        if file:
            self.openBkgFile(file) if file.endswith('.bkg') else self.addBkg(file)
        Q.accept()
        
    def openBkgFile(self, file):  ## read from .bkg file
        try:
            with open(file, 'r') as fp:
                self.setBkgColor(QColor(fp.readline()))
        except IOError:
            MsgBox('openBkgFile: Error reading file', 5)
  
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
        
        ## take care of a file previously saved
        if file.endswith('-bkg.jpg'):
            self.bkgItem.setScale(1.003)  ## for white space???
            self.bkgItem.setOrigin()
            self.lockBkg() ## set and forget
            self.settingBkgMsg()
            self.disableSetBkg()  ## turn off button to set it again 
        else:
            self.canvas.btnAddBkg.setEnabled(False)
            self.enableBkgBtns(True)  ## hasn't been set 
 
        if self.widget: QTimer.singleShot(0, partial(self.widget.resetSliders, self.bkgItem))

    def saveBkg(self):  ## save it to the background file
        if self.bkgItem.fileName == 'flat':
            self.saveBkgColor()  
            return  
        elif not self.bkgItem.locked:
            MsgBox('Set/Lock Background inorder to save', 3)
            return
        else:
            file = os.path.basename(self.bkgItem.fileName)
            file = file[0: file.index('.')]
            file = file[:15] + '-bkg.jpg'       
            ## if it's not already a bkg file and the new file doesn't exist
            if not self.bkgItem.fileName.lower().endswith('-bkg.jpg') and not \
                os.path.exists(paths['bkgPath']+ file):
                self.bkgItem.fileName = paths['bkgPath'] + file
                flopped = self.bkgItem.flopped
                pix = self.canvas.view.grab(QRect(QPoint(1,1), QSize()))
                pix.save(paths['bkgPath'] + file, format='jpg',
                    quality=100)
                MsgBox('Saved as ' + file, 3)
                self.canvas.clear()  ## replace current background with '-bkg.jpg' copy   
                self.addBkg(self.bkgItem.fileName, flopped)
            else:
                MsgBox('Already saved as background jpg', 5)
        self.canvas.btnAddBkg.setEnabled(True)
        self.disableBkgBtns()
 
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
                MsgBox('savePlay: Error saving file', 5)
                                                                       
    def bkgColor(self):  ## from button or widget   
        if self.canvas.control in PlayKeys:
            return
        self.setBkgColor(QColorDialog.getColor())

    def setBkgColor(self, color, bkz=common['bkgZ']):  ## add a flat color to canvas
        if color.isValid():
            self.bkgItem = Flat(color, self.canvas, bkz)    
            self.scene.addItem(self.bkgItem)
            self.updateZvals(self.bkgItem)

### --------------------------------------------------------     
    def delScroller(self, pix):
        self.scene.removeItem(pix)
        del pix
        self.num += 1
        if self.num % 3 == 0: gc
        
    def delSnakes(self):
        if len(self.canvas.scene.items()) > 0:
            for pix in self.canvas.scene.items():      
                if pix.type == 'snake':
                    self.canvas.scene.removeItem(pix)
                    del pix
                                               
### -------------------------------------------------------- 
    def addWidget(self, item):  ## background widget
        self.closeWidget()      
        self.bkgItem = item        
        self.lockBkg() if self.bkgItem.locked else self.unlockBkg()         
        self.widget  = BkgWidget(self.bkgItem, self)
        b = common['bkgrnd']
        p = getCtr(int(b[0]), int(b[1]))
        self.widgetX = int(p.x())  ## set to last position
        self.widgetY = int(p.y())        
        self.widget.setGeometry(self.widgetX, self.widgetY, int(self.widget.WidgetW), \
            int(self.widget.WidgetH)) 
                                
    def closeWidget(self):
        if self.widget and self.widget != None:
            self.save = self.widget.pos()
            self.widget.close()
            self.widget = None
                                       
    def setBkg(self):  ## from widget or button   
        if self.bkgItem:          
            self.lockBkg()
            self.settingBkgMsg()
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
                                                     
    def lockBkg(self):
        if self.bkgItem and self.bkgItem.fileName != 'flat':
            self.bkgItem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            self.bkgItem.locked = True
            if self.widget: self.widget.lockBtn.setText('Locked')
                              
    def unlockBkg(self):
        if self.bkgItem and self.bkgItem.fileName != 'flat':
            self.bkgItem.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
            self.bkgItem.locked = False
            if self.widget: self.widget.lockBtn.setText('UnLocked')
        
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
                
    def updateZvals(self, bkg):  ## move the rest back one Z and lock them
        for itm in self.scene.items():
            if itm.type == 'bkg' and itm.zValue() <= bkg.zValue():
                if itm != bkg:
                    itm.setZValue(itm.zValue()-1) 
                    # self.lockBkg(itm)  ## setting a color locks all bkg's - just to be sure
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
        if not self.dots.Vertical:
            self.canvas.btnSetBkg.setEnabled(bool)
            self.canvas.btnSaveBkg.setEnabled(bool)

    def disableBkgBtns(self):
        if not self.dots.Vertical:
            self.enableBkgBtns(False)

    def disableSetBkg(self):
        if not self.dots.Vertical:
            self.canvas.btnAddBkg.setEnabled(True)
            self.canvas.btnSetBkg.setEnabled(False)
            self.canvas.btnSaveBkg.setEnabled(True)
        
### --------------------- dotsBkgMaker ---------------------
                                    
                                    