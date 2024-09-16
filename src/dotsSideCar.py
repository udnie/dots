
import os
import os.path
import random

from PyQt6.QtCore       import QAbstractAnimation, Qt, QPointF, QPoint, QSize, QRect
from PyQt6.QtWidgets    import QFileDialog, QApplication
                                                    
from dotsShared         import common, paths
from dotsPixItem        import PixItem
from dotsSideGig        import MsgBox, constrain, Grid
from dotsMapMaker       import MapMaker
from dotsBkgScrollWrks  import tagBkg

### ---------------------- dotsSideCar ---------------------
''' no class: just stuff - pixTest, transFormPixitem, snapShot,
    help menu switch, small functions and a few from showbiz '''   
### --------------------------------------------------------
class SideCar:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.dots   = self.canvas.dots
        self.scene  = self.canvas.scene
        self.mapper = MapMaker(self.canvas)
 
        self.grid = Grid(self.canvas)
     
### --------------------------------------------------------
    def transFormPixItem(self, pix, rotation, scale, alpha2):         
        op = QPointF(pix.width/2, pix.height/2)  
        pix.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        pix.setTransformOriginPoint(op)
              
        pix.rotation = rotation
        pix.scale    = scale 
        pix.alpha2   = alpha2
        
        pix.setRotation(pix.rotation)         
        pix.setScale(pix.scale)     
        pix.setOpacity(pix.alpha2)
                                                              
        self.scene.addItem(pix)
                              
### --------------------------------------------------------
    def pixTest(self):  ## randomly places 10 apples on the canvas to play with 
        if not self.canvas.pathMakerOn:  
            self.canvas.pixCount = self.canvas.mapper.toFront()
            for _ in range(10):
                self.canvas.pixCount += 1
                pix = PixItem(paths['spritePath'] + 'apple.png', self.canvas.pixCount, 0, 0, 
                        self.canvas)
                ## note -> self.xy()
                pix.x = int(constrain(self.xy(common['ViewW']), pix.width, common['ViewW'], 
                        pix.width * -common['factor']))  ## factor from screens
                pix.y = int(constrain(self.xy(common['ViewH']), pix.height, common['ViewH'],
                        pix.height * -common['factor']))
                pix.setPos(pix.x, pix.y)
                rotation = random.randrange(-5, 5) * 5
                scale = random.randrange(90, 110)/100.0
                self.transFormPixItem(pix, rotation, scale, 1.0)
                             
    def xy(self, max):
        return random.randrange(-40, max+40)
                                    
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
  
### --------------------------------------------------------   
    def clearWidgets(self):                             
        for widget in QApplication.allWidgets():  ## note!!
            if widget.accessibleName() == 'widget':  ## shadow and pixitems widgets
                widget.close()
        if self.canvas.pathMakerOn: self.canvas.pathMaker.pathChooserOff()
  
    def hasBackGround(self):
        for itm in self.scene.items(Qt.SortOrder.AscendingOrder):
            if itm.type == 'bkg':
                return True
        return False
                                                                                                                 
    def pause(self):  ## because showtime wasn't reachable for controlview at the time
        self.canvas.showtime.pause()
    
    def pageDown(self, key):  ## because scrollpanel wasn't reachable for controlview at the time
        self.canvas.scroll.pageDown(key)
      
    def snapTag(self):
        return str(random.randrange(1000,9999)) + chr(random.randrange(65,90))
      
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
    def toggleKeysMenu(self):  ## keysPanel
        self.canvas.keysPanel.toggleKeysMenu()  ## no direct path from controlView
  
    def toggleOutlines(self):  ## runs from O as in Ohio
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadowMaker != None and \
                pix.shadowMaker.isActive == True:
                    pix.shadowMaker.works.toggleOutline()
                                  
    def toggleSprites(self):  ## lock/unlock sprites
        self.mapper.addTagGroup()
        for pix in self.scene.items():
            if pix.type == 'pix':
                pix.lockSprite() if pix.locked == False \
                    else pix.unlockSprite()    
                self.mapper.tagsAndPaths.tagThis('', pix, '')
                                         
    def toggleShadows(self):  ## link/unlink shadows
        self.mapper.addTagGroup()
        for pix in self.scene.items():
            if pix.type == 'shadow':
                pix.linkShadow() if pix.maker.linked == False \
                    else pix.unlinkShadow()    
                self.mapper.tagsAndPaths.tagThis('', pix, '')
                                                                                                    
    def resetAll(self):
        self.mapper.addTagGroup()
        for pix in self.scene.items():
            if pix.type == 'pix':
                pix.unlockSprite()
                pix.setSelected(False) 
                pix.isHidden = False   
                self.mapper.tagsAndPaths.tagThis('', pix, '')          
            elif pix.type == 'shadow':
                pix.unlinkShadow()
                pix.maker.works.hideOutline()
                self.mapper.tagsAndPaths.tagThis('', pix, '')
            elif pix.type == 'bkg': 
                pix.bkgMaker.unlockBkg(pix)  
                tagBkg(pix, QPoint(350, 200))
                                                                                                                                                                      
### --------------------------------------------------------                                                
    def hasHiddenPix(self):
        for pix in self.scene.items():
            if pix.type == 'pix'and pix.part not in ('pivot', 'left','right'):
                if pix.isHidden: 
                    return True  ## found one
            elif pix.zValue() <= common['pathZ']:
                break
        return False                                              
                                                         
    def hideOutlines(self):  ## runs from shift-O
        for pix in self.scene.items():
            if pix.type == 'pix'and pix.shadowMaker != None and \
                pix.shadowMaker.isActive == True:
                    pix.shadowMaker.works.hideOutline()
         
    def showOutlines(self):  ## runs from shift-O
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadowMaker != None and \
                pix.shadowMaker.isActive == True:
                    pix.shadowMaker.works.showOutline()
                                  
    def toggleSelections(self):
        if self.hasHiddenPix():
            self.showSelected()  ## hide selector frame - that's it     
        else:
            self.hideSelected()   
     
    def hideSelected(self):  
        if len(self.scene.items()) > 0 and self.scene.selectedItems():
            self.mapper.removeMap()  ## also updates pix.pos()
            for pix in self.scene.items():
                if pix.type == 'pix' and pix.part not in ('pivot', 'left','right'):
                    if pix.isSelected():
                        pix.setSelected(False)
                        pix.isHidden = True
                elif pix.zValue() <= common['pathZ']:
                    break
                                  
    def showSelected(self):  
        if len(self.scene.items()) > 0:
            for pix in self.scene.items():
                if pix.type == 'pix' and pix.part not in ('pivot', 'left','right'):
                    if pix.isHidden == True:
                        pix.setSelected(True)
                        pix.isHidden = False
                elif pix.zValue() <= common['pathZ']:
                    break
                                                                                                                                                                                                                           
    def hideSelectedShadows(self):  ## runs from shift-O
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadowMaker != None and pix.shadowMaker.isActive == True:
                if pix.isSelected():
                    pix.shadowMaker.shadow.hide() 
                elif pix.shadowMaker.shadow.isVisible() == False:
                    pix.shadowMaker.shadow.show()       
                    pix.setSelected(True)
  
### ---------------------- dotsSideCar ---------------------


