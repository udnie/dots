import os
import sys
import random

import os.path
from os import path

from PyQt5.QtCore    import Qt, QEvent, QPointF, QPoint, pyqtSlot, QSize, QRect
from PyQt5.QtGui     import QColor, QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QFileDialog, QColorDialog, QGraphicsItem, \
                            QGraphicsPixmapItem

from dotsSideGig     import MsgBox
from dotsShared      import common, paths

import dotsSideCar as sideCar

### ---------------------- dotsBkgItem ---------------------
''' dotsBkgItem: handles adding, setting, copying and saving background 
    items.  Includes BkgItem, Flat and InitBkg classes. '''
### --------------------------------------------------------
class BkgItem(QGraphicsPixmapItem):

    def __init__(self, imgFile, canvas, zval=0):
        super().__init__()

        self.canvas  = canvas
        self.scene   = canvas.scene

        self.mapper  = self.canvas.mapper
        self.dots    = canvas.dots
        self.initBkg = canvas.initBkg
 
        self.ViewW = common["ViewW"]
        self.ViewH = common["ViewH"]

        self.fileName = imgFile
        img = QImage(imgFile)

        self.imgFile = img.scaled(  ## fill to width or height
            self.ViewW, 
            self.ViewH,
            Qt.KeepAspectRatio|
            Qt.SmoothTransformation)

        self.key = ""

        self.type = 'bkg'
        self.flopped = False

        self.rotation = 0
        self.scale = 1.0

        self.setZValue(zval)
        self.tag = ''
        self.isBackgroundSet = False

        self.width = self.imgFile.width()
        self.height = self.imgFile.height()

        self.x = (self.ViewW - self.width)/2
        self.y = (self.ViewH - self.height)/2

        self.setPos(self.x, self.y)
        self.setMirrored(False)

        self.setPixmap(QPixmap.fromImage(self.imgFile))
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)

### --------------------------------------------------------
    def mousePressEvent(self, e):
        if self.canvas.key == 'del':       # delete it
            self.scene.removeItem(self)
            self.initBkg.disableBkgBtns()
            self.dots.btnAddBkg.setEnabled(True)
        elif self.canvas.key == '/':    # send to back
            ## lastZval uses the string to return the last zvalue
            self.setZValue(self.mapper.lastZval('bkg')-1)
            return
        elif self.canvas.key == 'shift':
            self.flopped = not self.flopped 
            self.setMirrored(self.flopped)
        e.accept()

    def setMirrored(self, mirror):
        sideCar.mirrorSet(self, mirror)

    def centerBkg(self):
        self.updateWidthHeight()
        op = QPointF(self.width/2, self.height/2)
        self.setTransformOriginPoint(op)

    def setBkgRotate(self, value):
        self.centerBkg()
        if value < 0:
            value = 0
        self.rotation = value
        self.setRotation(self.rotation)

    def setBkgScale(self, value):
        self.centerBkg()
        self.scale = value
        self.setScale(self.scale)

    def setBkgOpacity(self, value):
        self.centerBkg()
        self.opacity = value
        self.setOpacity(self.opacity)

    def updateWidthHeight(self):
        self.mapper.updateWidthHeight(self)

### --------------------------------------------------------
class Flat(QGraphicsPixmapItem):
    
    def __init__(self, color, canvas, zval=0):
        super().__init__()

        self.canvas = canvas
        self.scene  = canvas.scene

        self.dots   = canvas.dots
        self.mapper = self.canvas.mapper
        self.initBkg = canvas.initBkg
        
        self.type = 'bkg'
        self.color = color
        self.fileName = 'flat'
        self.key = ""

        self.setZValue(zval)

        p = QPixmap(common["ViewW"],common["ViewH"])
        p.fill(self.color)
        self.setPixmap(p)

        self.isBackgroundSet = False      
        self.setFlag(QGraphicsItem.ItemIsMovable, False)

### --------------------------------------------------------
    def mousePressEvent(self, e):
        if self.canvas.key == 'del':     
            self.scene.removeItem(self)
            self.initBkg.disableBkgBtns()
            self.dots.btnAddBkg.setEnabled(True)
        elif self.canvas.key == '/':   
            self.setZValue(self.mapper.lastZval('bkg')-1)
            return
        e.accept()
     
### --------------------------------------------------------
class InitBkg(QWidget):

    def __init__(self, parent):
        super().__init__()

        self.canvas = parent
        self.scene  = parent.scene
        self.dots   = parent.dots
     
        self.mapper   = self.canvas.mapper
        self.sideShow = self.canvas.sideShow
        self.sliders  = self.dots.sliderpanel

        self.sliders.sliderSignal[str, int].connect(self.mapKeys)

### --------------------------------------------------------
    @pyqtSlot(str, int)
    def mapKeys(self, key, val):
        self.key = key
        if key == 'rotate':
            self.bkg.setBkgRotate(val)
        elif key == 'scale':
            self.bkg.setBkgScale(val/100.0)
        elif key == 'opacity':
            self.bkg.setBkgOpacity(val/100.0)
        elif key == 'lock':
            self.bkg.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
        self.bkg.update()

    def openBkgFiles(self):
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self,
            "Choose an image file to open", paths["bkgPath"],
            "Images Files(*.bmp *.jpg *.png *.bkg)")
        if file:
            if file.endswith('.bkg'):
                self.openBkgFile(file)
            else:
                self.addBkg(file)

    def addBkg(self, file, flopped=False): ## also used by saveBkg
        if self.mapper.mapSet:
            self.mapper.removeMap()
        self.bkg = BkgItem(file, self.canvas)
        self.scene.addItem(self.bkg)
        if file.endswith('-bkg.jpg'):
            self.bkg.setScale(1.003)   ## for white space???
            self.bkg.centerBkg()
            self.lockBkg()
        else:
            self.dots.btnAddBkg.setEnabled(False)
            self.enableBkgBtns(True)
            sideCar.setCursor()

    def saveBkg(self):
        if not self.bkg.isBackgroundSet:
            MsgBox("Set to Background inorder to save", 3)
            return
        if self.bkg.fileName == 'flat':
            self.saveBkgColor()
        else:
            file = os.path.basename(self.bkg.fileName)
            file = file[0: file.index('.')]
            file = file[:15] + "-bkg.jpg"
            ## if it's not already a bkg file and the new file doesn't exist
            if not self.bkg.fileName.lower().endswith("-bkg.jpg") and not \
                path.exists(paths["bkgPath"]+ file):
                self.bkg.fileName = paths["bkgPath"] + file
                flopped = self.bkg.flopped
                pix = self.canvas.view.grab(QRect(QPoint(1,1), QSize()))
                pix.save(paths["bkgPath"] + file,
                    format='jpg',
                    quality=100)
                MsgBox("Saved as " + file, 3)
                self.canvas.clear() ## replace current background with "-bkg.jpg" copy   
                self.addBkg(self.bkg.fileName, flopped)
            else:
                MsgBox("Already saved as background jpg")
        self.dots.btnAddBkg.setEnabled(True)
        self.disableBkgBtns()

    def bkgColor(self):        ## triggered by "/" 
        self.setBkgColor(QColorDialog.getColor())

    def setBkgColor(self, color, val=0): ## add a flat color to canvas
        if color.isValid():
            self.bkg = Flat(color, self.canvas, val)
            self.scene.addItem(self.bkg)
            if val != 0:
                self.bkg.isBackgroundSet = True
                self.disableSetBkg()  ##
            elif self.bkg.isBackgroundSet == False and \
                self.bkg.key != 'lock' and val == 0:
                self.lockBkg()

    def openBkgFile(self, file):   ## read from .bkg file
        try:
            with open(file, 'r') as fp:
                self.setBkgColor(QColor(fp.readline()))
        except IOError:
            MsgBox("openBkgFile: Error reading file")

    def saveBkgColor(self):  ## write to .bkg file
        Q = QFileDialog()
        f = Q.getSaveFileName(self.canvas, paths["bkgPath"],  
            paths["bkgPath"] + 'tmp.bkg')    
        if not f[0]: 
            return
        if not f[0].lower().endswith('.bkg'):
            MsgBox("Save Background Color: Wrong file extention - use '.bkg'")  
            return
        else:
            try:
                with open(f[0], 'w') as fp:
                    fp.write(self.bkg.color.name())
            except IOError:
                MsgBox("savePlay: Error saving file")
                
    def setBkg(self):  
        if self.bkg.isBackgroundSet == False and self.bkg.key != 'lock':
            self.lockBkg()
            return
        else:
            self.disableBkgBtns()
            self.dots.btnAddBkg.setEnabled(True)
            MsgBox("Already set to background")

    def lockBkg(self):
        self.sliders.enableSliders()  ## default is false
        self.mapKeys("lock", 0)   ## 0 is a place holder
        if self.hasBackGround():  ## reset zvals of existing bkgs to by -1
            ## seems to work best in descending order
            for itm in self.scene.items():
                if itm.type == 'bkg' and itm.zValue() <= common['bkgZ']:
                    itm.setZValue(self.canvas.mapper.lastZval('bkg')-1)
        self.settingBkgMsg()

    def settingBkgMsg(self):
        self.bkg.setZValue(common['bkgZ'])   ## the one showing
        self.bkg.isBackgroundSet = True
        self.disableSetBkg()  ## turn off setting it again
        if self.bkg.fileName != 'flat':
            txt = os.path.basename(self.bkg.fileName)
            MsgBox(txt + " " +  "set to background")

    def snapShot(self):
        if self.hasBackGround() or self.scene.items():
            self.canvas.unSelect()  ## turn off any select borders
            if self.mapper.mapSet:
                self.mapper.removeMap()
            if self.canvas.openPlayFile == '':
                snap = "dots_" + snapTag() + ".jpg"
            else:
                snap = os.path.basename(self.canvas.openPlayFile)
                snap = snap[:-5] + ".jpg"
            if snap[:4] != "dots":  ## always ask unless
                Q = QFileDialog()
                f = Q.getSaveFileName(self, paths["snapShot"],
                    paths["snapShot"] + snap)
                if not f[0]:
                    return
                elif not f[0].lower().endswith('.jpg'):
                    MsgBox("Wrong file extention - use '.jpg'")
                    return
                snap = os.path.basename(f[0])
            pix = self.canvas.view.grab(QRect(QPoint(0,0), QSize()))
            pix.save(paths["snapShot"] + snap,
                format='jpg',
                quality=100)
            MsgBox("Saved as " + snap, 3)

    def enableBkgBtns(self, bool):
        self.sliders.enableSliders(bool)
        self.dots.btnSetBkg.setEnabled(bool)
        self.dots.btnSaveBkg.setEnabled(bool)

    def disableBkgBtns(self):
        self.enableBkgBtns(False)

    def disableSetBkg(self):
        self.dots.btnAddBkg.setEnabled(True)
        self.dots.btnSetBkg.setEnabled(False)
        self.dots.btnSaveBkg.setEnabled(True)

    def hasBackGround(self):
        for itms in self.scene.items(Qt.AscendingOrder):
            if itms.type == 'bkg':
                return True
        return False

def snapTag():
    return str(random.randrange(1000,9999)) + chr(random.randrange(65,90))

### --------------------- dotsBkgItem ----------------------
