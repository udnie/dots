
import time

from PyQt6.QtCore       import Qt, QPointF, QPoint, pyqtSlot
from PyQt6.QtGui        import QColor, QPixmap, QImage, QCursor
from PyQt6.QtWidgets    import QGraphicsPixmapItem

from dotsShared         import common
from dotsSideGig        import getVuCtr, tagBkg 
from dotsTableModel     import TableWidgetSetUp, QL

### ------------------ dotsFrameAndFlats.py ----------------
''' classes: Frame and Flat '''
### --------------------------------------------------------   

flatKeys = {  
    ' H ':     'Help Menu',
    ' T ':     'Toggle Lock',
    ' \\ ':    'Background Tag',
    'del':     'delete from screen', 
    'enter':   'move to the front',
    'return':  'move to the front',   
    'shift':   'move to the back',
}

sharedKeys =  ('H','T','del','tag','shift','enter','return')
        
 ### --------------------------------------------------------     
class FlatHelp:  ## flat and frame keyboard help for both
### --------------------------------------------------------
    def __init__(self, parent, canvas, off=0, str='', switch=''):
        super().__init__()  
        
        self.parent = parent  ## can be either
        self.canvas = canvas
        self.switch = switch
    
        self.table = TableWidgetSetUp(55, 155, len(flatKeys)+3)
        self.table.itemClicked.connect(self.clicked)         
  
        width, height = 216, 306
        self.table.setFixedSize(width, height)
 
        if str == 'flat':
            self.table.setRow(0, 0, f"{'Flat Help Menu   ':<15}",QL,True,True,2)
        else:
            self.table.setRow(0, 0, f"{'Frame Help Menu  ':<15}",QL,True,True,2)
        
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
        
        self.table.move(int(x - (width/2)), int(y - (height/2)))
        self.table.show() 

    def clicked(self):
        if self.switch == '':
            try:
                help = self.table.item(self.table.currentRow(), 0).text().strip()
                if help == '\\': help = 'tag'
                if help != 'H' and help in sharedKeys:
                    self.parent.shared(help)
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
        if self.key == '' and self.canvas.openPlayFile == 'menu':
            self.canvas.openPlayFile = ''
            self.canvas.clear()
            return
        
        elif e.button() == Qt.MouseButton.RightButton:
            if self.canvas.openPlayFile != 'menu' and self.canvas.videoPlayer == None:
                self.openMenu()  
                
        elif self.key in sharedKeys and not self.canvas.pathMakerOn: 
            self.shared(self.key)             
        e.accept()
        
    def mouseReleaseEvent(self, e):
        self.key = ''
        e.accept() 

    def shared(self, key):  ## used with help menu
        match key:
            case 'del':   
                self.delete()       
                        
            case 'shift':       ## to the back
                self.setZValue(self.canvas.bkgMaker.toBack())
                time.sleep(.10)       
                self.canvas.bkgMaker.renumZvals()     
                time.sleep(.10) 
                
            case 'B':           ## not actually tracked
                self.bkgtrackers.trackThis() if self.bkgtrackers.tracker == None \
                    else self.bkgtrackers.tracker.bye()  
                       
            case 'H':  
                self.openMenu()      
                
            case 'tag':          ## '\' tag key
                self.tagThis()
                
            case 'enter' | 'return':
                if self.zValue() == common['bkgZ']:
                    return
                self.canvas.bkgMaker.front(self)        
                time.sleep(.10)   
                
            case 'T':     
                self.setLock() if self.locked == False else self.setUnlock()
                self.tagThis()
     
    def setLock(self):
        self.locked = True     
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        
    def setUnLock(self):
        self.locked = False
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
            
    def openMenu(self):
        self.help = FlatHelp(self, self.canvas, 0,'flat')
                  
    def tagThis(self):
        p = QCursor.pos()
        tagBkg(self, self.canvas.mapFromGlobal(QPoint(p.x(), p.y()-20))) 
                      
    def delete(self):  ## also called by widget
        self.canvas.bkgMaker.deleteBkg(self)
  
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
        if not self.canvas.pathMakerOn:    
            if e.button() == Qt.MouseButton.RightButton:
                self.openMenu()  
            else:  ## doesn't run in pathMaker   
                if self.key in sharedKeys:
                    self.shared(self.key)     
        e.accept()
        
    def mouseReleaseEvent(self, e):   
        self.key = ''  
        e.accept()
 
    def shared(self, key):  ## key can come from help as well
        match key:
            case 'del':    
                self.delete()  
                    
            case 'shift':   ## back one
                self.setZValue(self.zValue()-1)  
                 
            case 'H':  
                self.openMenu()    
                  
            case 'tag':     ## '\' tag key
                self.tagThis() 
                
            case 'enter'| 'return': # send to front
                self.setZValue(self.mapper.toFront(1))  
                  
            case 'T':     
                self.setLock() if self.locked == False else self.setUnLock()
                self.tagThis()
      
    def setLock(self):
        self.locked = True     
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        
    def setUnLock(self):
        self.locked = False
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
        
    def openMenu(self):
        self.help = FlatHelp(self, self.canvas, 0,'frame')
                
    def tagThis(self):
        p = QCursor.pos()
        tagBkg(self, self.canvas.mapFromGlobal(QPoint(p.x(), p.y()-20))) 
                    
    def delete(self):  ## also called by widget
        self.canvas.showWorks.deleteFrame(self)  
                           
### ------------------ dotsFrameAndFlats.py ---------------- 






