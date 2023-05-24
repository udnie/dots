
import time
import os.path

from PyQt6.QtCore       import Qt, QPoint, QPointF, QPropertyAnimation
from PyQt6.QtGui        import QImage, QPixmap
from PyQt6.QtWidgets    import QGraphicsPixmapItem
    
from dotsShared         import common, RotateKeys
from dotsSideGig        import MsgBox

import dotsAnimation    as Anime

### ---------------------- dotsBkgItem ---------------------                   
''' There are two different speed settings, one for the first screen , the 
    other for the rest that follow.  THe first image doesn't have to 
    travel as far to exit while the second image has to wait its 
    turn and then catch up. A larger number slows its speed.  These
    values were used in the demo, There's also a fix that bumps up
    rate[1] for snakes.  I'm sure your results will vary. '''
### --------------------------------------------------------

abstract = {  ## used by abstract.jpg and snakes.jpg - based on 1280X640 2:1 - under 1MB
    '1080':  (10.0,  17.62,  17.55),  ## first, next, next-right
    '1280':  (10.0,  18.97, 19.0),
    '1215':  (10.0,  17.4,  17.4),  
    '1440':  (10.0,  18.85, 18.95),
    '1296':  (10.0,  17.45, 17.55),  
    '1536':  (10.0,  18.95, 18.95),
    '620':   (10.0,  20.9,   0.0),
}

pano = {  ## no right scroll - used 1600X400 4:1 - one 1MB or less
    '1080':  (10.0,   15.0,  0.0),
    '1280':  (10.0,   15.9,  15.6,),
    '1215':  (10.0,   15.6,  0.0,),
    '1440':  (10.0,   15.95,  0.0,),
    '1296':  (10.0,   15.6,  0.0,),
    '1536':  (10.0,   14.4,  0.0,),
}

showtime = {  ## trigger to add a new background based on number of pixels remaining in runway
    'snakes': 10,  ## same for vertical scrolling
    'left':    4,
    'right':  15,
    'pano':    4,  ## 3:1   ## ->  12,  ## 4:1
}

### --------------------------------------------------------
class BkgItem(QGraphicsPixmapItem):
### --------------------------------------------------------
    def __init__(self, fileName, canvas, z=common['bkgZ'], mirror=False):
        super().__init__()

        self.canvas   = canvas
        self.dots     = self.canvas.dots
        self.scene    = self.canvas.scene
        self.bkgMaker = self.canvas.bkgMaker
      
        self.ViewW = common['ViewW']
        self.ViewH = common['ViewH']
    
        self.fileName = fileName            
        self.scrollable = False    
    
        if not self.dots.Vertical:
            self.setWidthHeight(QImage(fileName))
        else:
            self.setVertical(QImage(fileName))
                 
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                                            
        self.id = 0  ## not used except for conisistency
        self.type = 'bkg'
        
        self.flopped = False
        self.locked = False
                
        self.width = self.imgFile.width()
        self.height = self.imgFile.height() 
        
        self.setZValue(z)
        if not self.dots.Vertical:
            self.setMirrored(mirror)
                                                         
        self.opacity = 100
        self.rotation = 0
        self.scale = 1

        self.x, self.y = 0.0, 0.0
        
        self.tag = ''  
        self.anime = None
        self.addedScroller = False
 
        self.direction = ''   ## direction this is heading in
        self.showtime = 4     ## number of pixels before the runway ends and then it's showtime
          
        self.setPixmap(QPixmap.fromImage(self.imgFile))   
         
        if 'snakes' in self.fileName:  ## snakes need more time
            self.showtime = showtime['snakes']
        elif self.direction in ('left'):    ## 2:1 - 1280X640
            self.showtime = showtime['left']
        elif self.direction in ('right'):   ## 2:1 - 1280X640
            self.showtime = showtime['right']
        elif 'pano' in self.fileName:        ##  4:1 - 1600X400                   
            self.showtime = showtime['pano']
                         
        if not self.dots.Vertical:             
            self.runway = int(common['ViewW'] - self.width) + self.showtime  ## <<--- important
        else:
            self.runway = int(common['ViewH'] - self.height) + self.showtime  ## <<--- important
        
        self.ratio = self.height/9
        self.ratio = int(self.width/self.ratio)
     
        self.dots.statusBar.showMessage(os.path.basename(self.fileName) + '    ' + \
            'Width:   '  + '  ' + str(self.width)       + '    ' +\
            'Runway:   ' + '  ' + str(abs(self.runway)) + '    ' +\
            'ShowTime: ' + '  ' + str(self.showtime)  + '    ' +\
            'Ratio: '    + '  ' + str(self.ratio)+ ':9')
                   
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, False)                                 
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True) 
        
### --------------------------------------------------------   
    def mousePressEvent(self, e):
        if not self.canvas.pathMakerOn:   
            if e.button() == Qt.MouseButton.RightButton:
                self.bkgMaker.addWidget(self)                    
            elif self.canvas.key == 'del':    
                self.delete()          
            elif self.canvas.key == '/':  ## to back
                self.bkgMaker.back(self)     
            elif self.canvas.key == 'shift':
                self.flopped = not self.flopped 
                self.setMirrored(self.flopped)     
            elif self.canvas.key in ('enter','return'):  
                self.bkgMaker.front(self)             
            elif self.canvas.key in ('left','right'):  ## use as scrolling background
                if self.scrollable:
                    self.setDirection(self.canvas.key)
                else:
                    MsgBox('Not Scrollable and Unable to Fulfill your Request...', 6)                           
        e.accept()
           
    def mouseReleaseEvent(self, e):
        if not self.canvas.pathMakerOn: 
            self.canvas.key = ''
        e.accept()
                
### -------------------------------------------------------- 
    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemScenePositionHasChanged: 
            if self.direction == '':
                return  
                       
            elif self.addedScroller == False:  ## check if its showtime             
                if self.direction  == 'left' and int(value.x()-self.runway) <= self.showtime or\
                    self.direction == 'right' and int(value.x()) >= -self.showtime or\
                    self.direction == 'vertical' and int(value.y())-self.runway <= self.showtime:         
                    self.addNextScroller(self)  ## add the next scroller item
                    self.addedScroller = True 
                    
            elif self.addedScroller == True:  ## are we done
                if self.direction  == 'right' and abs(int(value.x())) >= common['ViewW'] or \
                    self.direction == 'left' and abs((value.x())) >= self.width or\
                    self.direction == 'vertical' and int(value.y()) >= self.height:
                    self.anime.stop()
                    self.bkgMaker.delScroller(self)    
                                  
        return super(QGraphicsPixmapItem, self).itemChange(change, value)
                     
    def addNextScroller(self, pix):  ## add and scroll the next image            
        item = BkgItem(pix.fileName, self.canvas)   
            
        if self.ratio > 27 or not self.dots.Vertical:  ## 27:9 = 3:1 
            item.setMirrored(False) if pix.flopped else item.setMirrored(True) 
     
        if item.direction == 'right':
            item.setPos(QPointF(self.runway, 0))
        elif item.direction == 'vertical':
            item.setPos(QPointF(0, self.runway))
                        
        item.setZValue(pix.zValue())
        item.direction = pix.direction 
        item.tag = 'scroller'
           
        self.scene.addItem(item)   
        item.anime = self.setScrollerPath(item, 2)   
        
        item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True)               
        item.anime.start()
       
    def setScrollerPath(self, pix, which):  ## sets scroller animation 
        if pix.direction == '': 
            return  
        path = None      
        node = Anime.Node(pix)    
        try:          
            path = QPropertyAnimation(node, b'pos') 
        except RuntimeError:
            if path == None:
                return
            
        if 'pano' in pix.fileName:
            rate=pano[common['Screen']]         
        else:
            rate=abstract[common['Screen']]  
                            
        if pix.direction == 'left': 
            return self.left(path, pix, rate, which)                    
        elif pix.direction == 'right':
            return self.right(path, pix, rate, which) 
        elif pix.direction == 'vertical':
            return self.vertical(path, pix, rate, which) 
 
    def setDirection(self, key):  ## from keyboard
        self.tag = 'scroller'        
        if key == 'left': 
            self.setPos(QPointF(0, 0))    
            self.direction = key  
            
        elif key == 'right':
            self.setPos(QPointF(self.runway, 0))
            self.direction = key  
            
        self.anime = self.setScrollerPath(self, 1)             
        MsgBox('Direction set to ' +  self.canvas.key + '...', 6) 
       
    def left(self, path, pix, rate, which):       
        if which == 1:
            path.setDuration(int(common['ViewW'] * rate[0]))  ## rate time equals time to clear   
            path.setStartValue(QPoint(0,0)) 
            path.setEndValue(QPoint(-int(pix.width), 0))
        else:    
            rate_one = rate[1]
            if 'snakes' in pix.fileName:  ## looks better and not another dictionary to maintain
                rate_one = rate_one + .2
            path.setDuration(int(common['ViewW'] * rate_one))    
            path.setStartValue(QPoint(common['ViewW'], 0))
            path.setEndValue(QPoint(int(-pix.width), 0))
        return path
           
    def right(self, path, pix, rate, which): 
        if which == 1:        
            path.setDuration(int(common['ViewW'] * rate[0])) 
            path.setStartValue(QPoint(self.runway, 0))
            path.setEndValue(QPoint(int(common['ViewW']), 0))
        else:
            path.setDuration(int(common['ViewW'] * rate[2]))  
            path.setStartValue(QPoint(-self.width, 0))
            path.setEndValue(QPoint(int(common['ViewW']), 0))
        return path
                          
    def vertical(self, path, pix, rate, which):       
        if which == 1: 
            path.setDuration(int(common['ViewH'] * rate[0]))  ## rate time equals time to clear   
            path.setStartValue(QPoint(0, self.runway+self.showtime))
            path.setEndValue(QPoint(0, -self.height))
        else:    
            rate_one = rate[1]
            if 'snakes' in pix.fileName:  
                rate_one = rate_one + .2
            path.setDuration(int(common['ViewH'] * rate_one))    
            path.setStartValue(QPoint(0, self.height+self.runway))
            path.setEndValue(QPoint(0, -self.height))
        return path
             
    def setWidthHeight(self, img):       
        imf = img.scaledToHeight(self.ViewH, Qt.TransformationMode.SmoothTransformation)
        if imf.width() >= self.ViewW:  ## its scrollable enough
            self.imgFile = imf
            self.scrollable = True               
        else:   
            self.imgFile = img.scaled(  ## fill to width or height
            self.ViewW, 
            self.ViewH,
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        del img 
                                   
    def setVertical(self, img): 
        imf = img.scaledToWidth(self.ViewW, Qt.TransformationMode.SmoothTransformation)
        self.imgFile = imf
        self.scrollable = True   
        del img 
                
### --------------------------------------------------------   
    def delete(self):  ## also called by widget
        self.bkgMaker.deleteBkg(self)
   
    def setMirrored(self, bool):
        self.flopped = bool    
        if not self.dots.Vertical:
            self.setPixmap(QPixmap.fromImage(self.imgFile.mirrored(
                # horizontally=self.flopped, vertically=False)))  ## pyside6
                horizontal=self.flopped, vertical=False)))
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            
    def setRotate(self, key):
        self.setOrigin()
        p = int(RotateKeys[key])
        p = int(self.rotation - p) 
        if p > 360:            
            p = p - 360
        elif p < 0:
            p = p + 360  
        if self.bkgMaker.widget: self.bkgMaker.widget.setBkgRotate(p)       
            
    def setOrigin(self):  
        b = self.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.setTransformOriginPoint(op)
                                                  
### ---------------------- dotsBkgItem ---------------------


        