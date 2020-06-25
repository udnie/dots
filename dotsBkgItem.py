import os
import sys
import random

import os.path
from os import path

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from datetime import datetime

import dotsQt

bkgZ = -99.0

### ---------------------- dotsBkgItem ---------------------
class BkgItem(QGraphicsPixmapItem):

    def __init__(self, imgFile, viewW, viewH, parent):
        super().__init__()
        
        self.parent = parent
        self.filename = imgFile

        img = QImage(imgFile)

        self.imgFile = img.scaled(viewW, viewH, 
            Qt.KeepAspectRatio|
            Qt.SmoothTransformation)

        self.key = ""
        self.type = 'bkg'
      
        self.flopped = False
        self.isBackgroundSet = False
     
        self.viewW = viewW
        self.viewH = viewH

        self.width = self.imgFile.width()
        self.height = self.imgFile.height()
        
        self.x = (self.viewW - self.width)/2
        self.y = (self.viewH - self.height)/2  
   
        self.setPos(self.x, self.y)

        self.setPixmap(QPixmap.fromImage(self.imgFile))
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)

    def mousePressEvent(self, e):
        if self.parent.key == 'shift':          # delete it
            self.parent.scene.removeItem(self)
            self.parent.disableSliders()
        elif self.parent.key == 'draw' and self.isBackgroundSet == False \
            and self.key != 'lock':             # flop it
            if self.flopped == False:
                self.flopped = True
            else:
                self.flopped = False          
            self.setPixmap(QPixmap.fromImage(self.imgFile.mirrored(
                horizontal=self.flopped,
                vertical=False)))
            self.setTransformationMode(Qt.SmoothTransformation)

### --------------------------------------------------------
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
        brt = self.boundingRect()
        self.width = brt.width()
        self.height = brt.height()
   
### --------------------------------------------------------
class InitBkg(QWidget):
    
    def __init__(self, parent):
        super().__init__()
         
        self.parent = parent
        self.shared = dotsQt.Shared() 

        self.sliders = self.parent.sliders
        self.buttons = self.parent.buttons
        
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
            "Choose an image file to open", '', 
            "Images Files(*.bmp *.jpg *.png)")
        if len(file) != 0:
            self.bkg = BkgItem(
                file, 
                self.shared.viewW, 
                self.shared.viewH,
                self.parent)
            self.parent.scene.addItem(self.bkg)
            if '-bkg.jpg' in file:
                self.lockBkg()
            else:
                self.enableSave(True)
                dotsQt.setCursor
                
    def setBackground(self):
        if self.bkg.isBackgroundSet == False and self.bkg.key != 'lock':
            self.lockBkg()
        else:
            self.enableSave(False)
            MsgBox("Already set to background") 

    def lockBkg(self):
        self.sliders.enableSliders(False)
        self.mapKeys("lock", 0)  ## 0 is a place holder
        if self.parent.hasBackGround() > 0:
            for itm in self.parent.scene.items():  ## works best in descending order
                if itm.type == 'bkg' and itm.zValue():
                    itm.setZValue(self.parent.lastZval('bkg')-1)
        self.bkg.setZValue(bkgZ)
        self.bkg.isBackgroundSet = True
        self.enableSave(False)
        MsgBox("Set to background")
        
    def saveBkg(self):
        if self.buttons.btnSave.isEnabled() and self.bkg.isBackgroundSet:
            file = os.path.basename(self.bkg.filename)
            file = file[0: file.index('.')]
            file = file[-15:] + "-bkg.jpg"
            ## if it's not already a bkg file and the new file doesn't exist
            if not self.bkg.filename.lower().endswith("-bkg.jpg") and not \
                path.exists(self.shared.bkgPath + file):
                pix = self.parent.view.grab(QRect(QPoint(-1,-1), QSize()))
                pix.save(self.shared.bkgPath + file, 
                    format='jpg', 
                    quality=100)
                MsgBox("Saved as " + file)
            else:
                MsgBox("Already saved as background jpg")
            self.enableSave(False)
         
    def snapShot(self):        
        if self.parent.hasBackGround() > 0 or len(self.parent.scene.items()) > 0:    
            self.parent.unSelect()  ## turn off any select borders
            pix = self.parent.view.grab(QRect(QPoint(0,0), QSize(-1,-1)))
            snap = "dots_" + snapTag() + ".jpg"
            pix.save(self.shared.snapShot + snap, 
                format='jpg', 
                quality=90)
            MsgBox("Saved as " + snap)
   
    def enableSave(self, bool):
        self.sliders.enableSliders(bool)
        self.buttons.btnSetBkg.setEnabled(bool)
        self.buttons.btnSave.setEnabled(bool)

### --------------------------------------------------------
class MsgBox(QMessageBox):  ## another stackoverflow solution

    def __init__(self, text):
        super().__init__()

        self.timeOut = 2
        self.setText("\n" + text)
        self.setStandardButtons(QMessageBox.NoButton)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

        self.exec_()

    def enterEvent(self, e):  
        self.close()

    def changeContent(self):
        self.timeOut -= 1
        if self.timeOut <= 0:
            self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept() 

def snapTag():
    return str(random.randrange(1000,9999)) + chr(random.randrange(65,90))

### --------------------- dotsBkgItem ----------------------
