
import os
import os.path
import random

from PyQt6.QtCore       import Qt, QPointF
from PyQt6.QtWidgets    import QApplication
                                                    
from dotsShared         import common, paths
from dotsPixItem        import PixItem
from dotsSideGig        import constrain, VideoPlayer
from dotsMapMaker       import MapMaker

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
    def clearWidgets(self):                             
        for widget in QApplication.allWidgets():  ## note!!
            if widget.accessibleName() == 'widget':  ## shadow and pixitems widgets
                widget.close()
        if self.canvas.pathMakerOn: self.canvas.pathMaker.pathChooserOff()
                                                                                                                 
    def pageDown(self, key):  ## because scrollpanel wasn't reachable for controlview at the time
        self.canvas.scroll.pageDown(key)

    def pause(self):  ## called thru controlview spacebar as well
        self.canvas.showbiz.showtime.pause() 
              
    def videoPlayer(self, fileName=""):
        if self.canvas.video == None:
            self.canvas.video = VideoPlayer(self.canvas, fileName)
            if self.canvas.control == '':  ## no animation, disables run, enables 
                self.canvas.showWorks.disablePlay()  ## pause/resume/stop
                
    def videoOff(self):
        if self.canvas.video != None:
            self.canvas.video = None
        if self.canvas.openPlayFile in ('snakes', 'bats', 'hats'):  ## leave 'stop' alone
            return
        elif self.canvas.animation == False:  ## only place it's used
            self.canvas.showWorks.enablePlay()  ## enable run, disable pause/resume/stop
            
### --------------------------------------------------------
    def toggleKeysMenu(self):  ## keysPanel
        self.canvas.keysPanel.toggleKeysMenu()  ## no direct path from controlView
  
    def toggleOutlines(self):  ## runs from O as in Ohio
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadowMaker != None and \
                pix.shadowMaker.isActive == True:
                    pix.shadowMaker.works.toggleOutline()
                                  
    def toggleSpriteLocks(self):  ## lock/unlock sprites
        self.mapper.addTagGroup()
        for pix in self.scene.items():
            if pix.type == 'pix':
                pix.lockSprite() if pix.locked == False \
                    else pix.unlockSprite()    
                self.mapper.tagsAndPaths.tagThis('', pix, '')
                                         
    def toggleShadowLinks(self):  ## link/unlink shadows
        self.mapper.addTagGroup()
        for pix in self.scene.items():
            if pix.type == 'shadow':
                pix.linkShadow() if pix.maker.linked == False \
                    else pix.unlinkShadow()    
                self.mapper.tagsAndPaths.tagThis('', pix, '')
       
    def toggleTagItems(self, all=''):  ##  standin for mapper version
        if self.mapper.tagCount() > 0:      
            self.mapper.clearTagGroup()
            self.mapper.clearPaths() 
            return
        self.mapper.addTagGroup()
        for pix in self.scene.items():
            if pix.type in ('pix', 'shadow'):   
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
    
    def clearSceneItems(self):
        for p in self.scene.items():      
            if p.type == 'pix' and p.part in ('left', 'right'):
                continue
            try:
                self.scene.removeItem(p) 
            except Exception:
                continue
                                                                                                                                  
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


