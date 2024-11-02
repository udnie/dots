
import os
import os.path
import random

from PyQt6.QtCore       import Qt,  QAbstractAnimation, QPoint, QSize, QRect
from PyQt6.QtWidgets    import QFileDialog
                                                    
from dotsShared         import common, paths
from dotsSideGig        import MsgBox
from dotsMapMaker       import MapMaker

### ---------------------- dotsSideCar ---------------------
''' no class: just snapShot,dumptrackers, addBkgLabels and small functions '''   
### --------------------------------------------------------
class SideCar2:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.dots   = self.canvas.dots
        self.scene  = self.canvas.scene
        self.mapper = MapMaker(self.canvas)

### --------------------------------------------------------      
    def snapShot(self):  ## screen capture
        if self.hasBackGround() or self.scene.items():
            self.canvas.unSelect()  ## turn off any select borders
            if self.canvas.pathMakerOn == False:
                if self.canvas.mapper.isMapSet():
                    self.canvas.mapper.removeMap()
                    
            if self.canvas.openPlayFile == '':
                snap = 'dots_' + self.snapTag() + '.jpg'
            else:
                snap = os.path.basename(self.canvas.openPlayFile)
                snap = snap[:-5] + '.jpg'
                
            if snap[:4] != 'dots':  ## always ask unless                      
                Q = QFileDialog()
                Q.Option.DontUseNativeDialog
                Q.setDirectory(paths['snapShot'])
                f = Q.getSaveFileName(self.canvas, paths['snapShot'],
                    paths['snapShot'] + snap)
                Q.accept()
                if not f[0]:
                    return
                elif not f[0].lower().endswith('.jpg'):
                    MsgBox("Wrong file extention - use '.jpg'", 5)
                    return
                snap = os.path.basename(f[0])
            pix = self.canvas.view.grab(QRect(QPoint(0,0), QSize()))
            pix.save(paths['snapShot'] + snap, format='jpg',
                quality=100)        
            MsgBox('Saved as ' + snap, 3)
  
    def hasBackGround(self):
        for itm in self.scene.items(Qt.SortOrder.AscendingOrder):
            if itm.type == 'bkg':
                return True
        return False
                         
    def snapTag(self):
        return str(random.randrange(1000,9999)) + chr(random.randrange(65,90))
                         
### --------------------------------------------------------   
    def gotFlats(self):
        for itm in self.scene.items():  ## used in showbiz
            if itm.type == 'flat':
                return True
        return False
  
    def dumpTrackers(self):  ## used by bkgItem - 'B' in BkgHelp menu
        dump = []  
        for p in self.scene.items():
            if p.type == 'bkg':
                fileName = os.path.basename(p.fileName)  ## opposite of setMirroring 
                try:            
                    if r := self.canvas.bkgMaker.newTracker[fileName]: 
                        zval = p.zValue()
                        fileName, direction, mirroring, locked = self.addBkgLabels(p)
                        rate, showtime, path = str(r['rate']), str(r['showtime']), r['path']
                        s = f"{fileName} {zval} {direction} {mirroring} {rate} {showtime} {r['useThis']} {path[5:-1]}"
                        dump.append(s.split())
                except:
                    None            
        if len(dump) > 0:
            return dump
        else:
            MsgBox('Error in dumpTrackers - SideCar')
            return None

    def addBkgLabels(self, bkg):  ## used by dumpTrackers
        fileName = bkg.fileName       
        if bkg.locked == True:
            locked = 'Locked' 
        else:
            locked = 'UnLocked' 
        if bkg.direction == 'left':
            direction = 'Left'
        elif bkg.direction == 'right': 
            direction = 'Right'     
        elif self.dots.Vertical:
            direction = 'Vertical'
        else:
            if self.canvas.bkgMaker.newTracker[fileName]:   
                direction = self.canvas.bkgMaker.newTracker[fileName]['direction']     
            if direction == '':
                direction = 'NoDirection'
        if bkg.mirroring == False:
            mirror = 'Continuous'
        elif bkg.mirroring == True:
            mirror = 'Mirrored'
        elif bkg.direction == '' and bkg.scrollable == False:
            mirror = 'Not Scrollable'    
        return fileName.capitalize(), direction, mirror, locked
  
### --------------------------------------------------------
    def sendPixKeys(self, key):  ## update pixitems and bkgItems thru setPixKeys
        for itm in self.scene.items():  ## used with lasso to move selections
            if itm.type == 'pt' or itm.type == 'pix' and \
                itm.part not in ('pivot','left','right'):  
                itm.setPixKeys(key)
            elif itm.type in ('bkg', 'frame', 'flat', 'shadow'):   
                itm.setPixKeys(key)     
        if self.mapper.isMapSet(): 
            self.mapper.updateMap()

    def selectAll(self):
        if len(self.scene.items()) == 0:  ## if 'A' 
            self.bkgMaker.openBkgFiles() 
            return
        for pix in self.scene.items():
            if pix.type in ('pix', 'shadow'):
                pix.setSelected(True)
                pix.isHidden = False
            elif pix.zValue() <= common['pathZ']:
                break
 
    def deleteSelected(self):  ## self.pathMakerOn equals false   
        if len(self.scene.items()) == 0:
            self.canvas.setKeys('D')
        else:
            self.mapper.clearMap()
            self.mapper.clearTagGroup()
            k = 0
            for pix in self.scene.selectedItems():      
                if pix.type == 'pix':  ## could be something else
                    if pix.anime != None and \
                        pix.anime.state() == QAbstractAnimation.State.Running:
                        pix.anime.stop()  
                    pix.setSelected(False)
                    pix.deletePix()  ## deletes shadow as well 
                    del pix
                    k += 1
            if k > 0: self.canvas.showWorks.enablePlay()  ## stop it - otherwise it's hung
            
    def flopSelected(self):    
        if self.canvas.pathMakerOn == False:
            if len(self.scene.selectedItems()) > 0:
                for pix in self.scene.items():
                    if pix.type == 'pix':
                        if pix.isSelected() or pix.isHidden:
                            if pix.flopped:
                                pix.setMirrored(False)
                            else:
                                pix.setMirrored(True)
                    elif pix.zValue() <= common['pathZ']:
                        break
            else:
                self.canvas.setKeys('F')
                             
### --------------------- dotsSideCar2 ---------------------


