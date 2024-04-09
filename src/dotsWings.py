
import os

from PyQt6.QtCore       import Qt
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsShared         import paths, common
from dotsPixItem        import PixItem

### ------------------------ dotsWings ---------------------
class Wings: 
### --------------------------------------------------------    
    ''' Wings no longer come off, only the bat can move, wings still flap '''   
### --------------------------------------------------------
    def __init__(self, parent, x, y, tag): 
        super().__init__()
 
        self.canvas = parent    
        self.scene  = self.canvas.scene     
        
        if not os.path.exists(paths['imagePath'] + 'bat-pivot.png'):
            return
    
        self.pivot     = self.pivot(paths['imagePath'] + 'bat-pivot.png', x, y, tag)
        self.rightWing = self.right(paths['imagePath'] + 'bat-wings.png', x, y)
        self.leftWing  = self.left(paths['imagePath']  + 'bat-wings.png', x, y)
                                             
        self.half   = self.pivot.width/2 
        self.height = self.pivot.height/5    

        if common['Screen'] in ('1215', '1440'):
            self.height = self.pivot.height/7  ## drops too low otherwise
        elif common['Screen'] in ('1536', '1296'):
            self.height = self.pivot.height/9  
          
        try:
            self.pivot.setPos(self.pivot.x, self.pivot.y)
            self.pivot.setScale(.60)
            self.pivot.setOriginPt() 
        except IOError:
            pass    
                
        ## center wings around pivot - some magic numbers
        self.rightWing.setPos(self.half+1, self.height-2)
        self.leftWing.setPos(-self.leftWing.width+(self.half+5), self.height-5)

        self.rightWing.setParentItem(self.pivot)  
        self.leftWing.setParentItem(self.pivot)
        
        self.scene.addItem(self.pivot)
                   
### --------------------------------------------------------
    def pivot(self, file, x, y, tag):  ## tag may be empty - used for setting path or animation
        self.canvas.pixCount += 1         
        pivot = PixItem(file, 
            self.canvas.pixCount,
            x, y,  
            self.canvas
        ) 
        pivot.part = 'pivot' 
        pivot.tag  = tag  ## path to follow - random select
  
        pivot.setZValue(self.canvas.mapper.toFront(-1))
        pivot.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True)  
        pivot.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemDoesntPropagateOpacityToChildren, True)
                    
        return pivot
   
### --------------------------------------------------------  
    def right(self, file, x, y):            
        self.canvas.pixCount += 1
        pix = PixItem(file, self.canvas.pixCount, x-20, y, 
            self.canvas,
            False,
        )  ## don't flop it 
        return self.setWing(pix, 'right')  
            
### --------------------------------------------------------          
    def left(self, file, x, y):         
        self.canvas.pixCount += 1
        pix = PixItem(file, self.canvas.pixCount, x + self.rightWing.width, y,  ## offset to left
            self.canvas,
            True
        )  ## flop it
        return self.setWing(pix, 'left') 
   
### --------------------------------------------------------              
    def setWing(self, pix, wing):   
        pix.part = wing  ## part could be other than a wing   
        pix.tag  = 'Flapper'  ## applies this animation when run
        pix.setZValue(pix.zValue())  ## reset wing zvals
        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, False)
        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemStacksBehindParent)
        pix.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIgnoresParentOpacity, True)  ## won't disappear
        pix.setAcceptedMouseButtons(Qt.MouseButton.NoButton)  ## mouse ignored - wings can't be move       
        return pix
            
  ### ------------------------ dotsWings ---------------------
  
  
            