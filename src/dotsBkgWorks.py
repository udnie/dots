
import os.path
import math
import json

from PyQt6.QtCore       import Qt, QPoint, QTimer
                        
from dotsShared         import common, paths
from dotsSideGig        import MsgBox
from dotsBkgMatte       import Matte
from dotsBkgScrollWrks  import Tracker, BkgScrollWrks

### --------------------- dotsBkgWorks --------------------- 
''' classes: BkgWorks -- mostly scrolling'''    
# ### -------------------------------------------------------- 
class BkgWorks:  
### --------------------------------------------------------
    def __init__(self, parent):  
        super().__init__()

        self.bkgItem  = parent     
        self.canvas   = self.bkgItem.canvas
        self.bkgMaker = self.bkgItem.bkgMaker
        self.dots     = self.bkgItem.dots
        
        self.bkgScrollWrks = BkgScrollWrks(self.bkgItem)
        
### -------------------------------------------------------- 
    ## when loading a play file or adding from the screen - Tracker is in dotsBkgScrollWrks
    def addTracker(self, bkg): 
        bkg.fileName = bkg.path + os.path.basename(bkg.fileName) 
        file = os.path.basename(bkg.fileName) 
        
        ## bkg.factor is set to 1.0  ## default - if it's running slow - lower it to .85 in bkgItem 
        ## if randomizing speed factor do this 

        # fact = float((random.randint(17,30) *5)/100)  ## .85-1.50
        # bkg.factor = fact  ## if using a random screen speed factor 
    
        if len(self.bkgMaker.trackers) == 0:
            x = Tracker(file, bkg)
            self.bkgMaker.trackers.append(x)
            return True
        else:
            k = 0
            for p in self.bkgMaker.trackers:  ## see if it's already there
                if p.file == file:
                    k += 1
            if k == 0:  ## no others found - add it 
                # x = Tracker(file, bkg)
                self.bkgMaker.trackers.append(Tracker(file, bkg)) 
                return True
            else:
                return False  ## must be a duplicate, skip processing 
                    
    def delTracker(self, bkg):
        file = os.path.basename(bkg.fileName)  
        for item in self.bkgMaker.trackers:  ## see if it's already there
            if item.file == file:  
                self.bkgMaker.trackers.remove(item)
                break
                         
### --------------------------------------------------------                                                                                
    def setDirection(self, key):  ## from keybooard or widget - sets 'first'    
        if math.fabs(self.bkgItem.runway) < self.bkgItem.showtime:
            self.bkgScrollWrks.notScrollable()   
            return     
        if self.bkgItem.scrollable:  ## only place where scroller is set except demos 
            if self.dots.Vertical:   ## no direction equals 'not scrollable'
                self.bkgItem.direction = 'vertical'
            else:
                self.bkgItem.direction = key
            self.bkgItem.tag = 'scroller'    
            self.bkgItem.rate = 0
            file = os.path.basename(self.bkgItem.fileName)          
            for p in self.bkgMaker.trackers:
                if p.file == file:
                    p.direction = self.bkgItem.direction 
                    self.bkgItem.showtime = self.bkgScrollWrks.setShowTime()
                    p.showtime  = self.bkgItem.showtime
                    self.bkgItem.rate = self.getScreenRate()  ## blank it's first
                    p.rate      = self.bkgItem.rate
                    p.useThis   = self.bkgItem.useThis
                    break 
                
            # print(f'direction {file}\t{p.direction}\t{p.mirroring}\t{p.rate}\t{p.factor}')
            if p.rate == 0 and self.bkgItem.useThis == '':
                return
            
            self.bkgMaker.lockBkg(self.bkgItem) 
            if self.bkgMaker.widget != None:
                self.bkgMaker.updateWidget()      
                QTimer.singleShot(200, self.bkgItem.bkgMaker.resetSliders)
                                                  
### --------------------------------------------------------  
    ## reads twice - returns 'next' rate first, returns 'first' rate next 
    def getScreenRate(self, which =''): 
        rate = self.getThisRate(self.bkgItem)  
        if rate == 0:
            MsgBox(f'Error Loading Screen Rates File {self.bkgItem.useThis}', 5)
            self.bkgItem.useThis = ''
            self.bkgMaker.screenrate = {}
            return 0        
        if which == 'first':
            rate = rate[0]        
        elif self.bkgItem.rate == 0:  ## needs to be 0
            if self.bkgItem.direction == 'right':
                rate = rate[2]
            else:
                rate = rate[1]      
            self.bkgItem.rate = rate 
            self.bkgScrollWrks.setTrackerRate()  ## a useful addition
        return rate
    
### --------------------------------------------------------
    def getThisRate(self, bkg):
        bkg.useThis == '' 
        if common['Screen']  == '1080' and bkg.width  < 1280 or \
            common['Screen'] == '1215' and bkg.width  < 1440 or \
            common['Screen'] == '1296' and bkg.width  < 1536 or \
            common['Screen'] ==  '900' and bkg.height < 1102:  ##dd in this case 2:3  
            bkg.useThis = 'moretimes'  ## selecting which dictionary to use     
        else:
            bkg.useThis = 'screentimes'             
        try:  
            with open(paths['playPath'] +  "screenrates.dict", 'r') as fp:
                self.bkgMaker.screenrate = json.load(fp)  
            return self.bkgMaker.screenrate[bkg.useThis][common['Screen']]        
        except:
            return 0
        
### --------------------------------------------------------
    ## rate times screen long side = milliseconds needed to clear the scene end to end
    def setNextPath(self, path, bkg):  
        fact = bkg.factor      
        if bkg.direction == 'left':   
            path.setDuration(int(common['ViewW'] * (bkg.rate*fact)))    
            path.setStartValue(QPoint(common['ViewW'], 0))
            path.setEndValue(QPoint(int(-bkg.width), 0))
        elif bkg.direction == 'right':
            path.setDuration(int(common['ViewW'] * (bkg.rate*fact)))  
            path.setStartValue(QPoint(-bkg.width, 0))
            path.setEndValue(QPoint(int(common['ViewW']), 0))
        elif bkg.direction == 'vertical':
            path.setDuration(int(common['ViewH'] * (bkg.rate*fact))) 
            ## current kludge advances background into scene before starting - verticals seem to take longer to start
            path.setStartValue(QPoint(0, common['ViewH']-int(bkg.showtime*.75)))
            path.setEndValue(QPoint(0, -bkg.height))
        return path
           
    def setFirstPath(self, path, bkg):       
        fact = bkg.factor  
        if bkg.direction == 'left':
            path.setDuration(int(common['ViewW'] * (bkg.rate*fact))) 
            path.setStartValue(QPoint(0,0)) 
            path.setEndValue(QPoint(-int(bkg.width), 0))
        elif bkg.direction == 'right':
            path.setDuration(int(common['ViewW'] * (bkg.rate*fact)))
            path.setStartValue(QPoint(bkg.runway, 0))
            path.setEndValue(QPoint(int(common['ViewW']), 0))
        elif bkg.direction == 'vertical':   
            path.setDuration(int(common['ViewH'] * (bkg.rate*fact)))  ## rate time equals time to clear   
            path.setStartValue(QPoint(0, bkg.runway))
            path.setEndValue(QPoint(0, -bkg.height)) 
        return path
                
### -------------------------------------------------------- 
    def centerBkg(self):
        if self.bkgItem != None and self.bkgItem.type == 'bkg':  
            width = self.bkgItem.imgFile.width()
            height = self.bkgItem.imgFile.height()
            self.bkgItem.x = (common['ViewW']- width)/2
            self.bkgItem.y = (common['ViewH']- height)/2
            self.bkgItem.setPos(self.bkgItem.x, self.bkgItem.y) 

    def setMirroring(self):
        if self.bkgItem.scrollable:                                  
            if self.bkgItem.mirroring == True: 
                self.bkgItem.mirroring = False ## continuous
            else:
                self.bkgItem.mirroring = True  ## mirrored                               
        file = os.path.basename(self.bkgItem.fileName)  
        for p in self.bkgMaker.trackers:
            if p.file == file:
                p.mirroring = self.bkgItem.mirroring   
                break                                     
        self.bkgMaker.setMirrorBtnText() 
         
    def setMatte(self):
        self.bkgMaker.closeWidget()
        self.bkgMaker.matte = Matte(self.canvas)
        
### -------------------------------------------------------- 
    ## returns what gets lost on each reincarnation
    def restoreFromTrackers(self, bkg, where=''): 
        file = os.path.basename(bkg.fileName)  ## opposite of setMirroring
        for p in self.bkgMaker.trackers:
            if p.file == file:
                bkg.mirroring = p.mirroring   
                bkg.direction = p.direction 
                bkg.factor    = p.factor
                bkg.showtime  = p.showtime
                bkg.useThis   = p.useThis
                bkg.rate      = p.rate
                break
             
### --------------------------------------------------------                                                                                      
    def reset(self):  ## reset both tracker and bkgItem
        file = os.path.basename(self.bkgItem.fileName)  ## opposite of setMirroring
        for p in self.bkgMaker.trackers:
            if p.file == file:
                p.direction = ''
                p.mirroring = self.bkgMaker.mirroring
                p.factor    = self.bkgMaker.factor
                p.showtime  = 0
                p.useThis   = ''
                p.rate      = 0
                break      
        self.bkgItem.tag = ''   
        self.bkgItem.direction = ''             
        self.bkgItem.mirroring = self.bkgMaker.mirroring  
        self.bkgItem.factor    = self.bkgMaker.factor
        self.bkgItem.rate      = 0
        self.bkgItem.showtime  = 0
        self.bkgItem.useThis   = ''
        self.bkgItem.rate      = 0
        self.bkgMaker.addWidget(self.bkgItem)
                                                                    
### --------------------------------------------------------                     
    def setWidthHeight(self, img):     
        if img == None:
            return   
        imf = img.scaledToHeight(self.bkgItem.ViewH, Qt.TransformationMode.SmoothTransformation) 
        if imf.width() > self.bkgItem.ViewW:  ## its scrollable enough
            self.bkgItem.imgFile = imf
            self.bkgItem.scrollable = True               
        else:   
            try:
                self.bkgItem.imgFile = img.scaled(  ## fill to width or height
                    self.bkgItem.ViewW, 
                    self.bkgItem.ViewH,
                    Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            except:
                del img
                del imf
                 
    def setVertical(self, img):  
        if img == None:
            return
        imf = img.scaledToWidth(self.bkgItem.ViewW, Qt.TransformationMode.SmoothTransformation)
        self.bkgItem.imgFile = imf       
        if imf.height() > self.bkgItem.ViewH:  ## its scrollable enough
            self.bkgItem.scrollable = True  
        del img 
        del imf
                                                                                                    
### --------------------- dotsBkgWorks ---------------------


        
        