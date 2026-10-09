
import time
import math  
import os

from PyQt6.QtCore       import Qt, QTimer, QPoint, QRect
from PyQt6.QtGui        import QGuiApplication, QCursor
from PyQt6.QtWidgets    import QMessageBox,  QFileDialog

from videoClipsWidget   import *
from videoClipsMaker    import Ext, Mxt
from videoPlayerHelp    import VideoHelp, SlideShowHelp, VideoHelpWidget
from videoPlayerWorks   import getMetaData

HGT, PAD = 140, 100 ## pixels added to videowidget size when resizing videoPlayerOne's width and height

ViewW,  ViewH  =  790,  525  ## starting video size
MaxWid, MaxHgt = 1800, 1165

MinWid  = 300  ## minimum widget width
MinHgt  = 400  ## minimum widget height

VertW = 525  ## minimum vertical width on open
VertH = 100  ## vertical starting height
HorzH = 225  ## horizontal starting height

### -------------------------------------------------------- 
''' The function getMetaData and code shared by both videoPlayers 
    and some singletons relocated here to help reduce file sizes 
    and make files less packed and easier to read. I've added a 
    visual aid to point out files or code specific to videoPlayer 
    one or two... ## <- "one", ## <- "two". Easy to search for. 
    '''
### --------------------------------------------------------     
class Shared:  
### -------------------------------------------------------- 
    def __init__(self, parent): 
        super().__init__()  
        
        self.parent = parent
        self.player = 'shared'
        
        self.helpMenus = False
        self.videoPlaying = False
        self.loopSet = False
        self.path = ''
        
        self.frameVisible = True
        self.sliderVisible = True 
      
### --------------------------------------------------------
    def openPlayer(self, key):  ## from keyboard or helpMenu - default on open     
        self.closeHelpMenu()    
        if key == 'S' and self.videoPlaying:
            self.stopVideo()  ## next 'S' is the square format 
            return   
        if self.parent.player == "two": 
            self.parent.closeMediaPlayer()  
        if key in (AspKeys):
            self.parent.clips.setDefaultSizes(key)  ## sets self.aspect
            self.setScreenFormat()  ## just resize it 
            self.aspect = key
        else:
            self.msgbox('Unknown key entered: ' + key)
            return

    def setAspectRatio(self, fileName):
        ext = fileName[fileName.rfind('.'):].lower()   
        if ext in Ext or fileName == '':  ## photo - not a video
            self.msgbox('error setting fileName')
            return False
        key, width, height = '', 0, 0
        try: 
            width, height = getMetaData(fileName)  ## it's here
        except:   
            None    
        if width > 0 and height > 0: 
            self.parent.aspect = math.floor((width/height) * 100)/100.0    
            if key := self.returnKey(self.parent.aspect): 
                self.parent.clips.setDefaultSizes(key) 
            else:
                key = 'O'   
            self.parent.setDisplaySize(key) 
            return True
        else:
            self.msgbox("setAspectRatio: error reading getMetaData")
            return False  
    
    def setFileNameInMediaPlayer(self, fileName):
        if not self.parent.mediaPlayer.setFileName(fileName): 
            self.msgbox('error setting mediaPlayer')
            return False  
        return True 
        
    def setAutoAspect(self, fileName):  
        if self.parent.clips.AutoAspect and not self.parent.clips.MakeClips:
            if not self.setAspectRatio(fileName): ## skip it and open without
                return False
            return  ## hasn't been updated
    
    def moveAndSet(self):
        x = QGuiApplication.primaryScreen().availableGeometry().center().x()
        y = VertH if self.parent.aspect < 1.0 else HorzH
        self.parent.move(x - int(self.parent.width()/2), y)            
        self.parent.saveW, self.parent.saveH = self.parent.width(), self.parent.height()         
        if self.parent.player == 'two' and self.parent.videoItem != None:  ## <- "two"
            self.parent.videoWidth = int(self.parent.videoItem.size().width())
  
    ## if 'O', ctr on background requires more than just the video size
    def setVideoWH(self):  ## from setDisplaySize
        hgt = HGT if self.sliderVisible else HGT-PAD   
        self.parent.VideoH = int((self.parent.height()-hgt) * 1.20)
        self.parent.VideoW = int(self.parent.VideoH * self.parent.aspect)
  
    def setScreenFormat(self):  ## just resize it - single key format
        self.parent.flag = True
        hgt = HGT if self.sliderVisible else HGT-PAD  
        self.parent.resize(self.parent.ViewW+self.parent.wid, self.parent.ViewH+hgt) 
        self.moveAndSet()  
                     
  ### --------------------------------------------------------          
    def looper(self): 
        if not self.loopSet:
            self.loopSet = True
            self.parent.loopButton.setText('LoopOn')
            self.parent.stopButton.setEnabled(False)
            time.sleep(.03)   
            
            if self.parent.player == "one":  ## 6
                self.parent.mediaPlayer.setLoops(-1)  ## 6  
            
        elif self.loopSet:
            self.looperOff()
            if self.parent.mediaPlayer != None:
                self.parent.shared.stopVideo()
            time.sleep(.03)
 
    def looperOff(self):
        self.loopSet = False
        self.parent.loopButton.setText('Loop')
        self.parent.stopButton.setEnabled(True)
      
    def selectFiles(self):  ## keeps the path attached as it might not be the cwd 
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles) 
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            files = dialog.selectedFiles()
            if files != None:
                self.path = os.path.dirname(files[0])
                return self.getFileNames(files) 
            self.msgbox('getFileNames: No Files Found') 
            return None

    def getFileNames(self, files):  ## make sure it's viewable  
        filenames = []
        path = self.path  
        for file in files: 
            path = os.path.join(path, file)
            if os.path.isdir(path):  ## ignore directories
                continue        
            file = os.path.basename(file.lower()) 
            if self.parent.clips.FirstFrame:
                if file[file.rfind('.'):] in Mxt:  ## video file               
                    filenames.append(file)
            else:  
                if file[file.rfind('.'):] in Ext:  ## image file               
                    filenames.append(file)
        if len(filenames) == 0:
            return None
        return filenames
     
    def zoom(self, zoom, WID, HGT, asp ):
        height = int(self.parent.height()* zoom)    
        nvH = (height - HGT)  ## new video height
        
        nvW = int(nvH * asp)  ## new video width   
        nwidth = nvW + WID    ## new widget width   
        
        p, width = self.parent.pos(), self.parent.width()  
        self.parent.resize(nwidth, height)  
            
        dif = int((self.parent.width() - width)/2) 
        self.parent.move(p.x()-dif, p.y())  
                
        self.parent.ViewW, self.parent.ViewH = self.parent.width()-WID, self.parent.height()-HGT    
                      
### --------------------------------------------------------
    def openHelpMenu(self):
        if self.parent.helpFlag:
            self.closeHelpMenu()
        else:
            self.parent.helpMenu = VideoHelp(self.parent)
            self.parent.helpFlag = True
            time.sleep(.03)
 
    def closeHelpMenu(self):
        if self.parent.helpMenu != None: 
            self.parent.helpMenu.tableClose()
            self.parent.helpMenu.close()
            self.parent.helpFlag = False
            time.sleep(.03)
            if self.helpMenus:
                self.closeVideoSlideMenus()
         
    def videoSliderMenus(self):  ## from videoplayerhelp
        self.helpMenus = True
        self.vwidget   = VideoHelpWidget(self.parent)
        self.settings  = Settings(self.parent, 'aaa', 10)
        self.videohelp = VideoHelp(self.parent, -415, 'aaa')
        self.slidehelp = SlideShowHelp(self.parent, 428, 'aaa')
    
    def closeVideoSlideMenus(self):
        if self.helpMenus:    
            self.settings.close()
            time.sleep(.03)
            self.videohelp.table.close()
            self.slidehelp.table.close()
            self.vwidget.close() 
            self.helpMenus = False
   
### --------------------------------------------------------     
    def playVideo(self):  ## setButtons and setSlider don't know about mediaPlayer
        if self.parent.mediaPlayer != None:
            self.parent.mediaPlayer.playVideo()
            self.videoPlaying = True
      
    def stopVideo(self):  
        if self.parent.mediaPlayer != None:
            if self.loopSet:
                self.looperOff()
            self.parent.mediaPlayer.stopVideo()
            time.sleep(.03)
            self.videoPlaying = False
            
    def setPosition(self, position):  ## called by slider if finger pull
        if self.parent.mediaPlayer != None:
            self.parent.mediaPlayer.setPosition(position)
    
    def positionChanged(self, position):  
        if self.sliderVisible:  
            self.parent.slider.setValue(position)     
            
    def durationChanged(self, duration):
        if self.sliderVisible: 
            self.parent.slider.setRange(0, duration)  
  
### --------------------------------------------------------
    def msgbox(self, str):
        msg = QMessageBox()
        msg.setText(str)
        timer = QTimer(msg)
        timer.setSingleShot(True)
        timer.setInterval(7000)
        timer.timeout.connect(msg.close)
        timer.start()
        msg.exec() 
        
    def returnKey(self, asp): 
        for k, v in Keys.items():
            if asp == v[0]: 
                return k
            elif asp - .01 == v[0] or asp + .01 == v[0]:
                return k
        return None
   
    def clearScreen(self):
        self.closeHelpMenu()  ## improvised clear
        self.parent.closeMediaPlayer()  
   
    def toggleSlider(self):  ## now all
        self.parent.flag = True
        self.toggleFrameless()
        if self.sliderVisible and self.parent.height() > MinHgt+PAD: 
            self.sliderVisible = False  
            self.parent.slider.hide()
            self.parent.buttons.hide()
            self.parent.resize(self.parent.width(), self.parent.height()-PAD)
            time.sleep(.03)      
            
        elif not self.sliderVisible:
            self.parent.slider.show()
            self.parent.buttons.show()
            self.sliderVisible = True
            self.parent.resize(self.parent.width(), self.parent.height()+PAD)
            time.sleep(.03) 

    def toggleFrameless(self):  ## from toggleSlider
        p = self.parent.pos()
        if not self.frameVisible:  ## make it visible 
            self.parent.setWindowFlags(self.parent.windowFlags() & ~Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
            self.frameVisible = True
            self.parent.move(p.x(), p.y()-28) 
            
        else:
            self.parent.setWindowFlags(self.parent.windowFlags() | Qt.WindowType.FramelessWindowHint)
            self.frameVisible = False
            self.parent.move(p.x(), p.y()+28)  ## keep the frame stationary
        self.closeHelpMenu()
        self.parent.show()
        
### -------------------------------------------------------           
    def getDirection(self):  ## left out top, topleft and topright - feel free to add them
        corner, which = 6, ''      
        pos = self.parent.mapFromGlobal(QCursor.pos())
        
        bottomLeft  = self.parent.rect().bottomLeft()
        bottomRight = self.parent.rect().bottomRight()
            
        if QRect(QPoint(bottomLeft.x()-(1*corner), bottomLeft.y()-(3*corner)),
            QPoint(bottomLeft.x()+(3*corner), bottomLeft.y()+(1*corner))).contains(pos):
            which = 'botleft'
            
        elif QRect(QPoint(bottomRight.x()-(3*corner), bottomRight.y()-(3*corner)),
            QPoint(bottomRight.x()+(1*corner), bottomRight.y()+(1*corner))).contains(pos):
            which = 'botright'
            
        elif QRect(QPoint( bottomLeft.x()-(2*corner), bottomLeft.y()-(3*corner)),
            QPoint(bottomRight.x()+(2*corner), bottomRight.y()+(1*corner))).contains(pos):
            which = 'bottom'
                        
        return which
        
### ---------------------- that's all ---------------------- 
 

  
