
import os
  
from PyQt6.QtCore       import Qt, QPoint, QPointF, pyqtSlot
from PyQt6.QtGui        import QPixmap, QImage, QCursor
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsSideGig        import constrain
from dotsShared         import common, RotateKeys
from dotsMenus          import AnimationMenu
from dotsTagsAndPaths   import TagsAndPaths

import dotsAnimation    as Anime

### ------------------- dotsPixFrameWorks ------------------
''' classes: Frame and Works(functions moved from Pixitem and PixWidget) '''                                                                                           
### --------------------------------------------------------
Pct = -0.50   ## used by constrain - percent allowable off screen

PixSizes = {  ## match up on base filename using 5 characters - sometimes called chars?
    # "apple": (650, 450),  ## see setPixSizes below
    'doral': (215, 215),
}
 
### --------------------------------------------------------
class Frame(QGraphicsPixmapItem):  ## stripped down pixItem - that's why it's here, sort of
### --------------------------------------------------------
    def __init__(self, fileName, parent, z):  
        super().__init__()

        self.canvas = parent  
        self.mapper = self.canvas.mapper
        
        self.tagsAndPaths = TagsAndPaths(self)
              
        self.fileName = fileName  ## needs to contain 'frame'
        self.type = 'frame'  
          
        self.x, self.y = 0, 0  
        self.setZValue(z)
        
        self.tag = ''  
        self.locked = True
        
        self.id = self.canvas.pixCount ## used by mapper
        self.key = ''
    
        img = QImage(fileName)
        
        w = common["ViewW"]  ## from screens
        h = common["ViewH"] 

        img = img.scaled(int(w), int(h),
            Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation)
        
        self.setPixmap(QPixmap(img))
        self.setPos(QPointF(0,0))
        
        del img
        
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False) 
         
  ### --------------------------------------------------------
    @pyqtSlot(str)  ## updated by storyboard
    def setPixKeys(self, key):
        self.key = key  
            
    def hoverLeaveEvent(self, e):
        self.mapper.clearTagGroup()
        e.accept()
           
    def mousePressEvent(self, e):     
        if self.canvas.pathMakerOn == False:      
            if self.key == 'del':     
                self.canvas.showWorks.deleteFrame(self)  
            elif self.key in ('enter','return'):  
                if self.locked:
                    self.locked = False
                self.setZValue(self.canvas.mapper.toFront(1)) 
                self.locked = True
            elif self.key == 'opt': 
                self.mapper.toggleTagItems(self.id)
            e.accept()
      
    def mouseReleaseEvent(self, e):
        if self.canvas.pathMakerOn == False:
            self.key = '' 
            e.accept()
                                                                                 
### --------------------------------------------------------
class Works:  ## extends pixitem and pixwidget
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()
 
        self.pix = parent
        self.scene  = self.pix.scene
        self.canvas = self.pix.canvas

### --------------------------------------------------------
    def closeWidget(self):
        if self.pix.widget != None:
            self.pix.widget.close()
            self.pix.widget = None
                    
    def resetSliders(self):
        self.pix.widget.opacitySlider.setValue(int(self.pix.alpha2*100))
        self.pix.widget.opacityValue.setText('{0:.2f}'.format((self.pix.alpha2)))
        
        self.pix.widget.scaleSlider.setValue(int(self.pix.scale*100))
        self.pix.widget.scaleValue.setText('{0:.2f}'.format(self.pix.scale))
        
        self.pix.widget.rotaryDial.setValue(int(self.pix.rotation))
        self.pix.widget.rotateValue.setText('{:3d}'.format(int(self.pix.rotation)))
              
    def removeThis(self):
        self.pix.clearFocus() 
        self.pix.setEnabled(False)
        self.scene.removeItem(self.pix)
      
    def clearTag(self):  ## reset canvas key to '' 
        self.pix.mapper.clearTagGroup()
        self.pix.canvas.setKeys('') 
        
    def constrainX(self, X):    
        return int(constrain(X, self.pix.width, common["ViewW"], self.pix.width * Pct))
        
    def constrainY(self, Y):
        return int(constrain(Y, self.pix.height, common["ViewH"], self.pix.height * Pct))
                                
    def setPixSizes(self, newW, newH):  
        p = os.path.basename(self.pix.fileName)     
        for key in PixSizes:
            if key in p:
                val = PixSizes.get(key)
                return val[0], val[1]
        # print(p, "{0:.2f}".format(newW), "{0:.2f}".format(newH))
        if newW < 100 or newH < 100:
            newW, newH = 200, 200 
        elif newW > 400 or newH > 400:
            newW, newH = 425, 425
        return newW, newH
             
    def scaleThis(self, key):
        self.pix.setOriginPt()
        if key == '>':
            scale = .03
        elif key == '<':
            scale = -.03
        self.pix.scale += scale
        self.pix.setScale(self.pix.scale)
            
    def rotateThis(self, key):
        self.pix.setOriginPt()
        angle = RotateKeys[key]  ## thanks Martin
        p = self.pix.rotation - angle  ## necessary to match scaleRotate in pathWays
        if p > 360:                    ## now only one source and one set of keys 
            p = p - 360
        elif p < 0:
            p = p + 360
        self.pix.rotation = p
        self.pix.setRotation(self.pix.rotation) 
 
    def newTag(self):  ## hold on to this - position tag above cursor
        p = self.canvas.mapFromGlobal(QPointF(QCursor.pos()))  
        x = p.x()+ 20 
        y = p.y()-20
        return x, y        

    def animeMenu(self):
        x, y = self.makeXY()  
        self.pix.setSelected(True)  ## needs to be selected for menu to work   
        menu = AnimationMenu(self.canvas)     
        self.closeWidget()   
        menu.animeMenu(QPoint(x+50, y+50), 'pix')

    def reprise(self):  ## return pixitem to its original position
        if self.pix.tag == '':  ## you're done
            return
        self.pix.anime = None
        self.pix.anime = Anime.reprise(self.pix)
        self.pix.anime.start()
        self.pix.anime.finished.connect(self.pix.anime.stop)
        self.pix.clearFocus()
                
    def makeXY(self):  
        p = self.pix.pos()
        p = self.pix.canvas.mapToGlobal(QPoint(int(p.x()), int(p.y())))
        return int(p.x()), int(p.y())
    
    def updateXY(self, pos):
        dragX = pos.x() - self.pix.dragAnchor.x()
        dragY = pos.y() - self.pix.dragAnchor.y()     
        b = self.pix.boundingRect()
        self.pix.width, self.pix.height = b.width(), b.height()   
        self.pix.x = self.constrainX(self.pix.initX + dragX)
        self.pix.y = self.constrainY(self.pix.initY + dragY)
        
    def cloneThis(self):
        self.pix.canvas.addPixItem(self.pix.fileName, self.pix.x+25, self.pix.y+10,\
            (self.pix.rotation, self.pix.scale), self.pix.flopped)
                                                                                       
    def flopIt(self):
        self.pix.setMirrored(False) if self.pix.flopped else self.pix.setMirrored(True)
                                                                                                          
### ------------------- dotsPixFrameWorks ------------------



