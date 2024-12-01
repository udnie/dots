

from PyQt6.QtCore       import Qt, QPointF, QPoint, pyqtSlot
from PyQt6.QtGui        import QColor, QPixmap, QImage, QCursor
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsShared         import common
from dotsSideGig        import getVuCtr 
from dotsTableModel     import TableWidgetSetUp, QL
from dotsSideCar2       import tagBkg

### ------------------ dotsFrameAndFlats.py ----------------
''' classes: Frame and Flat '''
### --------------------------------------------------------   

flatKeys = {  
    ' H ':     'Help Menu',
    ' T ':     'Toggle Lock',
    ' \\ ':     'Background Tag',
    'del':     'delete from screen', 
    'enter':   'move to the front',
    'return':  'move to the front',   
    'shift':   'move back one ZValue',
    'dbl-clk': 'delete from screen',   
}

sharedKeys =  ('H','T','del','tag','shift','enter','return')
        
 ### --------------------------------------------------------     
class FlatHelp:  ## flat and frame keyboard help for both
### --------------------------------------------------------
    def __init__(self, parent, canvas, off=0, str='', switch=''):
        super().__init__()  
        
        self.eitherOne = parent  ## can be either
        self.canvas = canvas
        self.switch = switch
    
        self.table = TableWidgetSetUp(55, 155, len(flatKeys)+3)
        self.table.itemClicked.connect(self.clicked)         
  
        width, height = 216, 336
        self.table.setFixedSize(width, height)
 
        if str == 'flat':
            self.table.setRow(0, 0, f"{'Flat Help Menu   ':<15}",'',True,True,2)
        else:
            self.table.setRow(0, 0, f"{'Frame Help Menu  ':<15}",'',True,True,2)
        
        row = 1
        for k , val in flatKeys.items():
            self.table.setRow(row, 0, k, '',True, True, 7)
            self.table.setRow(row, 1, "  " + val, '',False, True)
            row += 1
        
        if str == 'flat':
            self.table.setRow(row, 0, f"{'Hold Down Key - Click on Flat':<25}",QL,True,True,2)
        else:
            self.table.setRow(row, 0, f"{'Hold Down Key - Click on Frame':<25}",QL,True,True,2)
              
        self.table.setRow(row+1, 0,f'{"Click Here to Close Menu  ":<20}' ,'',True,True, 2)
          
        x, y = getVuCtr(self.canvas) 
        if off != 0: x += off   
        
        self.table.move(int(x - width /2), int(y - height /2))
        self.table.show() 

    def clicked(self):
        if self.switch == '':
            try:
                help = self.table.item(self.table.currentRow(), 0).text().strip()
                if help == '\\': help = 'tag'
                if help != 'H' and help in sharedKeys:
                    self.eitherOne.shared(help)
            except:
                None
        self.closeMenu()
    
    def closeMenu(self):   
        self.table.close()
        if self.switch != '':
            self.canvas.setKeys('N')
                                                                            
### -------------------------------------------------------- 
class Flat(QGraphicsPixmapItem):
### -------------------------------------------------------- 
    def __init__(self, color, parent, z=common['bkgZ']):
        super().__init__()

        self.bkgMaker = parent
        self.canvas   = self.bkgMaker.canvas 
        self.scene    = self.bkgMaker.scene
        self.mapper   = self.canvas.mapper
            
        self.fileName = 'flat'
        self.type    = 'flat'
        
        self.color = QColor(color)
        self.tag   = QColor(color)
        
        self.locked = True
        self.setZValue(z)
        
        self.key = ''
        self.x, self.y = 0, 0
        
        p = QPixmap(common['ViewW'],common['ViewH'])
        p.fill(self.color)
        
        self.setPixmap(p)      
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)

### --------------------------------------------------------
    @pyqtSlot(str)  ## updated by storyboard
    def setPixKeys(self, key):
        self.key = key  
            
    def mousePressEvent(self, e):  
        if e.button() == Qt.MouseButton.RightButton:
            self.openMenu()  
        elif not self.canvas.pathMakerOn:    
            if self.key in sharedKeys:
                self.shared(self.key)                       
        e.accept()
        
    def mouseDoubleClickEvent(self, e):
        self.delete()

    def shared(self, key):  ## used with help menu
        self.key = key
        if self.key == 'del':    
            self.delete()      
        elif self.key == 'shift': 
            self.setZValue(self.zValue()-1)    
        elif self.key in('enter','return'): # send to front
            self.setZValue(self.mapper.toFront(1)) 
        elif self.key == 'tag': 
            self.tagThis()
        elif self.key == 'H':  
            self.openMenu()      
        elif self.key == 'T':     
            if self.locked == False:
                self.locked = True     
                self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            else:
                self.locked = False
                self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
            self.tagThis()
        self.key = ''
            
    def openMenu(self):
        self.help = FlatHelp(self, self.canvas, 0,'flat')
                  
    def tagThis(self):
        p = QCursor.pos()
        tagBkg(self, self.canvas.mapFromGlobal(QPoint(p.x(), p.y()-20))) 
                 
    def mouseReleaseEvent(self, e):
        if not self.canvas.pathMakerOn:
            self.key = ''       
        e.accept()
     
    def delete(self):  ## also called by widget
        self.bkgMaker.deleteBkg(self)
  
### --------------------------------------------------------
class Frame(QGraphicsPixmapItem): 
### --------------------------------------------------------
    def __init__(self, fileName, parent, z):  
        super().__init__()

        self.canvas = parent  
        self.mapper = self.canvas.mapper
       
        self.fileName = fileName  ## needs to contain 'frame'
        self.type = 'frame'  
             
        self.help = None
          
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
        self.setPos(QPointF())
        
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
        if e.button() == Qt.MouseButton.RightButton:
            self.openMenu()  
        elif self.canvas.pathMakerOn == False:  ## doesn't run in pathMaker   
            if self.key in sharedKeys:
                self.shared(self.key)     
        e.accept()
        
    def mouseDoubleClickEvent(self, e):
        self.delete()
          
    def shared(self, key):  ## with help menu
        self.key = key
        if self.key == 'del':    
            self.delete()      
        elif self.key == 'shift':  ## send to back of pixitems
            self.setZValue(self.zValue()-1)     
        elif self.key == 'H':  
            self.openMenu()      
        elif self.key in('enter','return'): # send to front
            self.setZValue(self.mapper.toFront(1))    
        elif self.key == 'tag':  ## was '\'
            self.tagThis()
        elif self.key == 'T':     
            if self.locked == False:
                self.locked = True     
                self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            else:
                self.locked = False
                self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
            self.tagThis()
        self.key = ''
    
    def openMenu(self):
        self.help = FlatHelp(self, self.canvas, 0,'frame')
                
    def tagThis(self):
        p = QCursor.pos()
        tagBkg(self, self.canvas.mapFromGlobal(QPoint(p.x(), p.y()-20))) 
                   
    def mouseReleaseEvent(self, e):
        if self.canvas.pathMakerOn == False:
            self.key = '' 
            e.accept()
       
    def delete(self):  ## also called by widget
        self.canvas.showWorks.deleteFrame(self)  
                           
### ------------------ dotsFrameAndFlats.py ---------------- 




