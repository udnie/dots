
import os
import os.path
import random


from PyQt6.QtCore       import QAbstractAnimation, Qt, QPointF, QPoint, QSize, QRect
from PyQt6.QtGui        import QPen, QColor
from PyQt6.QtWidgets    import QFileDialog, QGraphicsItemGroup, QGraphicsLineItem, \
                                QApplication
                                                    
from dotsShared         import common, paths
from dotsPixItem        import PixItem
from dotsSideGig        import MsgBox, constrain
from dotsMapMaker       import MapMaker

### ---------------------- dotsSideCar ---------------------
''' no class: just stuff - pixTest, transFormPixitem, snapShot, toggleGrid, 
    assorted small functions and a few from sideShow '''   
### --------------------------------------------------------
class SideCar:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.dots   = self.canvas.dots
        self.scene  = self.canvas.scene
        self.mapper = MapMaker(self.canvas)
                  
        self.gridZ     = common['gridZ']    
        self.gridGroup = None  
        self.menu      = None 
     
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
    def pixTest(self):
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
    def snapShot(self):  ## screen capture
        if self.hasBackGround() or self.scene.items():
            self.canvas.unSelect()  ## turn off any select borders
            if self.canvas.pathMakerOn == False:
                if self.canvas.mapper.isMapSet():
                    self.canvas.mapper.removeMap()
                    
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
  
### --------------------------------------------------------
    def clearWidgets(self):                             
        for widget in QApplication.allWidgets():  ## note!!
            if widget.accessibleName() == 'widget':  ## shadow and pixitems widgets
                widget.close()
        if self.canvas.pathMakerOn: self.canvas.pathMaker.pathChooserOff()
  
    def hasBackGround(self):
        for itm in self.scene.items(Qt.SortOrder.AscendingOrder):
            if itm.type == 'bkg':
                return True
        return False
                                                                                                                        
    def pause(self):
        self.canvas.showtime.pause()
    
    def pageDown(self, key):  ## for sprite scrollPanel
        self.canvas.scroll.pageDown(key)
      
    def snapTag(self):
        return str(random.randrange(1000,9999)) + chr(random.randrange(65,90))
      
    def dumpBkgs(self):  ## shift-B 
        for p in self.scene.items():
            if p.type == 'bkg':
                file, direction, mirror, locked = self.addBkgLabels(p)
                showtime = p.showtime
                print( f'{file}\t{direction}\t{mirror}\t{locked}\t{p.zValue()}\t{p.rate}\t{showtime}\t{p.factor}')
        print()
          
    def addBkgLabels(self, bkg): 
        file = os.path.basename(bkg.fileName)        
        if bkg.locked == True:
            locked = 'Locked' 
        else:
            locked = 'UnLocked' 
        if bkg.direction == 'left':
            direction = 'Left'
        elif bkg.direction == 'right': 
            direction = 'Right'     
        elif self.dots.Vertical:
            direction = 'Vertical'
        else:
            for item in self.canvas.bkgMaker.trackers:  ## see if it's already there
                if item.file == file:  
                    direction = item.direction
                    break
            if direction == '':
                direction = 'NoDirection'
        if bkg.mirroring == False:
            mirror = 'Continuous'
        elif bkg.mirroring == True:
            mirror = 'Mirrored'
        if bkg.scrollable == False:
            mirror = 'Not Scrollable'    
        return file.capitalize(), direction, mirror, locked
  
### --------------------------------------------------------
    def toggleMenu(self):
        self.canvas.keysPanel.toggleMenu()  ## no direct path from controlView
  
    def toggleOutlines(self):  ## runs from O as in Ohio
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadowMaker.isActive == True:
                pix.shadowMaker.works.toggleOutline()
                  
    def togglePixLocks(self, key):
        if self.canvas.control != '':  ## animation running
            return 
        stub = '' 
        for pix in self.scene.items(): 
            if pix.type in ('pix', 'bkg'):
                if pix.anime != None and \
                    pix.anime.state() == QAbstractAnimation.State.Running:
                    return    
                if key == 'R': 
                    pix.locked = True
                    stub = 'all'
                elif key == 'U': 
                    pix.locked = False
                    stub = 'all'
                    if pix.type == 'bkg': 
                        pix.bkgMaker.unlockBkg(pix)      
                elif key == 'L' and pix.isSelected() or pix.type == 'bkg': 
                    if pix.type == 'pix':
                        pix.togglelock()  ## wait to toggleTagItems
                    elif pix.type == 'bkg': 
                        pix.bkgWorks.toggleBkgLocks()  ## toggle bkgItem
                    stub = 'select'
        self.mapper.clearMap()
        self.mapper.toggleTagItems(stub)  
                                                                                                                                                                          
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
            if pix.type == 'pix'and pix.shadowMaker.isActive == True:
                pix.shadowMaker.works.hideOutline()
         
    ## added dlbclk if hidden to re-select ##
    def hideSelected(self): 
        ## if self.mapper.mapSet and self.hasHiddenPix():  
        self.mapper.removeMap()  ## also updates pix.pos()
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.part not in ('pivot', 'left','right'):
                if pix.isSelected():
                    pix.setSelected(False)
                    pix.isHidden = True
                elif pix.isHidden:
                    pix.setSelected(True)
                    pix.isHidden = False
            elif pix.zValue() <= common['pathZ']:
                break
                                                                                                                                                                                           
    def hideSelectedShadows(self):  ## runs from shift-H
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadowMaker.isActive == True:
                if pix.isSelected():
                    pix.hide() 
                elif pix.isVisible() == False:
                    pix.show()       
                    pix.setSelected(True)
  
### --------------------------------------------------------                               
    def toggleGrid(self):
        if self.gridGroup:
            self.scene.removeItem(self.gridGroup)
            self.gridGroup = None
        else: 
            self.gridGroup = QGraphicsItemGroup()  
            self.gridGroup.setZValue(common['gridZ'])
            self.scene.addItem(self.gridGroup)         
            gs = common['gridSize']
            pen = QPen(QColor(0,0,255))       
            for y in range(1, int(common['ViewH']/gs)):
                self.addLines(QGraphicsLineItem(0.0, gs*y,
                    float(common['ViewW']), gs*y), pen)
            for x in range(1, int(common['ViewW']/gs)):
                self.addLines(QGraphicsLineItem(gs*x, 0.0,
                    gs*x, float(common['ViewH'])), pen)
        
    def addLines(self, line, pen):
        line.type = 'grid'
        line.setPen(pen)
        line.setOpacity(.30)
        line.setZValue(common['gridZ'])
        line.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemIsMovable, False)
        self.gridGroup.addToGroup(line)

    def gridCount(self):  
        return sum(pix.type == 'grid' 
            for pix in self.canvas.scene.items())
              
### ---------------------- dotsSideCar ---------------------


