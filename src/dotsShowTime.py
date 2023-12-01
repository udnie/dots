
from os import path

import gc

from PyQt6.QtCore       import QAbstractAnimation
from PyQt6.QtWidgets    import QGraphicsPolygonItem, QGraphicsPixmapItem

from dotsSideGig        import *
from dotsSideCar        import SideCar
from dotsSideWorks      import SideWorks

Demos = ['snakes', 'bats', 'abstract']

### ---------------------- dotsShowTime --------------------
''' class: ShowTime: functions to run, pause, stop, etc.. .play animations'''        
### --------------------------------------------------------
class ShowTime:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas   = parent
        self.scene    = self.canvas.scene
        self.dots     = self.canvas.dots
        self.mapper   = self.canvas.mapper
        
        self.sideCar   = SideCar(self.canvas)  ## additional extentions
        self.sideWorks = SideWorks(self.canvas)
    
        self.animation = self.canvas.animation
        self.pathMaker = self.canvas.pathMaker
        
### --------------------------------------------------------        
    def run(self):  ## runs whatever is in scene that can be animated
        if self.canvas.control != '':
            return  
    
        self.mapper.clearMap()
        self.clearPathsandTags()  
        self.canvas.unSelect()
        self.sideCar.hideOutlines()
                       
        if not self.canvas.pathList:  ## should already exist - moved from animations
            self.canvas.pathList = getPathList(True)  
              
        b, k = 0, 0  ## counts bats and pixitems
        for pix in self.scene.items():  ## sets the animation and run it <<----
            
            if type(pix) == 'dotsShadowWidget.PointItem':  ## goes with shadows for now
                continue
            if isinstance(pix, QGraphicsPolygonItem):
                continue
          
            if pix.type in ('pix', 'bkg') and pix.tag:    
                ## if random, slice to length, display actual anime if paused 
                if 'Random' in pix.tag:
                    pix.tag = pix.tag[0:len('Random')]
                if 'frame' in pix.fileName:
                    pix.tag = 'idle' 
                                 
                ## set the animation using the tag
                if pix.type == 'pix':
                    pix.anime = self.animation.setAnimation(          
                        pix.tag, 
                        pix)        
                elif pix.type == 'bkg': 
                    if pix.tag == 'scroller':                
                        pix.anime = pix.setScrollerPath(pix, 'first')  ## in bkgItem 
                        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)
                    if pix.locked:
                        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable,False) 
                                    
                k += 1  ## k = number of pixitems - bats count as three
                if pix.anime == None:  ## not animated
                    continue
                else:  ## staggering the start 
                    QTimer.singleShot(100 + (k * 35), pix.anime.start)  #   
                    
                ### --->> optional drop shadow <<-- ###
                # shadow = QGraphicsDropShadowEffect(blurRadius=11, xOffset=8, yOffset=8)
                # pix.setGraphicsEffect(shadow)

        if k > 0:
            self.sideWorks.disablePlay()  ## sets pause/resume/stop
            file = os.path.basename(self.canvas.openPlayFile)
            if "play" in file:
                self.dots.statusBar.showMessage(file + ' - ' + 'Number of Pixitems: {}'.format(k))  
                
### --------------------------------------------------------                                 
    def pause(self):
        self.clearPathsandTags()  
        if self.canvas.control == 'resume':
           self.resume()
        else:          
            for pix in self.scene.items():          
                if type(pix) == 'dotsShadowWidget.PointItem':
                    continue
                if isinstance(pix, QGraphicsPolygonItem):
                    continue         
                if pix.type in ('bkg', 'pix') and pix.fileName in ('frame','flat'):
                    continue               
                if pix.type in ('pix', 'snake', 'bkg'):
                    if pix.anime != None and pix.anime.state() == QAbstractAnimation.State.Running:  ## running
                        pix.anime.pause() 
            self.sideWorks.setPauseKey()

    def resume(self):   
        for pix in self.scene.items():   
            if type(pix) == 'dotsShadowWidget.PointItem':
                continue
            if isinstance(pix, QGraphicsPolygonItem):
                continue 
            try:  ## the CAT bug likes this line sometimes
                if pix.type in ('bkg', 'pix') and pix.fileName in ('frame','flat'):
                    continue   
            except:
                continue  
            if pix.type in ('pix', 'snake', 'bkg'):
                if pix.anime != None and pix.anime.state() == QAbstractAnimation.State.Paused:
                    pix.anime.resume()                   
        self.sideWorks.setPauseKey()
        
### --------------------------------------------------------
    def stop(self, action=''):  ## action used by clear 
        self.clearPathsandTags()     
        scrolling = []  ## None doesn't work on lists - use len()
        
        for pix in self.scene.items():                      
            if type(pix) == 'point':  ## shadows pointItem
                continue           
            if isinstance(pix, QGraphicsPolygonItem):  ## shadows
                continue              
            try:
                if pix.fileName in ('frame','flat'):
                    continue       
            except:
                continue
            
            if pix.type in ('pix', 'snake', 'bkg'):                   
                if pix.anime != None and pix.anime.state() != QAbstractAnimation.State.Stopped:       
                    pix.anime.stop()                   
                    
                    # if pix.type == 'bkg':      
                    #     print(f'stop  {os.path.basename(pix.fileName)}\t{pix.direction}\t{pix.mirroring}\t{pix.factor}')
                    
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
                            
        if len(scrolling) > 0:
            self.sideWorks.cleanUpScrollers(self.canvas.scene)
        self.sideWorks.enablePlay() 
        self.canvas.btnPause.setText( 'Pause' )
        del scrolling  
                      
### --------------------------------------------------------
    def savePlay(self):   
        if self.canvas.openPlayFile in Demos:
            self.sideWorks.enablePlay()
            demo = self.canvas.openPlayFile 
            MsgBox("Can't Save " + demo.capitalize() + " as a Play File", 6)  ## seconds
            return                 
        if self.canvas.pathMakerOn:  ## using load in pathMaker
            self.pathMaker.pathWays.savePath()
            return                
        elif len(self.scene.items()) == 0:
            return         
        self.reallySaveIt()
            
    def reallySaveIt(self):      
        dlist = [] 
        for pix in self.scene.items():          
            if pix.type in ('pix','bkg'): 
                if pix.fileName != 'flat' and \
                    not path.exists(pix.fileName):  ## note
                    continue  
                     
                elif pix.type == 'pix':   
                    if pix.part in ('left','right'):  ## let pivot thru
                        continue                  
                    dlist.append(savePix(pix)) 
                               
                elif pix.type == 'bkg':
                    if pix.fileName != 'flat':       
                        dlist.append(saveBkg(pix)) 
                    else:
                        dlist.append(saveFlat(pix))            
        if dlist:
            try:
                self.sideWorks.saveToPlays(dlist)
            except Exception:
                MsgBox('Error saving file...', 5)         
        del dlist
                     
    def clearPathsandTags(self):
        self.mapper.clearTagGroup()
        self.mapper.clearPaths()  ## clears tags as well

### --------------------------------------------------------
def savePix(pix): 
    p = pix.pos() 
    tmp = {
        'fname':    os.path.basename(pix.fileName),
        'type':    'pix',
        'x':        float('{0:.2f}'.format(p.x())),
        'y':        float('{0:.2f}'.format(p.y())),
        'z':        pix.zValue(),
        'mirror':   pix.flopped,
        'rotation': pix.rotation,
        'scale':    float('{0:.2f}'.format(pix.scale)),
        'tag':      pix.tag,
        'alpha2':   float('{0:.2f}'.format(pix.alpha2)), 
        'locked':   pix.locked,
        'part':     pix.part,
    }  
    
    if pix.shadow != None:   
        shadow = {
            'alpha':    float('{0:.2f}'.format(pix.shadowMaker.alpha)),
            'scalor':   float('{0:.2f}'.format(pix.shadowMaker.scalor)),
            'rotate':   pix.shadowMaker.rotate,
            'width':    pix.shadowMaker.imgSize[0],
            'height':   pix.shadowMaker.imgSize[1],
            'pathX':    [float('{0:.2f}'.format(pix.shadowMaker.path[k].x()))
                            for k in range(4)],
            'pathY':    [float('{0:.2f}'.format(pix.shadowMaker.path[k].y()))
                            for k in range(4)],
            'flopped':   pix.shadowMaker.flopped,
            'linked':   pix.shadowMaker.linked,
        }
        tmp.update(shadow)
          
    return tmp 

def saveBkg(pix):
    p = pix.boundingRect() 
    tmp = {
        'fname':    os.path.basename(pix.fileName),
        'type':    'bkg',
        'x':        float('{0:.2f}'.format(pix.x)),
        'y':        float('{0:.2f}'.format(pix.y)),
        'z':        pix.zValue(),
        'mirror':   pix.flopped,
        'locked':   pix.locked,
        'rotation': pix.rotation,
        'scale':    float('{0:.2f}'.format(pix.scale)),
        'opacity':  float('{0:.2f}'.format(pix.opacity)),
        'width':    int(p.width()),
        'height':   int(p.height()),
        'tag':      pix.tag,
        'scrollable':   pix.scrollable,
        'direction':    pix.direction,
        'mirroring':    pix.mirroring,
        'factor':       pix.factor,
    }  
      
    return tmp

def saveFlat(pix):
    tmp = {
        'fname': 'flat',
        'type':  'bkg',
        'z':      pix.zValue(),
        'tag':    pix.color.name(),
        'color':  pix.color.name(),
    }
    
    return tmp

### ---------------------- dotsShowTime --------------------


