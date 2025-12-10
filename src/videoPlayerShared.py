
import os
import time
import math  
import subprocess

from functools          import partial

from PyQt6.QtCore       import Qt, QTimer, QPoint, QRect
from PyQt6.QtGui        import QGuiApplication, QCursor
from PyQt6.QtWidgets    import QSlider, QHBoxLayout, QLabel, QFileDialog, \
                                QPushButton, QFrame, QSizePolicy, QMessageBox

from videoClipsWidget   import *
from videoClipsMaker    import Ext  

### -------------------------------------------------------- 
''' The function getMetaData and code shared by both videoPlayers 
    and some singletons relocated here to help reduce file sizes 
    and make files less packed and easier to read. I've added a 
    visual aid to point out files or code specific to videoPlayer 
    one or two... ## <- "one", ## <- "two". Easy to search for. '''
### --------------------------------------------------------     
class Shared:  
### -------------------------------------------------------- 
    def __init__(self, parent): 
        super().__init__()  
        
        self.parent = parent
    
### --------------------------------------------------------
    def openPlayer(self, key):  ## from keyboard or helpMenu - default on open      
        self.closeHelpMenu() 
        if self.parent.player == "two": self.closeMediaPlayer()  ## <- "two"
        if key in AspKeys:    
            self.parent.clips.setDefaultSizes(key)  ## sets self.aspect
            self.parent.shared.setScreenFormat()  ## just resize it
        else:
            self.msgbox('Unknown key entered')
            return

    def setAspectRatio(self, fileName):
        ext = fileName[fileName.rfind('.'):].lower()   
        if ext in Ext or fileName == '':  ## photo - not a video
            self.msgbox('error setting fileName')
            return False
        key, width, height = '', 0, 0
        try: 
            width, height = getMetaData(fileName)  ## in clipswidget
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
    
    def moveAndSet(self):
        x = QGuiApplication.primaryScreen().availableGeometry().center().x()
        y = VertH if self.parent.aspect < 1.0 else HorzH
        self.parent.move(x - int(self.parent.width()/2), y)            
        self.parent.saveW, self.parent.saveH = self.parent.width(), self.parent.height()         
        if self.parent.player == 'two' and self.parent.videoItem != None:  ## <- "two"
            self.parent.videoWidth = int(self.parent.videoItem.size().width())
  
    ## if 'O', ctr on background requires more than just the video size
    def setVideoWH(self):  ## from setDisplaySize
        hgt = HGT if self.parent.sliderVisible == True else HGT-PAD   
        self.parent.VideoH = int((self.parent.height()-hgt) * 1.20)
        self.parent.VideoW = int(self.parent.VideoH * self.parent.aspect)
  
    def setScreenFormat(self):  ## just resize it - single key format
        self.parent.flag = True
        hgt = HGT if self.parent.sliderVisible == True else HGT-PAD  
        self.parent.resize(self.parent.ViewW+WID, self.parent.ViewH+hgt) 
        self.moveAndSet()  
           
    def addToScene(self, fileName): ## <- "two"
        self.parent.fileName = fileName  
        self.parent.scene.addItem(self.parent.videoItem)
        self.parent.mediaPlayer.setBackDrop()
            
### --------------------------------------------------------
    def openDirectory(self):  ## in clips - point to a directory to read from  
        if self.parent.player == 'two':  ## <- "two"
            self.closeMediaPlayer()
        self.closeOnOpen() 
        if self.parent.clips.MakeClips == False: 
            self.msgbox('Make sure Opencv is installed and MakeClipsOn is set')
            return      
        if self.parent.clips.SkipFrames == True:
            self.parent.clips.openFile(True)   ## <- "one"
        else:
            path = QFileDialog.getExistingDirectory(self.parent, '')
            if path == None or path == '':
                return  
            title = self.parent.clips.setTitle(path)    
            self.parent.setFileName(title)
            QTimer.singleShot(20, partial(self.parent.clips.assembler, os.getcwd(), title))
  
### --------------------------------------------------------
    def playVideo(self):  ## setButtons and setSlider don't know about mediaPlayer
        if self.parent.mediaPlayer != None:
            self.parent.mediaPlayer.playVideo()
      
    def stopVideo(self):
        if self.parent.mediaPlayer != None:
            self.parent.mediaPlayer.stopVideo()
            time.sleep(.03)
            
    def setPosition(self, position):  ## called by slider if finger pull
        if self.parent.mediaPlayer != None:
            self.parent.mediaPlayer.setPosition(position)
    
    def positionChanged(self, position):  
        if self.parent.sliderVisible == True:  
            self.parent.slider.setValue(position)     
            
    def durationChanged(self, duration):
        if self.parent.sliderVisible == True: 
            self.parent.slider.setRange(0, duration)  
  
### --------------------------------------------------------
    def openHelpMenu(self):
        if self.parent.helpFlag == True:
            self.closeHelpMenu()
        else:
            self.parent.helpMenu = Help(self.parent)
            self.parent.helpFlag = True
            
    def closeHelpMenu(self):
        if self.parent.helpMenu != None: 
            self.parent.helpMenu.tableClose()
            self.parent.helpMenu.close()
            self.parent.helpFlag = False
            time.sleep(.03)
            
    def closeOnOpen(self):   ## <- "one"
        self.closeHelpMenu();   
        self.parent.clips.closeSettings()
        time.sleep(.03)  
        self.parent.clips.looperOff() 
        if self.parent.mediaPlayer != None:
            self.stopVideo()
                  
    def closeMediaPlayer(self):   ## <- "two"
        if self.parent.mediaPlayer != None: 
            self.stopVideo() 
            time.sleep(.03)  
            self.parent.clips.looperOff()
            self.parent.scene.removeItem(self.parent.mediaPlayer.backdrop)
            self.parent.scene.removeItem(self.parent.videoItem) 
            self.parent.videoItem = None
            self.parent.mediaPlayer = None 
            time.sleep(.03)      

### --------------------------------------------------------
    def msgbox(self, str):
        msg = QMessageBox()
        msg.setText(str)
        timer = QTimer(msg)
        timer.setSingleShot(True)
        timer.setInterval(5000)
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
    
    def showHideAspectBtn(self):   ## <- "one"
        self.parent.aspButton.show() if self.parent.width() > VertW \
            else self.parent.aspButton.hide()
        
    def toggleSlider(self):
        self.parent.flag = True
        if self.parent.sliderVisible and self.parent.height() > MinHgt+PAD: 
            self.parent.sliderVisible = False  
            self.parent.slider.hide()
            self.parent.resize(self.parent.width(), self.parent.height()-PAD)
            time.sleep(.03)      
        elif self.parent.sliderVisible == False:
            self.parent.slider.show()
            self.parent.sliderVisible = True
            self.parent.resize(self.parent.width(), self.parent.height()+PAD)
            time.sleep(.03)    
        
### --------------------------------------------------------            
    def zoom(self, zoom):   ## <- "one"
        if self.parent.mediaPlayer != None:  
            if int(self.parent.height() * zoom) > 1280 or int(self.parent.height()* zoom) < 300:
                return  
                
            asp = 0    
            if self.parent.aspect == 0 and (self.parent.key != '' and self.parent.key != 'O'):
                self.parent.aspect = Keys[self.parent.key][0]  
                      
            elif self.parent.key == 'O' and self.parent.aspect > 0:  ## horizontals
                asp = self.parent.aspect
                nwidth = self.parent.lastVWidth
                
            if self.parent.aspect != 0:
                asp = self.parent.aspect
                
            elif asp == 0:
                self.msgbox('The Aspect Ratio Has Not Been Set')
                return 
                                                       
            height = int(self.parent.height()* zoom)  ## new height  
            
            nvH = (height - HGT)  ## new video height
            nvW = int(nvH * asp)  ## new video width   
            nwidth = nvW + WID    ## new widget width   
            
            p, width = self.parent.pos(), self.parent.width()  
            self.parent.resize(nwidth, height)   
            dif = int((self.parent.width() - width)/2) 
            self.parent.move(p.x()-dif, p.y()) 
                 
            self.parent.ViewW, self.parent.ViewH = self.parent.width()-WID, self.parent.height()-HGT 
            
            self.showHideAspectBtn()
                                      
### -------------------------------------------------------           
def getDirection(self):  ## left out top, topleft and topright - feel free to add them
    corner, which = 5, ''      
    pos = self.mapFromGlobal(QCursor.pos())
    
    bottomLeft  = self.rect().bottomLeft()
    bottomRight = self.rect().bottomRight()
        
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

### --------------------------------------------------------
def setSlider(self):
    self.slider = QSlider(Qt.Orientation.Horizontal)
    self.slider.sliderMoved.connect(self.shared.setPosition)
    self.slider.setFixedHeight(30)
    
    self.slider.setStyleSheet("""                                        
        QSlider::groove:horizontal {
            background-color: #ccc;
            height: 3px;
        }     
        QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #e4e4e4, stop:1 #4f4f4f);
            border: 1px solid rgb(105,105,105);
            width: 11px;
            margin: -7px 0;
            border-radius: 3px;
        }
    """)

    return self.slider
                           
### --------------------------------------------------------
def setButtons(self):
    self.buttonGroup = QLabel()
    self.buttonGroup.setFixedHeight(45)
        
    self.openButton = QPushButton("Files")
    self.playButton = QPushButton("Play")  
    if self.player == "one":                ## <- "one"
        self.aspButton   = QPushButton("Aspect")
    self.loopButton = QPushButton("Loop")
    self.stopButton = QPushButton("Stop")
    self.byeButton  = QPushButton("Quit")
    
    self.openButton.clicked.connect(self.clips.openFile) if self.player == "one"\
        else  self.openButton.clicked.connect(self.openFile)         ## <- "one"
    
    self.playButton.clicked.connect(self.shared.playVideo)
    if self.player == "one":
        self.aspButton.clicked.connect(self.setAspButton)
    self.loopButton.clicked.connect(self.clips.looper)
    self.stopButton.clicked.connect(self.shared.stopVideo)
    self.byeButton.clicked.connect(self.bye)

    hbox = QHBoxLayout(self)
            
    hbox.addWidget(self.openButton)  
    hbox.addWidget(self.playButton)    
    if self.player == "one":                 ## <- "one"
        hbox.addWidget(self.aspButton)
    hbox.addWidget(self.loopButton)    
    hbox.addWidget(self.stopButton)  
    hbox.addWidget(self.byeButton)
    
    self.buttonGroup.setLayout(hbox)
    self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
    self.buttonGroup.setLineWidth(1)
    
    hbox = QHBoxLayout(self)
    hbox.addWidget(self.buttonGroup)

    self.bGroup = QLabel()
    self.buttonGroup.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    self.bGroup.setFixedHeight(60)
    self.bGroup.setLayout(hbox)
    
    return self.bGroup
      
### --------------------------------------------------------
### detect video width and height to set aspect ratio 
### --------------------------------------------------------
def getMetaData(path):   
    
    ''' requires opencv-python - may not always report width/height correctly 
        for non 9:16 verticals - initial method - not mac specific '''
    # try:  
    #     import cv2  ## <<---------------------  
    #     try:
    #         cap = cv2.VideoCapture(path) 
    #     except:
    #         return 0,0
    #     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #     cap.release()
    #     return width, height
    # except:
    #     return 0, 0
    
    ''' uses mdls - mac only - reports non 9:16 vertical width and height correctly -- 
        drag and drop doesn't work in pyqt5 on desktop '''  
    # try:  
    #     result = subprocess.run(
    #         ['mdls', '-name', 'kMDItemPixelWidth', '-name', 'kMDItemPixelHeight', path],
    #         capture_output=True,
    #         text=True,
    #         check=True
    #         )
    #     output = result.stdout
    #     width, height = None, None
    #     for line in output.splitlines():
    #         if 'kMDItemPixelWidth' in line:
    #             width = int(line.split('=')[-1].strip())
    #         elif 'kMDItemPixelHeight' in line:
    #             height = int(line.split('=')[-1].strip())
    #         del line
    #     return width, height
    # except Exception:
    #     return 0, 0
    

    ''' uses ffprobe -- may not always report width/height correctly for non 9:16 verticals
        and blows up if run from mac desktop -- works well in vscode '''
    # try: 
    #     result = subprocess.run(
    #         ['ffprobe', '-v', 'error', '-select_streams',  'v:0', '-show_entries', 'stream=width,height','-of', 'csv=s=,:p=0', path],
    #         capture_output=True,
    #         text=True,
    #         check=True
    #     )
    #     res = result.stdout.strip()
    #     i = res.index(',')
    #     width, height = res[0:i], res[i+1:]
    #     return int(width), int(height) 
    # except Exception:
    #     return 0, 0
           
        
### ---------------------- that's all ---------------------- 
 


