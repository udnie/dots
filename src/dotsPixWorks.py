
import os
  
from PyQt6.QtCore       import QPoint
  
from dotsSideGig        import constrain
from dotsShared         import common, RotateKeys 

import dotsAnimation    as Anime


### --------------------- dotsPixWorks ---------------------
''' classes: Works - small functions that were in Pixitem '''                                                                                           
### --------------------------------------------------------

Pct = -0.50   ## used by constrain - percent allowable off screen
PixSizes = {  ## match up on base filename using 5 characters - sometimes called chars?
    # "apple": (650, 450),  ## see setPixSizes below
    'doral': (215, 215), 
}
                                                                               
### --------------------------------------------------------
class Works: 
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
        self.pix.widget.scaleSlider.setValue(int(self.pix.scale*100))
        self.pix.widget.rotaryDial.setValue(int(self.pix.rotation))
          
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
        angle = RotateKeys[key]        ## thanks Martin
        p = self.pix.rotation - angle  ## necessary to match scaleRotate in pathWays
        if p > 360:                    ## now only one source and one set of keys 
            p = p - 360
        elif p < 0:
            p = p + 360
        self.pix.rotation = p
        self.pix.setRotation(self.pix.rotation) 
 
    def animeMenu(self):
        x, y = self.makeXY()  
        self.pix.setSelected(True)  ## needs to be selected for menu to work
        self.closeWidget()
        self.pix.canvas.sideCar.animeMenu(QPoint(x+50, y+50), 'pix')
 
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
  
### --------------------- dotsPixWorks ---------------------                                                                                                         


