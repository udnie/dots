
import os

from PyQt6.QtCore       import QPoint
from PyQt6.QtGui        import QCursor

from dotsSideGig        import constrain, MsgBox, getPathList, getVuCtr
from dotsShared         import common, RotateKeys
from dotsMapMaker       import MapMaker
from dotsAnimation      import AnimeList
from dotsAnimation      import reprise
from dotsTableModel     import TableWidgetSetUp, QC, QL, QH

Pct = -0.50   ## used by constrain - percent allowable off screen

PixSizes = {  ## match up on base filename using 5 characters - sometimes called chars?
    # "apple": (650, 450),  ## see setPixSizes below
    'doral': (215, 215),
}
                  
### --------------------------------------------------------  
''' shared with canvas.contextMenu and with pixitem thru pixwidget '''
### --------------------------------------------------------    
class AnimationHelp:  
### --------------------------------------------------------
    def __init__(self, parent, pos, token='', off=0):
        super().__init__()
 
        self.pixitem = parent
        self.canvas = self.pixitem.canvas
        self.scene  = self.canvas.scene
        self.mapper = MapMaker(self.canvas)
     
        self.token = token  
         
        if len(self.scene.selectedItems()) > 0:  ## the new way of doing things      
            for p in self.canvas.scene.items():     
                if p.type == 'pix' and p.isSelected() == True:
                    self.token = 'pix'
                    self.pixitem = p
                     
        alst = sorted(AnimeList)  
        ## basing pathlist on what's in the directory
        self.canvas.pathList = getPathList(True)  ## names only
        if len(self.canvas.pathList) == 0:
            MsgBox('getPathList: No Paths Found!', 5)
            return 
    
        alst.extend(['Random']) ## add random to lst
        
        self.table = TableWidgetSetUp(0, 185, len(alst)+4)
        self.table.setColumnHidden(0, True) 
        self.table.itemClicked.connect(self.clicked)   
        
        width, height = 191, 426
        self.table.setFixedSize(width, height)
                         
        self.table.setRow(0, 0, f"{'Animations and Paths':<47}",QL,True,True,2)  
        
        row = 1
        for anime in alst: 
            self.table.setRow(row, 0,  "  " + anime,'', False, True, 2) 
            row += 1

        self.table.setRow(row,     0,f'{"Path Chooser":<44}',QC,True,True, 2)  ## these are tags
        self.table.setRow(row + 1, 0,f'{"Clear Tags":<42}',QL,True,True, 2)       
        self.table.setRow(row + 2, 0,f'{"Click Here to Close Menu":<49}','',True,True, 2)

        x, y = getVuCtr(self.pixitem.canvas)
        z = 50
        
        if self.token == 'pix':  ## from the sprite
             b = self.pixitem.boundingRect()
             width = b.width() + 20      
        elif self.token == 'on':  ## from menus 
             x, y = getVuCtr(self.pixitem.canvas)
             pos = QPoint(x + off, int(y - (height/2)) + 50)
             width = 0           
        else:
            width, z = width/2, 100  ## from storyboard
                     
        self.table.move(int(pos.x()) + int(width), int(pos.y())-z)

        self.table.show() 
          
    def clicked(self):   
        if self.token != 'on':
            tag = self.table.item(self.table.currentRow(), 0).text().strip()   
            if tag != '':     
                if self.token == 'pix' and tag == 'Path Chooser': 
                    self.pixitem.setSelected(True)  ## double tap to be sure
                    self.canvas.pathMaker.pathChooser('Path Menu')
                self.setTag(tag)
                self.mapper.toggleTagItems('anime')  ## adds tagGroup
        self.closeMenu()
      
    def closeMenu(self):   
        self.table.close()
        if self.token == 'on':
            self.canvas.setKeys('N')
      
    def setTag(self, tag):
        if self.mapper.tagSet and tag == 'Clear Tags':
            self.mapper.clearTagGroup()  
             
        for pix in self.scene.selectedItems(): 
            if pix.type in( 'pix', 'shadow'):     
                if tag == 'Clear Tags':
                    pix.tag = ''
                else:
                    pix.tag = tag
                pix.anime = None  ## set by play
                pix.setSelected(False)  ## when tagged
                    
        if self.mapper.isMapSet(): 
            self.mapper.removeMap()
                
        self.closeMenu()
                                                       
### ---------------------- dotsPixWorks -------------------- 
class Works:  ## extends pixitem and pixwidget
### --------------------------------------------------------
    def __init__(self, parent, pix):
        super().__init__()
 
        self.canvas  = parent
        self.pix = pix
             
### --------------------------------------------------------
    def closeWidget(self):
        if self.pix.widget != None:
            self.pix.widget.close()
            self.pix.widget = None
              
    def resetSliders(self):
        self.pix.widget.opacitySlider.setValue(int(self.pix.alpha2*100))
        self.pix.widget.opacityValue.setText(f'{self.pix.alpha2:.2f}')
        
        self.pix.widget.scaleSlider.setValue(int(self.pix.scale*100))
        self.pix.widget.scaleValue.setText(f'{self.pix.scale:.2f}')
        
        self.pix.widget.rotaryDial.setValue(int(self.pix.rotation))
        self.pix.widget.rotateValue.setText(f'{self.pix.rotation:3}')
                           
    def removeThis(self):
        self.pix.clearFocus() 
        self.pix.setEnabled(False)
        self.pix.scene.removeItem(self.pix)
      
    def animeMenu(self):
        self.closeWidget()
        self.pix.setSelected(True)
        x, y = self.makeXY()
        self.help = AnimationHelp(self.pix, QPoint(x,y), 'pix')
   
    def makeXY(self):  
        p = self.pix.pos()
        p = self.pix.canvas.mapToGlobal(QPoint(int(p.x()), int(p.y())))
        return int(p.x()), int(p.y())
 
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
        p = self.pix.canvas.mapFromGlobal(QCursor.pos()) 
        x = p.x()+ 20 
        y = p.y()-20
        return x, y    
 
    def reprise(self):  ## return pixitem to its original position
        if self.pix.tag == '':  ## you're done
            return
        self.pix.anime = None
        self.pix.anime = reprise(self.pix)
        self.pix.anime.start()
        self.pix.anime.finished.connect(self.pix.anime.stop)
        self.pix.clearFocus()
                   
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

### ---------------------- dotsPixWorks --------------------


