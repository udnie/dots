  
import os
import json
import random

from PyQt6.QtCore       import QPointF
from PyQt6.QtWidgets    import QFileDialog, QGraphicsPixmapItem

from dotsShared         import common, paths
from dotsSideGig        import MsgBox
from dotsPixFrameWorks  import Frame

### --------------------- dotsShowWorks --------------------
''' functions for scroller cleanup, saving play files, setting play buttons 
    and Lost Files'''                                  
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
  ### --------------------------------------------------------      
    def cleanupMenus(self, showbiz):    
        if showbiz.tableView != None: 
            showbiz.tableView.bye()      
        if showbiz.demoAvailable != None:  
            showbiz.snakes.delSnakes()                     
            showbiz.demoMenu.closeDemoMenu()     
        if showbiz.screenMenu != None:   
            showbiz.screenMenu.closeScreenMenu()
            
### --------------------------------------------------------                                                            
    def dothis(self, p):    
        direction = p.direction
        mirroring = p.mirroring
        factor    = p.factor
        showtime  = p.showtime
        rate      = p.rate
        usethis   = p.useThis
        z = p.zValue()

        p.init()  ## just to make sure
        
        p.tag       = 'scroller'
        p.direction = direction 
        p.mirroring = mirroring
        p.factor    = factor
        p.showtime  = showtime 
        p.rate      = rate
        p.useThis   = usethis
        
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
    def setPauseKey(self):  ## showbiz all the way down    
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
    
### --------------------------------------------------------
    def addFrame(self, frame):  ## it's a handoff 
        frame = Frame(frame, self.canvas, self.canvas.mapper.toFront(1))
        self.scene.addItem(frame)
    
    def deleteFrame(self, frame):
        self.scene.removeItem(frame)
        frame = None    
          
### -------------------------------------------------------- 
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
        self.canvas.dots.statusBar.showMessage('') 
                    
### --------------------------------------------------------
    def lookForStrays(self, pix):  ## it can happen
        if pix.x < -25 or pix.x > common['ViewW'] -10:
            pix.setPos(float(random.randint(25, 100) * 2.5), pix.y)      
        if pix.y < -25 or pix.y > common['ViewH']-10:
            pix.setPos(pix.x, random.randint(25, 100) * 1.5) 
        return pix
     
### --------------------------------------------------------
class LostFiles:  ## not used <<<---------------
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.canvas = parent
        self.scene  = self.canvas.scene
 
 ### --------------------------------------------------------
    def writeMissingFiles(self, rows):
        file = self.maketmp()
        print('write', file, len(rows))
        try:
            with open(file, 'w') as fp:
                json.dump(rows, fp)
        except IOError:
            MsgBox('writeMissingFiles: Error writing file', 5)
            return
 
    def returnMissingFiles(self):  ## if there's a tmp file
        file = self.maketmp()
        if os.path.exists(file): 
            print('return', file) 
            try:
                with open(file, 'r') as fp: 
                    rows = json.load(fp)   
            except IOError:
                MsgBox('returnMissingFiles: Error reading file', 5)
                return None       
            return rows  ## as a json file
 
    def lookForDupes(self, rows, dlist):
        for tmp in dlist:
            for row in rows:
                if tmp['fileName'] == row['fileName'] and tmp['z'] == row['z']:
                    rows.remove(row)   
                    break
        if len(rows) == 0:
            self.deletetmp()
        else:
            for row in rows:  ## still missing and not in dlist
                dlist.append(row)
        dlist = sorted(dlist, key=lambda x: x['fileName'], reverse=True) 
        return dlist    
 
    def deleteSelectedFiles(self, selected):  ## get started
        file = self.maketmp() 
        if rows := self.returnMissingFiles(file):
            self.removeMissingFiles(file, selected, rows)                            

    def removeMissingFiles(self, file, selected, rows):  ## delete selected files
        print('remove', file) 
        for s in selected:
            for tmp in rows:
                print('remove', tmp['fileName'], tmp['z'])
                if s[0] == tmp['fileName'] and s[1] == tmp['z']:
                    rows.remove(tmp)    
        print('nrows', len(rows)) 
        self.deletetmp()       
        if len(rows) > 0:
            self.writeMissingFiles(file, rows)
    
    def hastmp(self):
        return os.path.exists(self.maketmp()) 
 
    def maketmp(self):
        file = os.path.basename(self.canvas.openPlayFile)
        return paths['playPath'] + file[:file.index('.')] + '.tmp'
         
    def deletetmp(self):
        if self.hastmp():  
            file = self.maketmp()
            print('deleting', file)
            try:
                os.remove(file)     
            except IOError:
                MsgBox('MissingFiles: Error deleting tmp file', 5)
                return  
                    
### ---------------------- dotsShowWorks -------------------




