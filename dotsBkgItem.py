import os
import sys
import random

import os.path
from os import path

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from dotsShared      import common, paths

import dotsSideCar as sideCar

bkgZ = -99.0

### ---------------------- dotsBkgItem ---------------------
''' dotsBkgItem: handles adding, setting, copying and saving background 
    items.  Includes BkgItem and InitBkg classes. '''
### --------------------------------------------------------
class BkgItem(QGraphicsPixmapItem):

    def __init__(self, imgFile, parent, mirror=False):
        super().__init__()

        self.canvas  = parent
        self.sideCar = self.canvas.sideCar
        self.fileName = imgFile

        img = QImage(imgFile)

        self.viewW = common["viewW"]
        self.viewH = common["viewH"]

        self.imgFile = img.scaled(
            self.viewW, 
            self.viewH,
            Qt.KeepAspectRatio|
            Qt.SmoothTransformation)

        self.key = ""

        self.type = 'bkg'
        self.flopped = mirror

        self.rotation = 0
        self.scale = 1.0

        self.setZValue(0)
        self.tag = ''
        self.isBackgroundSet = False

        self.width = self.imgFile.width()
        self.height = self.imgFile.height()

        self.x = (self.viewW - self.width)/2
        self.y = (self.viewH - self.height)/2

        self.setPos(self.x, self.y)
        self.setMirrored(mirror)

        self.setPixmap(QPixmap.fromImage(self.imgFile))
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)

### --------------------------------------------------------
    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.ungrabMouse()   
        if self.canvas.key == 'del':       # delete it
            self.canvas.scene.removeItem(self)
            self.canvas.disableSliders()
            self.canvas.buttons.btnBkgFiles.setEnabled(True)
        elif self.canvas.key == 'bak':    # send to back
            self.setZValue(self.sideCar.lastZval('bkg')-1)
        elif self.canvas.key == 'shift':
            if self.flopped == False:
                self.flopped = True
            else:
                self.flopped = False
            self.setMirrored(self.flopped)

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
        sideCar.widthHeightSet(self)

### --------------------------------------------------------
class InitBkg(QWidget):

    def __init__(self, parent):
        super().__init__()

        self.canvas  = parent
        self.sliders = self.canvas.sliders
        self.buttons = self.canvas.buttons
        self.initMap = self.canvas.initMap

        self.sliders.signal[str, int].connect(self.mapKeys)

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

    def bkgfiles(self):
        Q = QFileDialog()
        file, _ = Q.getOpenFileName(self,
            "Choose an image file to open", paths["bkgPath"],
            "Images Files(*.bmp *.jpg *.png)")
        if file:
            self.addBkg(file)

    def addBkg(self, file, flopped=False): ## also used by saveBkg
        if self.initMap.mapSet:
            self.initMap.removeMap()
        self.bkg = BkgItem(file, self.canvas)
        self.canvas.scene.addItem(self.bkg)
        if file.endswith('-bkg.jpg'):
            self.bkg.setScale(1.003)   ## for white space???
            self.bkg.centerBkg()
            self.lockBkg()
        else:
            self.buttons.btnBkgFiles.setEnabled(False)
            self.enableSave(True)
            sideCar.setCursor()

    def saveBkg(self):
        if not self.bkg.isBackgroundSet:
            self.canvas.MsgBox("Set to Background inorder to save", 3)
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
                self.canvas.MsgBox("Saved as " + file, 3)
                self.canvas.clear() ## replace current background with "-bkg.jpg" copy   
                self.addBkg(self.bkg.fileName, flopped)
            else:
                self.canvas.MsgBox("Already saved as background jpg")
            self.buttons.btnBkgFiles.setEnabled(True)
            self.enableSave(False)

    def setBkg(self):  ## from set background button
        if self.bkg.isBackgroundSet == False and self.bkg.key != 'lock':
            self.lockBkg()
        else:
            self.enableSave(False)
            self.buttons.btnBkgFiles.setEnabled(True)
            self.canvas.MsgBox("Already set to background")

    def lockBkg(self):
        self.sliders.enableSliders(False)
        self.mapKeys("lock", 0)   ## 0 is a place holder
        if self.hasBackGround():  ## reset zvals of existing bkgs to by -1
            ## seems to work best in descending order
            for itm in self.canvas.scene.items():
                if itm.type == 'bkg' and itm.zValue() <= bkgZ:
                    itm.setZValue(self.canvas.sideCar.lastZval('bkg')-1)
        self.bkg.setZValue(bkgZ)   ## the one showing
        self.bkg.isBackgroundSet = True

        self.buttons.btnBkgFiles.setEnabled(True)
        self.buttons.btnSetBkg.setEnabled(False)
        self.buttons.btnSave.setEnabled(True)

        txt = os.path.basename(self.bkg.fileName)
        self.canvas.MsgBox(txt + " " +  "set to background")

    def snapShot(self):
        if self.hasBackGround() or self.canvas.scene.items():
            self.canvas.unSelect()  ## turn off any select borders
            if self.initMap.mapSet:
                self.initMap.removeMap()
            if self.canvas.sideCar.openPlayFile == '':
                snap = "dots_" + sideCar.snapTag() + ".jpg"
            else:
                snap = os.path.basename(self.canvas.sideCar.openPlayFile)
                snap = snap[:-5] + ".jpg"
            if snap[:4] != "dots":  ## always ask unless
                Q = QFileDialog()
                f = Q.getSaveFileName(self, paths["snapShot"],
                    paths["snapShot"] + snap)
                if not f[0]:
                    return
                elif not f[0].lower().endswith('.jpg'):
                    self.canvas.MsgBox("Wrong file extention - use '.jpg'")
                    return
                snap = os.path.basename(f[0])
            pix = self.canvas.view.grab(QRect(QPoint(0,0), QSize()))
            pix.save(paths["snapShot"] + snap,
                format='jpg',
                quality=100)
            self.canvas.MsgBox("Saved as " + snap, 3)

    def enableSave(self, bool):
        self.sliders.enableSliders(bool)
        self.buttons.btnSetBkg.setEnabled(bool)
        self.buttons.btnSave.setEnabled(bool)

    def hasBackGround(self):
        for pix in self.canvas.scene.items(Qt.AscendingOrder):
            if pix.type == 'bkg':
                return True
            elif pix.zValue() > bkgZ:
                return False

### --------------------- dotsBkgItem ----------------------
