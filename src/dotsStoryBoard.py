
import random
import time

from PyQt6.QtCore       import QEvent, QPointF, pyqtSlot, QRect, QPoint
from PyQt6.QtGui        import QTransform, QCursor
from PyQt6.QtWidgets    import QWidget, QRubberBand, QGraphicsScene
                                        
from dotsShared         import common, CanvasStr, PathStr, MoveKeys, PlayKeys

from dotsSideCar        import SideCar
from dotsSideCar2       import SideCar2

from dotsControlView    import ControlView
from dotsMapMaker       import MapMaker
from dotsBkgMaker       import *
from dotsShowBiz        import ShowBiz
from dotsShowWorks      import ShowWorks
from dotsPathMaker      import PathMaker
from dotsKeysPanel      import KeysPanel
from dotsScrollPanel    import ScrollPanel
from dotsDocks          import *
from dotsHelpButtons    import ButtonHelp
from dotsPixItem        import PixItem
from dotsPixWorks       import AnimationHelp
from dotsWings          import Wings

### -------------------- dotsStoryBoard --------------------
''' class StoryBoard: program hub/canvas, setKeys, includes 
            addPixitem, clear and context menu '''
### --------------------------------------------------------
class StoryBoard(QWidget):
### --------------------------------------------------------
    def __init__(self, parent):
        super().__init__()

        self.dots  = parent 
        self.scene = QGraphicsScene(0, 0, common['ViewW'], common['ViewH'])
        self.view  = ControlView(self)
        
        self.view.setGeometry(QRect(0,0,common['ViewW']+2, common['ViewH']+2))
        self.setFixedSize(common['ViewW']+2, common['ViewH']+2)
        
        self.control = ''           ## variables are shared across some classes
        self.pathMakerOn = False    ## shared
        self.openPlayFile = ''      ## shared 
        self.pathList = []          ## used by animations and animation menu
        self.videoPlayer = None     ## holds mediaplayer reference
        self.animation = False      ## set by showtime
    
        self.canvas = self 
        
        self.sideCar   = SideCar(self)  ## extends canvas
        self.sideCar2  = SideCar2(self)
          
        self.keysPanel = KeysPanel(self)
        self.scroll    = ScrollPanel(self)
        self.pathMaker = PathMaker(self)

        self.mapper    = MapMaker(self) 
        self.bkgMaker  = BkgMaker(self)
                   
        self.showbiz    = ShowBiz(self)   ## reads .play files from showRunner
        self.showWorks  = ShowWorks(self) 
        self.helpButton = ButtonHelp(self)  
     
        addScrollDock(self) 
        addKeysDock(self)
        addButtonDock(self)  

        self.key = ''
        self.origin = QPoint()
        self.pixCount = 1
        
        self.animeHelp = None
        self.rubberBand = QRubberBand(QRubberBand.Shape.Rectangle, self)
        
        self.setMouseTracking(True)
              
        self.view.viewport().installEventFilter(self)
        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)  
    
        self.view.keysSignal[str].connect(self.setKeys)  
        
        if self.dots.msg != '':
            QTimer.singleShot(100, self.bkgMaker.exceedsMsg)
            self.dots.msg = ''
                
### ---------------------- send keys -----------------------
    @pyqtSlot(str)   ## sends keys to canvas, storyboard, pathMaker and sceneItems
    def setKeys(self, key): 
        self.key = key    
         
        if not self.pathMakerOn: 
            if self.key == 'C':
                self.clear()   
            elif self.key in PlayKeys:  ## absolutely necessary for help menus !!!
                QTimer.singleShot(10, partial(self.showbiz.keysInPlay, self.key)) 
            elif self.key == 'H' and len(self.scene.items()) == 0:
                self.helpButton.openMenus()  ## opens canvas help menu
            elif self.key in CanvasStr or self.key == '':
                self.sideCar2.sendPixKeys(self.key) 
                
        elif self.pathMakerOn:                            
            ## send MoveKeys to PathItem selections in PathEdits
            if self.pathMaker.edits.pointItemsSet() == True and \
                self.pathMaker.selections and self.key in MoveKeys:  ## Keys in shared.py
                    self.sideCar2.sendPixKeys(self.key)  ## pointItems get messaged    
                                   
            ## send the rest to pathMaker
            elif self.key in PathStr: 
                if self.key == 'C' and len(self.scene.items()) == 0: 
                    self.clear()  ## really does it and returns to canvas
                elif self.key in ('H', 'M'):
                    self.helpButton.openMenus() 
                else:    
                    self.pathMaker.pathKeys(self.key)
                     
### --------------------- event filter ---------------------- 
    def eventFilter(self, source, e): 
         ## mostly used by mapper and rubberband for selecting sprites  
        if not self.pathMakerOn:    
            if e.type() == QEvent.Type.MouseButtonPress:      
                self.origin = QPoint(e.pos())
                self.mapper.clearTagGroup()  
                
                if self.key == 'cmd':   ## start rubberband 
                    self.mapper.clearMap() 
                    self.sideCar2.unSelect()              
                elif self.sideCar.hasHiddenPix() or self.mapper.selections:
                    if self.animation == False:
                        self.mapper.updatePixItemPos()   
                            
            ##  enter 'cmd' before you move the mouse and the rubberband kicks in, but not after
            elif e.type() == QEvent.Type.MouseMove:  
                if self.key == 'cmd' and self.origin != QPoint(0,0):
                    if self.mapper.isMapSet(): 
                        self.mapper.removeMap()
                    self.rubberBand.show()
                    self.rubberBand.setGeometry(QRect(self.origin, e.pos()).normalized())          
                elif self.mapper.isMapSet() and not self.scene.selectedItems():
                    self.mapper.removeMap()
                elif self.animation == False:  ## no animations running
                    self.mapper.updatePixItemPos()  ## costly but necessary    
                               
            elif e.type() == QEvent.Type.MouseButtonRelease:
                if self.mapper.isMapSet() == False:
                    self.rubberBand.hide()  ## supposes something is selected
                    self.mapper.addSelectionsFromCanvas()           
                if self.key == 'cmd'and self.mapper.isMapSet():
                    self.setKeys('')           
                if self.mapper.isMapSet() and not self.scene.selectedItems():
                    self.mapper.removeMap()
                self.mapper.updatePixItemPos()    
                       
            elif e.type() == QEvent.Type.MouseButtonDblClick:
                ## to preseve selections dbl-clk on an selection otherwise it 
                ## will unselect all - possibly a default as it works the same as 
                ## single click outside the map area do this if nothing at location          
                if p := self.scene.itemAt(QPointF(e.pos()), QTransform()):
                    if p != None and p.type != 'pix' and self.mapper.isMapSet():
                        self.mapper.removeMap()
                        self.setKeys('noMap')                                                 
        return QWidget.eventFilter(self, source, e)
    
### --------------------------------------------------------
    def addPixItem(self, fileName, x, y, clone, mirror):  ## id set in drag/drop
        if 'wings' in fileName:  ## makes a bat
            Wings(self, x, y, '')       
        else:
            self.pixCount += 1  ## can't move this
            pix = PixItem(fileName, self.pixCount, x, y, self, mirror)            
            if clone != None:  ## clone it - uses id and in pixitem to clone itself         
                self.sideCar.transFormPixItem(pix,
                    clone[0],
                    clone[1] * random.randrange(95, 105)/100.0,
                    pix.alpha2)
                return   
            elif 'frame' in pix.fileName: 
                self.showWorks.addFrame(pix.fileName)  ## pin it on drag and drop
            else:
                self.scene.addItem(pix)
              
    def exit(self):
        QTimer.singleShot(0, self.clear) 
        QTimer.singleShot(100, self.dots.closeAll)
        QTimer.singleShot(200, self.dots.close)   
                           
    def clear(self):
        if  self.canvas.videoPlayer != None:  ## this is seriously redundant but necessary
            self.canvas.videoPlayer.stopVideo()
            time.sleep(.10) 
            self.canvas.sideCar.videoOff()
        time.sleep(.10) 
            
        if self.control != '' or self.animation == True:
            self.showbiz.showtime.stop('clear')  
            time.sleep(.10)  ## otherwise an error report and lockup
        
        if self.canvas.pathMakerOn:
            self.pathMaker.pathMakerOff() 
        if self.showbiz.tableView != None:
            self.showbiz.tableView.bye()                     
        self.sideCar.clearWidgets()   
        self.sideCar.clearSceneItems()    
        self.scene.clear() 
        self.helpButton.closeMenus() 
        self.mapper.clearMap() 
        self.bkgMaker.init()    
        self.btnAddBkg.setEnabled(True)   
        self.btnHelp.setEnabled(True)
        self.pixCount = 0  ## set it to match showbiz
        self.sideCar.gridGroup = None
        self.openPlayFile = ''
        self.video = None
        self.animation = False  
        self.view.grabKeyboard()
        self.canvas.setFocus()

### --------------------------------------------------------
    def contextMenuEvent(self, e):  ## if sprites are selected and right-mouse click
        if len(self.scene.selectedItems()) > 0:  ## don't remove e
            if self.animeHelp != None:
                self.animeHelp == None
            self.animeHelp = AnimationHelp(self.canvas, QCursor.pos(), 'story')
        e.accept()
        
### -------------------- dotsStoryBoard --------------------


