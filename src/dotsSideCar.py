
import random
import time

from PyQt6.QtCore       import Qt, QPointF, QTimer
from PyQt6.QtWidgets    import QApplication

                                                 
from dotsShared         import common, paths
from dotsSideGig        import constrain

from dotsPixItem        import PixItem
from dotsMapMaker       import MapMaker
from dotsVideoPlayer    import VideoPlayer

### ---------------------- dotsSideCar ---------------------
''' no class: pixTest, transFormPixitem,  clearWidgets, videoPlayer, 
    toggles, small functions and a few from showbiz '''   
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
                pix.locked = False;  pix.tag = ''
                self.transFormPixItem(pix, rotation, scale, 1.0)
                                                                 
    def clearWidgets(self):                             
        for widget in QApplication.allWidgets():  ## note!!
            if widget.accessibleName() == 'widget':  ## shadow and pixitems widgets
                widget.close()
        if self.canvas.pathMakerOn: self.canvas.pathMaker.pathChooserOff()
                                                              
    def dump(self, called=''):  ## shift-M
        print()
        for itm in self.canvas.scene.items():
            if itm.type in ('bkg', 'flat', 'video'):       
                print(f'{itm.type.strip()}\t{itm.zValue()}\t{itm.fileName}')  
                                       
### --------------------------------------------------------         
    def addVideo(self, fileName, src='', loops=False):  ## plays if 'dnd'  
        if  self.canvas.videoPlayer != None:
            self.videoOff()
             
        if src == 'dnd' and self.canvas.control == '':
            self.canvas.showWorks.disablePlay()  ## enables pause/resume/stop   
            self.canvas.control = ''  ## otherwise it won't run
            
        elif self.canvas.pathMakerOn:  ## no animation
             self.canvas.showWorks.enablePlay()
                  
        for itm in self.scene.items(Qt.SortOrder.AscendingOrder):  
            if itm.type in ('bkg', 'flat'):  ## make room for videoplayer and backdrop
                itm.setZValue(itm.zValue()-1)  
            elif itm.zValue() > -50:
                break    
                   
        self.canvas.videoPlayer = VideoPlayer(self.canvas, fileName, src, loops)   
        self.scene.addItem(self.canvas.videoPlayer.videoItem)  ## zValue set to cover screen  
        QTimer.singleShot(300, self.canvas.videoPlayer.setBackDrop) 
    
    def looper(self):
        if self.canvas.videoPlayer != None:  
            if self.canvas.videoPlayer.loopSet == False:   
                self.canvas.videoPlayer.loopSet = True
                self.canvas.btnLoop.setText('LoopOn')
            else:
                self.canvas.videoPlayer.loopSet = False
                self.canvas.btnLoop.setText('Loop')
                self.canvas.btnStop.setEnabled(True)
                self.canvas.videoPlayer.stopVideo()
                if self.canvas.control != '':   ## animation running
                    self.canvas.showbiz.showtime.stop()
         
    def videoOff(self):  ## also called from storyboard in clear()
        if  self.canvas.videoPlayer == None:
            return 
        self.canvas.videoPlayer.loopSet = False
        self.canvas.videoPlayer.stopVideo()  ## very process intensive
        self.canvas.videoPlayer = None 
        self.canvas.showWorks.enablePlay()
        self.canvas.btnLoop.setText('Loop')
        time.sleep(.20) 
        self.removeSceneItems() 
                  
    def removeSceneItems(self):              
        for itm in self.scene.items(Qt.SortOrder.AscendingOrder):
            if itm.type in ('video', 'ball'):
                self.scene.removeItem(itm)
                del itm 
            elif itm.zValue() > -50:
                break   
        if self.canvas.control == '' and \
            self.canvas.animationRunning == False or  \
            self.canvas.openPlayFile not in ('snakes', 'bats', 'hats'):  
            if len(self.scene.items()) > 0:                         
                self.canvas.showWorks.enablePlay() 
        else:
            self.canvas.showWorks.disablePlay()        
        self.canvas.btnRun.setText('Run')  
        
    def delbackdrp(self):  ## dbl-clk from backdrp - just in case?
        for itm in self.scene.items(Qt.SortOrder.AscendingOrder):
            if itm.type == 'ball':
                self.scene.removeItem(itm)
                del itm
            elif itm.zValue() > -50:
                break  
        if self.canvas.videoPlayer != None:
            self.canvas.videoPlayer.backdrp = None
   
### --------------------------------------------------------      
    def xy(self, max):
        return random.randrange(-40, max+40)
                                                                                                   
    def pageDown(self, key):  ## because scrollpanel wasn't reachable for controlview at the time
        self.canvas.scroll.pageDown(key)

    def pause(self):  ## called thru controlview spacebar as well
        self.canvas.showbiz.showtime.pause() 
        
    def toggleOutlines(self):  ## runs from O as in Ohio
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadowMaker != None and \
                pix.shadowMaker.isActive:
                    pix.shadowMaker.works.toggleOutline()  ## where it happens
                                  
    def toggleSpriteLocks(self):  ## lock/unlock sprites - from controlview
        self.mapper.addTagGroup()
        for pix in self.scene.items():
            if pix.type == 'pix':
                pix.lockSprite() if pix.locked == False \
                    else pix.unlockSprite()    
                self.mapper.tagsAndPaths.tagThis('',  pix)
                                         
    def toggleShadowLinks(self):  ## link/unlink shadows - from controlview
        self.mapper.addTagGroup()
        for pix in self.scene.items():
            if pix.type == 'shadow':
                pix.linkShadow() if pix.maker.linked == False \
                    else pix.unlinkShadow()    
                self.mapper.tagsAndPaths.tagThis('',  pix)
                                                                                                   
    def resetAll(self):  ## from controlview
        self.mapper.addTagGroup()
        for pix in self.scene.items():
            if pix.type == 'pix':
                pix.unlockSprite()
                pix.setSelected(False) 
                pix.isHidden = False   
                self.mapper.tagsAndPaths.tagThis('',  pix)          
            elif pix.type == 'shadow':
                pix.unlinkShadow()
                pix.maker.works.hideOutline()
                self.mapper.tagsAndPaths.tagThis('',  pix)
        self.canvas.sideCar2.unlockAll()
    
    def clearSceneItems(self):  ## from storyboard
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
                                                         
    def hideOutlines(self):  ## runs from showRunner and ShowTime
        for pix in self.scene.items():
            if pix.type == 'pix'and pix.shadowMaker != None and \
                pix.shadowMaker.isActive:
                    pix.shadowMaker.works.hideOutline()
         
    def showOutlines(self):  ## runs showRunner
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadowMaker != None and \
                pix.shadowMaker.isActive:
                    pix.shadowMaker.works.showOutline()
                                  
    def toggleSelections(self):  ## hides/unhides selections 
        self.showSelected() if self.hasHiddenPix() else self.hideSelected()   
           
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
                    if pix.isHidden:
                        pix.setSelected(True)
                        pix.isHidden = False
                elif pix.zValue() <= common['pathZ']:
                    break
  
### ---------------------- dotsSideCar ---------------------


