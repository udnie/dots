
import os
import os.path
import random

from PyQt6.QtCore       import QAbstractAnimation, QPoint, QSize, QRect
from PyQt6.QtWidgets    import QFileDialog
                                                    
from dotsShared         import common, paths
from dotsSideGig        import MsgBox
from dotsMapMaker       import MapMaker
from dotsBkgItem        import BkgItem

### --------------------- dotsSideCar2 ---------------------
''' no class: snapShot,dumptrackers, addBkgLabels, setMirroredBtnText,
    setBtns, tagBkg and files from storyboard - no connection to pathMaker'''   
### --------------------------------------------------------
class SideCar2:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.scene  = self.canvas.scene
        self.mapper = MapMaker(self.canvas)
  
### --------------------------------------------------------      
    def snapShot(self, pathMaker):  ## screen capture
        if self.hasBackGround() > 0 or self.scene.items():
            self.unSelect()  ## turn off any select borders
            if self.canvas.pathMakerOn == False:
                if self.mapper.isMapSet():
                    self.mapper.removeMap()
                    
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
                           
    def snapTag(self):
        return str(random.randrange(1000,9999)) + chr(random.randrange(65,90))
                         
### --------------------------------------------------------   
    def gotFlats(self):
        for itm in self.scene.items():  ## used in showbiz
            if itm.type == 'flat':
                return True
        return False
    
    def hasBackGround(self): 
        return sum(pix.type == 'bkg' for pix in self.scene.items())
                   
    def bkgStuff(self):
        self.canvas.bkgMaker.openBkgFiles() if self.hasBackGround() == 0 \
            else self.sendPixKeys('B')
                 
    def newTracker(self):  
        if self.hasBackGround() > 0:
            self.canvas.bkgMaker.bkgtrackers.trackThis() if self.canvas.bkgMaker.bkgtrackers.tracker == None \
                else self.canvas.bkgMaker.bkgtrackers.tracker.bye()  
                            
    def mirrorBkg(self, switch):  ## either 1 default or -1, flip it
        if self.hasBackGround() and self.canvas.openPlayFile == '':  ## only a background
            wuf = None
            for bkg in self.scene.items():  
                if bkg.type == 'bkg':
                    wuf = bkg
                    break  
            if wuf == None: return  
            
            bkg.setMirrored(bkg.flopped, switch)    
            x = int(common['ViewW']/2- bkg.width)  ## starts off screen - left
            bkg.setPos(x , 0)   

            akg = BkgItem(wuf.fileName, self.canvas, common['bkgZ'], wuf.imgFile)
            if akg == None:
                return
            
            self.scene.addItem(akg)  
            akg.setMirrored(True, switch) if bkg.flopped == False else akg.setMirrored(False, switch) 
            akg.setPos(int(common['ViewW']/2), 0)  ## start center screen
        
        self.delDupes()
                                       
    def delDupes(self):  ## otherwise they can build up
        if self.hasBackGround() >= 3:
            i = 0
            for bkg in self.scene.items():  
                if bkg.type == 'bkg':
                    i += 1 
                    if i >= 3:
                        self.scene.removeItem(bkg)

### --------------------------------------------------------
    def sendPixKeys(self, key):
        if self.canvas.bkgMaker.bkgtrackers.tracker != None and \
            key in ('up', 'down'):  ## to trackers
                self.canvas.bkgMaker.bkgtrackers.tracker.setPixKeys(key) 
                return
            
        elif self.canvas.bkgMaker.widget != None and key in ('up', 'down','right','left'):
            self.canvas.bkgMaker.widget.setKeys(key)  ## to bkgWidget
            return
        ## update pixitems and bkgItems thru setPixKeys
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
            self.canvas.bkgMaker.openBkgFiles() 
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
  
    def unSelect(self):
        for itm in self.scene.items():  
            if itm.type == 'pix':       
                itm.isHidden = False 
                itm.setSelected(False) 
            
    def unlockAll(self):
        for itm in self.scene.items():  
            if itm.type == 'pix':
                itm.unlockSprite()            
            elif itm.type == 'bkg':
                self.canvas.bkgMaker.unlockBkg(itm)
        
    def flopSelected(self):    
        if self.canvas.pathMakerOn == False:
            if len(self.scene.selectedItems()) > 0:
                for pix in self.scene.items():
                    if pix.type == 'pix':
                        if pix.isSelected() or pix.isHidden:
                            pix.setMirrored(False) if pix.flopped else pix.setMirrored(True)   
                    elif pix.zValue() <= common['pathZ']:
                        break
            else:
                self.canvas.setKeys('F')
    
    def setMirrorBtnText(self, bkg, widget):  ## if added - from bkgMaker widget
        if bkg:  ## shouldn't need this but - could have just started to clear        
            if self.canvas.dots.Vertical == False and bkg.imgFile.width() >= bkg.showtime + bkg.ViewW or \
                self.canvas.dots.Vertical == True and bkg.imgFile.height() >= bkg.showtime + bkg.ViewH:  
                bkg.scrollable = True    
                                                  
            if bkg.scrollable == False:
                widget.mirrorBtn.setText('Not Scrollable')  
                bkg.direction = ''    
                          
            widget.mirrorBtn.setText('Continuous') if bkg.mirroring == False else \
                widget.mirrorBtn.setText('Mirrored')

    def setBtns(self, bkg, widget):  ## from bkgMaker widget
        match bkg.direction:  
            case 'right': 
                widget.rightBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                widget.leftBtn.setStyleSheet(
                    'background-color: None') 
            case 'left': 
                widget.leftBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                widget.rightBtn.setStyleSheet(
                    'background-color: None')
            case 'vertical':
                widget.leftBtn.setText('Vertical')   
                widget.leftBtn.setStyleSheet(
                    'background-color: LIGHTGREY')
                                              
### --------------------- dotsSideCar2 ---------------------


