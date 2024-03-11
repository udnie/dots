
import os

from PyQt6.QtCore       import QPointF
from PyQt6.QtGui        import QColor

from dotsShared         import paths

### --------------------- dotsShowFiles --------------------
''' functions fileNotFound, functions used by showbiz to create screen 
    items and functions used by showtime to save screen items '''          
### --------------------------------------------------------
class ShowFiles:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.canvas  = parent
        self.scene   = self.canvas.scene
 
        self.errorOnShadows = False

### -------------------------------------------------------- 
    def fileNotFound(self, tmp):  ## look in the paths set by types - used by dictionaries
        if 'fname' in list(tmp.keys()):  ## just to make sure
            tmp['fileName'] = tmp['fname']                    
        if tmp['type'] == 'bkg' and tmp['fileName'] == 'flat':  ## no file, only stores the color
            tmp['type'] = 'flat'   
        if 'bat' in tmp['fileName'] and not os.path.exists(paths['imagePath'] + \
            tmp['fileName']):
            return True
        elif tmp['type'] == 'frame' and not os.path.exists(paths['spritePath'] + \
            tmp['fileName']):
            return True
        elif tmp['type'] == 'pix' and 'bat' not in tmp['fileName'] and \
            not os.path.exists(paths['spritePath'] + tmp['fileName']):
            return True
        elif tmp['type'] == 'bkg' and not os.path.exists(paths['bkgPath'] + \
            tmp['fileName']):
            return True     
        else:
            return False  ## flats ride free
                               
### --------------------------------------------------------
    ## fills in the blanks and treats shadow as a pix 
    def addPixToScene(self, pix, tmp, z): 
        pix = self.setAll(pix, tmp)  ## sets all shared named variables
        if pix.type == 'frame':  ## nothing to add
            self.scene.addItem(pix)         
                  
        if pix.type == 'flat':
            pix = self.setFlat(pix, tmp) 
            self.scene.addItem(pix) 
        
        if pix.type == 'pix': 
            pix = self.setPixitem(pix, tmp)
            pix.setZValue(z)

        if 'tag' not in tmp.keys():     ## pix and bkg
            tmp['tag'] = ''
        if 'alpha2' not in tmp.keys():  ## for shadows
            tmp['alpha2'] = 1.0     
        if 'locked' not in tmp.keys():  ## pix and bkg
            tmp['locked'] = False     
                    
        pix.tag    = tmp['tag'] 
        pix.alpha2 = tmp['alpha2']
        pix.locked = tmp['locked']  
                                                                
        if pix.type == 'pix' and 'scalor' in tmp.keys():  ## test pix.shadowMaker.isActive when adding to scene
            pix = self.setShadow(pix, tmp)  
                 
        elif pix.type == 'bkg':  ## adding the rest of it
            pix = self.setBackGround(pix, tmp, z)  ## checking if a dupe
            if pix != None:
                self.scene.addItem(pix)     
                if pix.tag == 'scroller':  ## replace transformPix.. action
                    if pix.direction == 'right':
                        pix.setPos(QPointF(pix.runway, 0))  ## offset to right 
                    elif pix.direction == 'vertical':
                        pix.setPos(QPointF(0.0, float(pix.runway)))                             
        del tmp                                                                                            
        ## adds pix to the scene and performs any transforms - used by other classes
        if pix != None and pix.type == 'pix': 
            self.canvas.sideCar.transFormPixItem(pix, pix.rotation, pix.scale, pix.alpha2)
        del pix
               
### --------------------------------------------------------
    def setAll(self, pix, tmp):  ## used by showbiz - sets shared variables                         
        pix.type = tmp['type']           
        if 'frame' in pix.fileName:
            pix.type = 'frame'          
        if 'tag' not in tmp.keys(): 
            tmp['tag'] = ''      
        if 'locked' not in tmp.keys(): 
            tmp['locked'] = False   
           
        if 'x' not in tmp.keys():
            tmp['x'] = 0       
        if 'y' not in tmp.keys():
            tmp['y'] = 0     
        if 'z' not in tmp.keys():
            tmp['z'] = 0 
    
        pix.x    = float('{0:.2f}'.format(tmp['x']))
        pix.y    = float('{0:.2f}'.format(tmp['y']))   
        pix.setZValue(tmp['z']),  ## use the new one
             
        if pix.type not in ('flat', 'frame'):   
            pix.setMirrored(tmp['mirror']),             
       
        if pix.type not in ('bkg', 'flat', 'frame'):   
            pix.rotation = tmp['rotation']
            pix.scale    = tmp['scale']     
        return pix
 
    def setPixitem(self, pix, tmp):
        pix.setZValue(pix.zValue() + 100)  ## not for 'bkg'
        pix.setPos(pix.x, pix.y)  
        pix.locked = tmp['locked']   
        if pix.locked: 
            self.canvas.showbiz.locks += 1  
        if 'frame' not in pix.fileName:
            pix.part = tmp['part']  
        pix = self.canvas.showWorks.lookForStrays(pix)     
        return pix 
      
    def setFlat(self, pix, tmp):
        if 'color' not in tmp.keys(): 
            tmp['color'] = ''          
        if 'tag' not in tmp.keys(): 
            tmp['tag'] = ''      
        if 'locked' not in tmp.keys(): 
            tmp['locked'] = False   
        
        pix.color   = QColor(tmp['color'])
        pix.tag     = QColor(tmp['tag'])
        pix.locked  = tmp['locked']  
        return pix
     
    def setBackGround(self, bkg, tmp, z):  ## pix is a stand_in for bkg
        ## doing this only if missing in .play file otherwise gets the default     
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
   
        bkg.locked      = tmp['locked']                 
        bkg.anime       = tmp['anime']
        bkg.scrollable  = tmp['scrollable']
        bkg.mirroring   = tmp['mirroring']
        bkg.direction   = tmp['direction']
        bkg.factor      = tmp['factor']
        bkg.rate        = tmp['rate']
        bkg.showtime    = tmp['showtime']
             
        result = bkg.bkgWorks.addTracker(bkg)  
        if result == False:  ## must be a dupe
            del bkg         ## not yet added to scene
            return None      
        return bkg ## return to showbiz
    
    def setShadow(self, pix, tmp):  ## read by restore shadows - copies one dictionary to another with some possible changes
        try:
            pix.shadow = {  ## makes any stmp data available after the .play file is read
                'alpha':    tmp['alpha'],
                'scalor':   tmp['scalor'],  ## unique to shadow  - used for a test
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
        except:
            pix.shadow = {} 
            self.errorOnShadows = True               
        return pix
    
### --------------------------------------------------------
    def savePix(self, pix):  ## used by showtime when saving scene items
        p = pix.pos() 
        tmp = {
            'fileName':  os.path.basename(pix.fileName),
            'type':     'pix',
            'x':        float('{0:.2f}'.format(p.x())),
            'y':        float('{0:.2f}'.format(p.y())),
            'z':        pix.zValue(),
            'tag':      pix.tag,
            'locked':   pix.locked,
            'mirror':   pix.flopped,
            'rotation': pix.rotation,
            'scale':    float('{0:.2f}'.format(pix.scale)),
            'alpha2':   float('{0:.2f}'.format(pix.alpha2)), 
            'part':     pix.part,
        }  
   
        if len(pix.shadow) > 0:
            if pix.shadowMaker.isActive == True:
                try:
                    shadow = {
                        'alpha':    float('{0:.2f}'.format(pix.shadowMaker.alpha)),
                        'scalor':   float('{0:.2f}'.format(pix.shadowMaker.scalor)),
                        'rotate':   pix.shadowMaker.rotate,
                        'width':    pix.shadowMaker.width,
                        'height':   pix.shadowMaker.height,
                        'pathX':    [float('{0:.2f}'.format(pix.shadowMaker.path[k].x()))
                                        for k in range(4)],
                        'pathY':    [float('{0:.2f}'.format(pix.shadowMaker.path[k].y()))
                                        for k in range(4)],
                        'flopped':   pix.shadowMaker.flopped,
                        'linked':   pix.shadowMaker.linked,
                    }
                except:       
                    shadow = {}
                    self.errorOnShadows = True   
            else:
                 shadow = pix.shadow   
            tmp.update(shadow)             
        return tmp 

    def saveBkgnd(self, pix):
        p = pix.boundingRect()      
        tmp = {
            'fileName':  os.path.basename(pix.fileName),
            'type':     'bkg',
            'x':        float('{0:.2f}'.format(pix.x)),
            'y':        float('{0:.2f}'.format(pix.y)),
            'z':        pix.zValue(),
            'tag':      pix.tag,
            'locked':   pix.locked,
            'mirror':   pix.flopped,
            'width':    int(p.width()),
            'height':   int(p.height()),
            'scrollable':   pix.scrollable,
            'direction':    pix.direction,
            'mirroring':    pix.mirroring,
            'factor':       pix.factor,
            'rate':         pix.rate,
            'showtime':     pix.showtime,      
        }     
        return tmp

    def saveFrame(pix):       
        tmp = {
            'fileName':  os.path.basename(pix.fileName),
            'type':     'frame',
            'x':        float('{0:.2f}'.format(pix.x)),
            'y':        float('{0:.2f}'.format(pix.y)),
            'z':        pix.zValue(),   
            'tag':      '',
            'locked':   pix.locked,
        }
        return tmp

    def saveFlat(self, pix):       
        tmp = {
            'fileName':  'flat',
            'type':     'flat',
            'x':        float('{0:.2f}'.format(pix.x)),
            'y':        float('{0:.2f}'.format(pix.y)),   
            'z':        pix.zValue(),
            'tag':      pix.color.name(),
            'locked':   pix.locked,
            'color':    pix.color.name(),
        }  
        return tmp
   
### --------------------- dotsShowFiles --------------------   
    
    
    
    
