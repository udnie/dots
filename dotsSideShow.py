from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

import dotsAnimation as animat

from dotsShared      import common, paths
from dotsSideCar     import MsgBox

### ---------------------- dotsSideShow --------------------
''' dotsSideShow: handles play, pause, stop, & tag functions '''
### --------------------------------------------------------
class SideShow():

    def __init__(self, parent):
        super().__init__()
 
        self.canvas  = parent
        self.sideCar = self.canvas.sideCar
        self.scene   = parent.scene

        self.buttons = parent.buttons
        self.initMap = parent.initMap
 
        self.gridZ   = common["gridZ"]
        self.control = ""
        self.tagSet  = False
        self.tagZ    = 0

### --------------------------------------------------------
    def setAction(self, tag):
        if self.tagSet and tag == "Clear Tags":
            self.clearTagItems()
        for pix in self.scene.selectedItems():
            if tag == "Clear Tags":
                pix.tag = ''
            else:
                pix.tag = tag
            pix.anime = None        ## set by play
            pix.setSelected(False)  ## when tagged 
        if self.initMap.mapSet: 
            self.initMap.removeMap()

    def play(self):
        if self.control != '': return
        k = 0
        self.canvas.unSelect()
        if self.initMap.mapSet: self.initMap.removeMap()
        if self.tagSet: self.clearTagItems()
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.tag:
                ## if random, slice to length, display actual anime if paused 
                if 'Random' in pix.tag:
                    pix.tag = pix.tag[0:len('Random')]
                pix.anime = animat.setAnimation(
                    pix.tag, 
                    pix)
                pix.anime.start()
                k += 1
            elif pix.zValue() <= self.gridZ:
                break 
        if k:
            self.disablePlay()  
            self.control = 'pause'
          
    def pause(self):
        if self.initMap.mapSet: self.initMap.removeMap()
        if self.tagSet: self.clearTagItems()
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.anime:
                if self.control == 'pause':
                    pix.anime.pause()
                elif self.control == 'resume':
                    pix.anime.resume()
                    if pix.isSelected(): 
                        pix.setSelected(False)
            if pix.zValue() <= self.gridZ:
                break
        self.setPauseKey()
 
    def stop(self, rep=''):  ## stop set to clear in dropcanvas
        if self.tagSet: self.clearTagItems()
        for pix in self.scene.items():
            if pix.type == 'pix' and pix.anime:
                pix.anime.stop()
                ## reprise not run if clearing screen 
                if not rep: pix.reprise() 
            elif pix.zValue() <= self.gridZ:
                break
        self.enablePlay() 

    def toggleTagItems(self):  
        if self.tagSet: 
            self.clearTagItems()
        else:
            k = 0
            self.tagZ = self.sideCar.toFront(20.0)
            for pix in self.scene.items():
                if pix.type == 'pix' and pix.tag:  
                    self.tagIt(pix) 
                    k += 1
                elif pix.zValue() <= self.gridZ:
                    break
            if k > 0: self.tagSet = True
  
    def clearTagItems(self):
        for itm in self.scene.items():
            if itm.type == 'tag':  
                itm.clearFocus()
                self.scene.removeItem(itm)
            elif itm.zValue() < self.tagZ:
                break
        self.tagSet = False      

    def enablePlay(self):
        self.control = ''
        self.buttons.btnPlay.setEnabled(True)
        self.buttons.btnPause.setEnabled(False)
        self.buttons.btnStop.setEnabled(False) 
        self.buttons.btnPause.setText("Pause");

    def disablePlay(self):
        self.control = 'pause'
        self.buttons.btnPlay.setEnabled(False)
        self.buttons.btnPause.setEnabled(True)
        self.buttons.btnStop.setEnabled(True)  

    def setPauseKey(self):        
        if self.control == 'pause': 
            self.control = 'resume'
            self.buttons.btnPause.setText( "Resume" );
        elif self.control == 'resume':
            self.buttons.btnPause.setText( "Pause" );
            self.control = 'pause'

    def tagIt(self, pix):  
        p = pix.sceneBoundingRect()
        x = int(p.x() + p.width()*.25)
        y = int(p.y() + p.height()*.30)
        if  p.width() + p.height() < 30: ## too small??
            return
        tag = TagIt(self.control, pix.tag)
        tag.setPos(x,y)
        tag.setZValue(self.tagZ)
        self.scene.addItem(tag)

### --------------------------------------------------------
class TagIt(QGraphicsSimpleTextItem):

    def __init__(self, control, tag):
        super().__init__()

        if control in ['pause','resume'] and "Random" in tag:
            tag = tag[7:]
            self.color = QColor(QColor(0,255,127))
        else:
            self.color = QColor(QColor(255,165,0))
            if "Random" in tag: tag = tag[0:6] 
   
        self.type = 'tag'
        self.text = tag   

        self.font = QFont('Modern', 12)
        metrics   = QFontMetrics(self.font)
        self.rect = QRectF(0, 0, metrics.width(self.text)+13, 19)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget): 
        brush = QBrush()
        brush.setColor(self.color)
        brush.setStyle(Qt.SolidPattern)

        painter.fillRect(self.boundingRect(), brush)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(Qt.black)
        painter.setFont(self.font)
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self.text)

### ---------------------- dotsSideShow --------------------
