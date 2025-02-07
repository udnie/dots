
from os import path

from PyQt6.QtCore       import QAbstractAnimation
from PyQt6.QtWidgets    import QGraphicsPolygonItem, QGraphicsPixmapItem

from dotsSideGig        import *
from dotsShowFiles      import ShowFiles
from dotsShowWorks      import ShowWorks
from dotsShared         import ControlKeys
from dotsAnimation      import Animation
from dotsTableModel     import Types

Demos = ['snakes', 'bats', 'hats']

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

        self.showWorks = ShowWorks(self.canvas)
        self.showFiles = ShowFiles(self.canvas) 
        self.animation = Animation(self.canvas)
        
        self.pathMaker = self.canvas.pathMaker
     
### --------------------------------------------------------        
    def run(self):  ## runs whatever is in scene that can be animated
        if self.canvas.control != '':
            return  
        
        self.mapper.clearMap()
        self.mapper.clearPathsandTags()  
        self.canvas.sideCar2.unSelect()
        self.canvas.sideCar.hideOutlines()
                      
        if self.canvas.showbiz.tableView != None:
            if self.canvas.showbiz.tableView != None:
                self.canvas.showbiz.tableView.bye()    
                               
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
            self.canvas.animation = True
            
        if self.canvas.videoPlayer != None: 
            self.canvas.videoPlayer.playVideo()
            if k == 0: self.showWorks.disablePlay()
                
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
            if self.canvas.videoPlayer != None:
                self.canvas.videoPlayer.playVideo()  ## toggles pause and play
            
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
        if self.canvas.videoPlayer != None:  ## toggles pause and play
            self.canvas.videoPlayer.playVideo()
        
### --------------------------------------------------------
    def stop(self, action=''):  ## action used by clear               
        self.mapper.clearPathsandTags()     
        scrolling = []  ## used by tracker to remove the 'next' bkg 
        
        if self.canvas.videoPlayer != None:
            self.canvas.videoPlayer.stopVideo()
            
        self.canvas.control = ''
            
        for pix in self.scene.items():                          
            if type(pix) == 'dotsShadowWidget.PointItem' or \
                isinstance(pix, QGraphicsPolygonItem):
                continue              
            try:
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
                    if self.canvas.openPlayFile != 'hats':            
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
            
        self.canvas.animation = False
        self.showWorks.enablePlay() 
        self.canvas.btnPause.setText( 'Pause' )
        del scrolling  
                  
### --------------------------------------------------------
    def savePlay(self):   
        if self.canvas.control in ControlKeys:  ## there's an animation running - needs to be stopped first
            return 
        if self.canvas.openPlayFile in Demos:
            self.showWorks.enablePlay()
            demo = self.canvas.openPlayFile 
            MsgBox("Can't Save " + demo + " as a Play File", 5)  ## seconds
            return                 
        if self.canvas.pathMakerOn == True:  ## using load in pathMaker
            self.pathMaker.pathWays.savePath()
            return                   
        if len(self.scene.items()) == 0:
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
        if self.showFiles.errorOnShadows == True:
            MsgBox('Error on Saving Some Shadows...', 5)
                            
    def updlist(self):
        dlist = []
        for pix in self.scene.items():  ## bag what's left     
            if pix.type in Types:  ## let 'pivot' thru
                if pix.type == 'pix' and pix.part in ('left','right'): 
                    continue    
                if pix.type == 'frame': 
                    dlist.append(self.showFiles.saveFrame(pix))       
                elif pix.type == 'pix':                 
                    dlist.append(self.showFiles.savePix(pix))                    
                elif pix.type == 'bkg':    
                    dlist.append(self.showFiles.saveBkgnd(pix)) 
                elif pix.type == 'flat': 
                    dlist.append(self.showFiles.saveFlat(pix))
                elif pix.type == 'video' and self.canvas.videoPlayer != None:
                    dlist.append(self.canvas.videoPlayer.saveVideo())
        return dlist           

### ---------------------- dotsShowTime --------------------

    ### --->> optional drop shadow <<-- ###
    # shadow = QGraphicsDropShadowEffect(blurRadius=11, xOffset=8, yOffset=8)
    # pix.setGraphicsEffect(shadow)


