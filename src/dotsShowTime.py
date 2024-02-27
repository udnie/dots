
from os import path

import gc

from PyQt6.QtCore       import QAbstractAnimation
from PyQt6.QtWidgets    import QGraphicsPolygonItem, QGraphicsPixmapItem

from dotsSideGig        import *
from dotsSideCar        import SideCar
from dotsShowFiles      import savePix, saveBkgnd, saveFrame, saveFlat
from dotsShowWorks      import ShowWorks
from dotsShared         import Types, ControlKeys

Demos = ['snakes', 'bats', 'abstract']

### ---------------------- dotsShowTime --------------------
''' ShowTime: functions to run .play animations, pause, stop,
                  and save them to a .play file  '''        
### --------------------------------------------------------
class ShowTime:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas   = parent
        self.scene    = self.canvas.scene
        self.dots     = self.canvas.dots
        self.mapper   = self.canvas.mapper
        
        self.sideCar   = SideCar(self.canvas) 
        self.showWorks = ShowWorks(self.canvas)
        
        self.animation = self.canvas.animation
        self.pathMaker = self.canvas.pathMaker
     
### --------------------------------------------------------        
    def run(self):  ## runs whatever is in scene that can be animated
        if self.canvas.control != '':
            return  
        
        self.mapper.clearMap()
        self.mapper.clearPathsandTags()  
        self.canvas.unSelect()
        self.sideCar.hideOutlines()
                       
        if not self.canvas.pathList:  ## should already exist - moved from animations
            self.canvas.pathList = getPathList(True) 
            if len(self.canvas.pathList) == 0:
                MsgBox('getPathList: No Paths Found!', 5)
                return 
                 
        b, k = 0, 0  ## counts bats and pixitems  
        for pix in self.scene.items():  ## main loop - sets and runs animations
            if type(pix) == 'dotsShadowWidget.PointItem' or \
                isinstance(pix, QGraphicsPolygonItem):
                continue
                    
            if pix.type in ('pix', 'bkg') and pix.tag:    
                ## if random, slice to length, display actual anime if paused 
                if 'Random' in pix.tag:
                    pix.tag = pix.tag[0:len('Random')]                  
                ## set the animation using the tag
                if pix.type == 'pix':
                    pix.anime = self.animation.setAnimation(          
                        pix.tag, 
                        pix)        
                elif pix.type == 'bkg': 
                    if pix.tag == 'scroller':                       
                        pix.anime = pix.setScrollerPath(pix, 'first')  ## in bkgItem 
                        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag. \
                            ItemSendsScenePositionChanges, True)
                    if pix.locked:
                        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag. \
                            ItemIsMovable,False)
                         
                # if pix.type == 'pix' and pix.part == 'pivot': ## staggers bats zvalue
                #     if b == 1: 
                #         pix.setZValue(-101) 
                #     elif b == 2:            
                #         pix.setZValue(-102) 
                #     b += 1   
                
                k += 1  ## k = number of pixitems - bats count as three
                if pix.anime == None:  ## not animated
                    continue
                else:  ## staggering the start 
                    QTimer.singleShot(100 + (k * 35), pix.anime.start)    
   
        if k > 0:
            self.showWorks.disablePlay()  ## sets pause/resume/stop
            file = os.path.basename(self.canvas.openPlayFile)
            if "play" in file:
                self.dots.statusBar.showMessage(file + ' - ' + \
                    'Number of Pixitems: {}'.format(k))  
           
### --------------------------------------------------------                                 
    def pause(self):
        self.mapper.clearPathsandTags()  
        if self.canvas.control == 'resume':
           self.resume()
        else:          
            for pix in self.scene.items(): 
                if type(pix) == 'dotsShadowWidget.PointItem' or \
                    isinstance(pix, QGraphicsPolygonItem):
                    continue
                if pix.type in ('flat', 'frame'):
                    continue             
                if pix.type in ('pix', 'snake', 'bkg'):
                    if pix.anime != None and pix.anime.state() == \
                        QAbstractAnimation.State.Running:  ## running
                        pix.anime.pause() 
            self.showWorks.setPauseKey()

    def resume(self):   
        for pix in self.scene.items():  
            if type(pix) == 'dotsShadowWidget.PointItem' or \
                isinstance(pix, QGraphicsPolygonItem):
                continue
            if pix.type in ('frame','flat'):
                continue      
            if pix.type in ('pix', 'snake', 'bkg'):
                if pix.anime != None and pix.anime.state() == \
                    QAbstractAnimation.State.Paused:
                    pix.anime.resume()                   
        self.showWorks.setPauseKey()
        
### --------------------------------------------------------
    def stop(self, action=''):  ## action used by clear               
        self.mapper.clearPathsandTags()     
        scrolling = []  ## used by tracker to remove the 'next' bkg 
        
        for pix in self.scene.items():                          
            if type(pix) == 'dotsShadowWidget.PointItem' or \
                isinstance(pix, QGraphicsPolygonItem):
                continue              
            try:
                # if pix.fileName in ('frame','flat'):
                if pix.type in ('frame','flat'):
                    continue       
            except:
                continue
            
            if pix.type in ('pix', 'snake', 'bkg'):                   
                if pix.anime != None and pix.anime.state() != \
                    QAbstractAnimation.State.Stopped:       
                    pix.anime.stop()                                           
                    if pix.tag == 'scroller':  ## can be more than one
                        pix.anime = None
                        scrolling.append(pix.tag)    
                                                   
                if pix.type == 'pix' and pix.opacity() < .2:  ## just in case  
                    if self.canvas.openPlayFile != 'abstract':            
                        pix.setOpacity(1.0) 
                        pix.alpha2 = pix.opacity()  ## opacity can't be a varibale name   
                                                                                                    
                if pix.type in ('pix', 'snake'):
                    if pix.part in ('left','right'):  
                        continue  ## these stop when pivot stops                  
                    if action != 'clear':
                        if pix.type == 'pix':
                            pix.works.reprise()  ## moved         
                        elif pix.type == 'snake':
                            pix.reprise()
                      
        if len(scrolling) > 0:  ## used by tracker to remove the 'next' bkg 
            self.showWorks.cleanUpScrollers(self.canvas.scene)
            
        self.showWorks.enablePlay() 
        self.canvas.btnPause.setText( 'Pause' )
        del scrolling  
                         
### --------------------------------------------------------
    def savePlay(self):   
        if self.canvas.control in ControlKeys:  ## there's an animation running - needs to be stopped first
            return 
        elif self.canvas.openPlayFile in Demos:
            self.showWorks.enablePlay()
            demo = self.canvas.openPlayFile 
            MsgBox("Can't Save " + demo + " as a Play File", 5)  ## seconds
            return                 
        elif self.canvas.pathMakerOn == True:  ## using load in pathMaker
            self.pathMaker.pathWays.savePath()
            return                   
        elif len(self.scene.items()) == 0:
            MsgBox("Nothing on Screen to Save", 5)
            return     
        self.reallySaveIt()
            
    def reallySaveIt(self):                                    
        dlist = self.updlist()                                                                                 
        if dlist:                    
            try:
                self.showWorks.saveToPlays(dlist)
            except Exception:
                MsgBox('Error saving file...', 5)         
        del dlist
                            
    def updlist(self):
        dlist = []
        for pix in self.scene.items():  ## bag what's left                             
            if pix.type in Types:              ## let 'pivot' thru
                if pix.type == 'pix' and pix.part in ('left','right'): 
                    continue    
                if pix.type == 'frame': 
                    dlist.append(saveFrame(pix))       
                elif pix.type == 'pix':                 
                    dlist.append(savePix(pix))                    
                elif pix.type == 'bkg':    
                    dlist.append(saveBkgnd(pix)) 
                elif pix.type == 'flat': 
                    dlist.append(saveFlat(pix)) 
        return dlist           
   
### ---------------------- dotsShowTime --------------------

    ### --->> optional drop shadow <<-- ###
    # shadow = QGraphicsDropShadowEffect(blurRadius=11, xOffset=8, yOffset=8)
    # pix.setGraphicsEffect(shadow)


