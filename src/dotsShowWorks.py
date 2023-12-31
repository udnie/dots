
import os 
import json
import random

from PyQt6.QtCore       import QPointF
from PyQt6.QtWidgets    import QFileDialog, QGraphicsPixmapItem

from dotsShared         import common, paths
from dotsSideGig        import MsgBox

### --------------------- dotsShowWorks --------------------
'''  ## saving to a play file from showtime and setting play buttons '''
### --------------------------------------------------------
class ShowWorks: 
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()

        self.canvas = parent
        self.scene  = self.canvas.scene
  
### --------------------------------------------------------  
    def cleanUpScrollers(self, scene):  ## called from showtime  
        self.scene = scene
        for t in self.canvas.bkgMaker.trackers:
            tracker = t.file  
            k = 0 
            for p in self.scene.items():  ## delete duplicates
                if p.type == 'bkg' and tracker in p.fileName: 
                    if p.tag == 'scroller' and p.direction == t.direction:
                        if k == 0:
                            self.dothis(p) 
                            k = 1
                        elif k > 0:
                            self.scene.removeItem(p)
                                                                
    def dothis(self, p):    
        direction = p.direction
        mirroring = p.mirroring
        factor    = p.factor
        showtime  = p.showtime
        rate      = p.rate
        z = p.zValue()

        p.init()
        p.tag = 'scroller'
        p.direction = direction 
        p.mirroring = mirroring
        p.factor    = factor
        p.showtime  = showtime 
        p.rate      = rate
        
        p.setZValue(z)   
        p.locked == True
        p.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)          

        if p.direction == 'right':
            p.setPos(QPointF(p.runway, 0)) 
        elif p.direction == 'left':      
            p.setPos(QPointF())  
        elif p.direction == 'vertical':
            p.setPos(QPointF(0.0, float(p.runway)))
   
### --------------------------------------------------------      
    def setPauseKey(self):  ## sideShow all the way down    
        if self.canvas.control == 'pause': 
            self.canvas.btnPause.setText( 'Resume' );
            self.canvas.control = 'resume'
        elif self.canvas.control == 'resume':
            self.canvas.btnPause.setText( 'Pause' );
            self.canvas.control = 'pause'

    def enablePlay(self):
        self.canvas.control = ''
        self.canvas.btnRun.setEnabled(True)
        self.canvas.btnPause.setEnabled(False)
        self.canvas.btnStop.setEnabled(False) 
        self.canvas.btnSave.setEnabled(True) 
 
    def disablePlay(self):
        self.canvas.control = 'pause'
        self.canvas.btnRun.setEnabled(False)
        self.canvas.btnPause.setEnabled(True)
        self.canvas.btnStop.setEnabled(True)  
        self.canvas.btnSave.setEnabled(False)  

    def saveToPlays(self, dlist):     
        if self.canvas.openPlayFile == '':
            self.canvas.openPlayFile = paths['playPath'] + 'tmp.play'       
        Q = QFileDialog()        
        Q.Option.DontUseNativeDialog    
        Q.setDirectory(paths['playPath'])
        f = Q.getSaveFileName(self.canvas, paths['playPath'],  
            self.canvas.openPlayFile)
        Q.accept()
        if not f[0]: 
            return
        if not f[0].lower().endswith('.play'):
            MsgBox("saveToPlays: Wrong file extention - use '.play'", 5)  
            return
        else:
            try:
                with open(f[0], 'w') as fp:
                    json.dump(dlist, fp)
            except IOError:
                MsgBox('saveToPlays: Error saving file', 5)
        del dlist
     
  ### --------------------------------------------------------
    def setAll(self, pix, tmp):  ## from a play file
        pix.type = tmp['type']                 
        pix.x    = float('{0:.2f}'.format(tmp['x']))
        pix.y    = float('{0:.2f}'.format(tmp['y']))   
        pix.setZValue(tmp['z']),  ## use the new one
        pix.setMirrored(tmp['mirror']),
        if pix.fileName == 'flat':
            pix.type = 'flat'
        elif pix.type != 'bkg':   
            pix.rotation = tmp['rotation']
            pix.scale    = tmp['scale']
        return pix

    def setPixitem(self, pix, tmp):
        pix.setZValue(pix.zValue() + 100)  ## not for 'bkg'
        pix.setPos(pix.x, pix.y)     
        if 'frame' not in pix.fileName:
            pix.locked = tmp['locked']
            if pix.locked: self.canvas.sideShow.locks += 1
            pix.part = tmp['part']
            pix = lookForStrays(pix)
        return pix 
     
    def setBackGround(self, pix, tmp):  ## pix is a stand_in for bkg
        ## doing this only if missing in .play file other gets the default     
        if 'anime' not in tmp.keys(): 
            tmp['anime'] = None   
        
        if 'scrollable' not in tmp.keys(): 
            tmp['scrollable'] = False
            
        if 'direction' not in tmp.keys(): 
            tmp['direction'] = 'left'   
                 
        if 'mirroring' not in tmp.keys(): 
            tmp['mirroring'] = self.canvas.bkgMaker.mirroring    
            
        if 'factor' not in tmp.keys(): 
            tmp['factor'] = self.canvas.bkgMaker.factor
                    
        if 'rate' not in tmp.keys(): 
            tmp['rate'] = 0
  
        if 'showtime' not in tmp.keys(): 
            tmp['showtime'] = 0
  
        pix.locked      = tmp['locked']                 
        pix.anime       = tmp['anime']
        pix.scrollable  = tmp['scrollable']
        pix.mirroring   = tmp['mirroring']
        pix.direction   = tmp['direction']
        pix.factor      = tmp['factor']
        pix.rate        = tmp['rate']
        pix.showtime    = tmp['showtime']
             
        result = pix.bkgWorks.addTracker(pix)    
        if result == False:  ## must be a dupe
            del pix          ## not yet added to scene
            return None
           
        return pix  ## return to sideShow
    
    def setShadow(self, pix, tmp):
        pix.shadow = {
            'alpha':    tmp['alpha'],
            'scalor':   tmp['scalor'],  ## unique to shadow
            'rotate':   tmp['rotate'],
            'width':    tmp['width'],
            'height':   tmp['height'],
            'pathX':    tmp['pathX'],
            'pathY':    tmp['pathY'],  
        }   
                        
        if 'flopped' not in tmp.keys():      
            pix.shadow['flopped'] = None
        else:
            pix.shadow['flopped'] = tmp['flopped']
        if 'fileName' not in tmp.keys(): 
            pix.shadow['fileName'] = 'shadow' 
        if 'linked' not in tmp.keys(): 
            pix.shadow['linked'] = False
        else:
            pix.shadow['linked'] = tmp['linked']
                       
        return pix
            
### --------------------------------------------------------
def lookForStrays(pix):  ## it can happen
    if pix.x < -25 or pix.x > common['ViewW'] -10:
        pix.setPos(float(random.randint(25, 100) * 2.5), pix.y)      
    if pix.y < -25 or pix.y > common['ViewH']-10:
        pix.setPos(pix.x, random.randint(25, 100) * 1.5) 
    return pix
     
### ---------------------- dotsShowWorks -------------------


