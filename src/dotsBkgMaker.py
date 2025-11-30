
import os 
import os.path

from functools          import partial
       
from PyQt6.QtCore       import QPoint, QPointF, QTimer
from PyQt6.QtGui        import QColor, QCursor
from PyQt6.QtWidgets    import QWidget, QFileDialog, QGraphicsPixmapItem, \
                                QColorDialog

from dotsShared         import common, paths, ControlKeys
from dotsSideGig        import MsgBox
from dotsBkgWidget      import BkgWidget
from dotsBkgItem        import BkgItem
from dotsScreens        import *
from dotsFrameAndFlats  import Flat
from dotsBkgTrackers    import BkgTrackers
from dotsHelpDesk       import StoryHelp2

### --------------------- dotsBkgMaker ---------------------
''' class: BkgMaker - creates and supports BkgItem '''       
### --------------------------------------------------------
class BkgMaker(QWidget):  
### --------------------------------------------------------
    def __init__(self, parent, file =''):
        super().__init__()
           
        self.canvas = parent 
        self.scene  = self.canvas.scene
        self.view   = self.canvas.view  
        self.mapper = self.canvas.mapper
        
        self.fileName = file  ## current
  
        self.init()
      
    def init(self):
        self.flat    = None
        self.widget = None  ## there is only one
        
        self.storyHelp2 = None  ## do it here as there's no storyboard
        
        self.factor = 1.0  ## sets the factor and mirroring defaults in bkgItem
        self.mirroring = False
          
        self.screenrate = {}
        self.newTracker = {}
        
        self.bkgtrackers = BkgTrackers(self)
           
### --------------------------------------------------------
    def openBkgFiles(self):  ## opens both background and flats 
        if self.canvas.control in ControlKeys and \
            self.canvas.pathMakerOn == False:  ## animation
            return
        Q = QFileDialog()   ## open only background  
        Q.Option.DontUseNativeDialog
        file, _ = Q.getOpenFileName(self.canvas,
            'Choose an image file to open', paths['bkgPath'],
            'Images Files(*.bmp *.jpg *.png *.bkg *.JPG *.PNG *.mov *.mp4)')
        if file:  ## it's either a flat or an jpg/png or a video
            if file.endswith('.mov') or file.endswith('.mp4'): 
                QTimer.singleShot(100, partial(self.canvas.sideCar.addVideo, file)) 
            else:
                file = paths['bkgPath'] + os.path.basename(file)  
                self.openFlatFile(file) if file.endswith('.bkg') else self.addBkg(file)
        Q.accept()

### --------------------------------------------------------              
    def addBkg(self, file):  ## background from jpg/png
        if self.mapper.isMapSet():
            self.mapper.removeMap()

        bkg = BkgItem(file, self.canvas)  ## the real deal
        if bkg.type == None:
            return
            
        bkg.setZValue(common['bkgZ'])  ## always on top              
        self.scene.addItem(bkg)    
   
        self.updateZvals(bkg)  ## update other bkg zvalues 
        self.setXY(bkg)
            
        self.bkgtrackers.addTracker(bkg)  ## always - even if not a scroller   
        self.lockBkg(bkg)  ## always lock it
                        
        bkg.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False) 
                      
### --------------------------------------------------------
    def openFlatFile(self, file):  ## read from .bkg file - a 'flat'
        try:
            with open(file, 'r') as fp:
                self.setBkgColor(QColor(fp.readline()))
        except IOError:
            MsgBox('openFlatFile: Error reading file', 5)
            return

    def bkgColor(self):  ## from button or widget   
        if self.canvas.control in ControlKeys:  ## running animation
            return
        self.setBkgColor(QColorDialog.getColor())

    def setBkgColor(self, color):  ## add a flat color to canvas
        if color.isValid():
            self.flat = Flat(color, self) 
            self.flat.setZValue(common['bkgZ'])  ## always on top       
            self.scene.addItem(self.flat) 
            self.updateZvals(self.flat)   ## update other bkg, frame zvalues 
    
    def saveFlat(self):  ## saves a color 'flat' file - from bkg save button
        if self.flat != None and self.flat.type == 'flat':
            if self.flat.zValue() == self.mapper.toFront():  ## top most screen item   
                self.saveBkgColor()  
                return  

    def saveBkgColor(self):  ## write to .bkg file
        if self.canvas.pathMakerOn == False:
            Q = QFileDialog()
            Q.Option.DontUseNativeDialog
            Q.setDirectory(paths['bkgPath'])
            f = Q.getSaveFileName(self.canvas, paths['bkgPath'],  
                paths['bkgPath'] + 'tmp.bkg')  
            Q.accept()       
            if not f[0]: 
                return                 
            if not f[0].lower().endswith('.bkg'):
                MsgBox("Save Background Color: Wrong file extention - use '.bkg'", 5)  
                return
            else:
                try:
                    with open(f[0], 'w') as fp:
                        fp.write(self.flat.color.name())
                except IOError:
                    MsgBox('saveBkgColor: Error saving file', 5)
                self.flat = None
                                           
### -------------------------------------------------------- 
    def addWidget(self, bkg):  ## background widget
        self.closeWidget()  
        if bkg.type == 'flat':
            return          
        self.widget = BkgWidget(bkg, self) 
        self.lockBkg(bkg)
        p = common['widgetXY']
        p = self.canvas.mapToGlobal(QPoint(p[0], p[1]))       
        self.widget.save = QPointF(p.x(), p.y())
        self.widget.setGeometry(p.x(), p.y(), int(self.widget.WidgetW), \
            int(self.widget.WidgetH))
        self.resetSliders(bkg)
        self.bkgtrackers.restoreFromTrackers(bkg)
        self.updateWidget(bkg)
           
    def addStoryHelp2(self):
        self.closeStoryHelp2()
        self.storyHelp2 = StoryHelp2(self.canvas)
        
    def closeStoryHelp2(self):
        if self.storyHelp2 != None:
            self.storyHelp2.closeMenu()
            self.storyHelp2 = None  
              
    def closeStoryHelp(self):
        if self.canvas.helpButton.storyFlag == True:
            self.canvas.helpButton.storyHelp.closeMenu()
            self.canvas.helpButton.storyFlag = False
            self.canvas.helpButton.storyHelp = None
                    
    def closeWidget(self):
        if self.widget != None:
            self.closeStoryHelp()
            self.closeStoryHelp2() 
            self.widget.close()
            self.widget = None
            self.view.grabKeyboard()
  
    def updateWidget(self, bkg):
        self.canvas.sideCar2.setMirrorBtnText(bkg, self.widget)
        self.canvas.sideCar2.setBtns(bkg, self.widget)
        self.setLocksText(bkg) 
                
### --------------------------------------------------------
    def resetSliders(self, bkg):
        if bkg != None and bkg.type == 'bkg':                                
            self.widget.factorDial.setValue(int(bkg.factor*100))
            self.widget.factorValue.setText(f'{bkg.factor:.2f}')
            
            self.widget.rateSlider.setValue(int(bkg.rate*100))
            self.widget.rateValue.setText(f'{bkg.rate:.2f}')
            
            self.widget.showtimeSlider.setValue(bkg.showtime)
            self.widget.showtimeValue.setText(f'{bkg.showtime:3}')
                                                                 
    def setLocksText(self, bkg):
        if bkg == None:
            return
        self.widget.lockBtn.setText('UnLocked') if bkg.locked == False \
            else self.widget.lockBtn.setText('Locked')         
                                     
### --------------------------------------------------------                                           
    def deleteBkg(self, bkg, where=''):  ## delete tracker as well   
        if bkg.type == 'flat':
            self.scene.removeItem(bkg)
            bkg = None
            return
        elif where == '' and bkg.type == 'bkg':
            self.bkgtrackers.delTracker(bkg)
            
        if self.widget:
            self.closeWidget()
             
        if bkg.matte != None:
            bkg.matte.bye()
            bkg.matte = None
           
        self.scene.removeItem(bkg)
        bkg = None
        try:
            self.canvas.btnAddBkg.setEnabled(True)
        except:
            None
                                                     
    def lockBkg(self, bkg):
        if bkg and bkg.type == 'bkg':  
            bkg.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
            bkg.locked = True
            if self.widget: self.widget.lockBtn.setText('Locked')
                            
    def unlockBkg(self, bkg):
        if bkg and bkg.type == 'bkg':  
            bkg.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
            bkg.locked = False
            if self.widget: self.widget.lockBtn.setText('UnLocked')
  
### --------------------------------------------------------            
    def showtime(self, bkg):  ## 'run' from widget button
        self.closeWidget()
        
        p = QCursor.pos()
        QCursor.setPos(int(p.x()+220), int(p.y()+650.0))  ## works for 720
     
        self.canvas.showbiz.showtime.run()
     
    def flopIt(self, bkg):  ## used by widget 
        if bkg and bkg.type == 'bkg':  
            bkg.setMirrored(False) if bkg.flopped else bkg.setMirrored(True)
                                                                             
    def front(self, bkg):
        if bkg.zValue() == common['bkgZ']:
            return
        bkg.setZValue(common['bkgZ'])  ## -99
        self.updateZvals(bkg)  ## update other bkg zvalues 
        self.lockBkg(bkg) 
        self.closeWidget()
             
    def updateZvals(self, bkg):  ## move the rest back one Z
        for itm in self.scene.items():  ## used by bkgMaker mainly to add
            if itm.type in ('bkg', 'flat') and itm.zValue() <= bkg.zValue():
                if itm != bkg:
                    itm.setZValue(itm.zValue()-1)                 
        self.renumZvals()
        
    def toBack(self):  ## finds the lowest bkg, flat zValue 
        last = 1000  ## used by bkgItem and flat - default
        for itm in self.scene.items():
            if itm.type in  ('bkg', 'flat') and itm.zValue() < last:
                last = itm.zValue()
        return last - 1   
 
    def renumZvals(self, called=''):
        bkz = common['bkgZ']  ## renumber - bkg and flats no gaps
        for itm in self.scene.items():
            if itm.type in ('bkg', 'flat'):
                itm.setZValue(bkz)
                bkz -= 1 
        # self.canvas.sideCar.dump(called)
                       
    def setXY(self, bkg):
        p = bkg.sceneBoundingRect()
        bkg.setPos(p.x() , p.y())
        self.x, self.y = p.x() , p.y()     
                                                 
### --------------------- dotsBkgMaker ---------------------




