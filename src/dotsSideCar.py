
import os
import os.path
import random
import json

from PyQt6.QtCore       import Qt, QPointF, QPoint, QSize, QRect
from PyQt6.QtGui        import QPen, QColor
from PyQt6.QtWidgets    import QFileDialog, QGraphicsItemGroup, QGraphicsLineItem, \
                                QApplication, QMenu
                                                    
from dotsShared      import common, paths
from dotsPixItem     import PixItem
from dotsSideGig     import MsgBox, constrain, getPathList
from dotsMapItem     import InitMap
from dotsAnimation   import *

### ---------------------- dotsSideCar ---------------------
''' no class: pixTest, transFormPixitem, snapShot, toggleGrid, 
    animationMenu, assorted small functions and a few from sideShow '''   
### --------------------------------------------------------
class SideCar:
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.canvas = parent
        self.dots   = self.canvas.dots
        self.scene  = self.canvas.scene
        self.mapper = InitMap(self.canvas)
      
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
                        pix.width * -common['factor']))
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
        
    def hasBackGround(self):
        for itm in self.scene.items(Qt.SortOrder.AscendingOrder):
            if itm.type == 'bkg':
                return True
        return False
    
    def snapTag(self):
        return str(random.randrange(1000,9999)) + chr(random.randrange(65,90))
             
### --------------------------------------------------------           
    def toggleMenu(self):
        self.canvas.keysPanel.toggleMenu()  ## no direct path from controlView
                                                                                           
    def clearWidgets(self):                             
        for widget in QApplication.allWidgets():  ## note!!
            if widget.accessibleName() == 'widget':  ## shadow and pixitems widgets
                widget.close()
        if self.canvas.pathMakerOn: self.canvas.pathMaker.pathChooserOff()
    
    def pageDown(self, key):  ## for sprite scrollPanel
        self.canvas.scroll.pageDown(key)
        
### --------------------------------------------------------                                                                                                                
    def toggleOutlines(self):  ## runs from O as in Ohio
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadowMaker.isActive == True:
                pix.shadowMaker.works.toggleOutline()
                                                                                                          
    def hideOutlines(self):  ## runs from shift-O
        for pix in self.scene.items():
            if pix.type == 'pix'and pix.shadowMaker.isActive == True:
                pix.shadowMaker.works.hideOutline()
                                                                                                                                                                                                       
    def hideSelectedShadows(self):  ## runs from shift-H
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.shadowMaker.isActive == True:
                if pix.isSelected():
                    pix.hide() 
                elif pix.isVisible() == False:
                    pix.show()       
                    pix.setSelected(True)
 
### --------------------------------------------------------                               
    def animeMenu(self, pos, where=''): ## shared with canvas thru context menu
        self.closeMenu()                ## and with pixitem thru pixwidget
         
        self.menu = QMenu(self.canvas)                   
        alst = sorted(AnimeList)
        
        ## basing pathlist on what's in the directory
        self.canvas.pathList = getPathList(True)  ## names only
        
        rlst = sorted(self.canvas.pathList)     
        alst.extend(['Random']) ## add random to lst
        
        self.menu.addAction('Animations and Paths')
        self.menu.addSeparator()   
        
        for anime in alst:
            action = self.menu.addAction(anime)
            action.triggered.connect(
                lambda chk, anime=anime: self.setAnimationTag(anime))
            
        self.menu.addSeparator()
        for anime in rlst:
            action = self.menu.addAction(anime)
            action.triggered.connect(
                lambda chk, anime=anime: self.setAnimationTag(anime))    
         
        self.menu.addSeparator()
        anime = 'Clear Tags'
        action = self.menu.addAction(anime)
        action.triggered.connect(
            lambda chk, anime=anime: self.setAnimationTag(anime))
        
        if where == 'pix':
            self.menu.move(pos) 
            self.menu.show()
        else:
            self.menu.exec(pos)
         
    def closeMenu(self):   
        if self.menu:
            self.menu.close()
        self.menu = None    
    
    def setAnimationTag(self, tag):
        self.closeMenu()
        if self.mapper.tagSet and tag == 'Clear Tags':
            self.mapper.clearTagGroup()
        for pix in self.scene.selectedItems(): 
            if pix.type != 'pix':
                continue
            if tag == 'Clear Tags':
                pix.tag = ''
            else:
                pix.tag = tag
            pix.anime = None        ## set by play
            pix.setSelected(False)  ## when tagged 
        if self.mapper.isMapSet(): 
            self.mapper.removeMap()               
                
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
        
### ------------------ moved from sideShow -----------------
    def setPauseKey(self):        
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
                
### ---------------------- dotsSideCar ---------------------


