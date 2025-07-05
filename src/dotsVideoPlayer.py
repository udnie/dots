
import os
import time

from PyQt6.QtCore       import Qt, QUrl, QSizeF, QRectF, QTimer, QRect, QPoint, QSize  
from PyQt6.QtGui        import QColor, QPen, QPainter                          
from PyQt6.QtWidgets    import QWidget, QHBoxLayout, QGroupBox, QLabel,QSlider,\
                                QPushButton, QVBoxLayout
                                
from PyQt6.QtMultimedia         import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets  import QGraphicsVideoItem
### ------------ comment out for 6, uncomment for 5 -----------------
# from PyQt5.QtMultimedia       import QMediaContent  ## 5 

### ---------------------------- end --------------------------------
from dotsSideGig        import getVuCtr
from dotsSideGig        import MsgBox
from dotsShared         import common, Ball

### --------------------------------------------------------
class QVD(QGraphicsVideoItem):  ## added type to track it better
### --------------------------------------------------------
     def __init__(self):
          super().__init__()          
         
          self.type = 'video'

### ------------------ dotsVideoPlayer ---------------------        
class VideoPlayer(QMediaPlayer):
### --------------------------------------------------------
    def __init__(self, parent, fileName='', src='', loops=1):
        super().__init__()

        self.canvas = parent 
        self.scene  = self.canvas.scene
         
        self.fileName = ''
        self.type    = 'video'
        self.tag     = src
        self.loops   = loops
        self.widget  = None 
        self.backdrp = None
    
        if fileName != '': self.fileName = os.path.basename(fileName)

### ------------ comment out for 5, uncomment for 6 -----------------
        self.mediaPlayer = QMediaPlayer(self)   ## 6
        # self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)  ## 5
### ---------------------------- end --------------------------------
        
        self.videoWidget = QVD()   
        self.videoWidget.setZValue(self.canvas.mapper.toFront(100)) 
        
        self.videoWidget.setSize(QSizeF(common['ViewW'], common['ViewH']))  
        self.mediaPlayer.setVideoOutput(self.videoWidget) 
           
        self.mediaPlayer.mediaStatusChanged[QMediaPlayer.MediaStatus].connect(self.mediaStateChanged) 
        # self.mediaPlayer.error.connect(self.handleError)  ## 5
        
### ------------ comment out for 5, uncomment for 6 -----------------
        self.mediaPlayer.setLoops(self.loops)  ## 6 -- note!!! doesn't work in 5
        self.audioOut = QAudioOutput()  ## 6
        self.mediaPlayer.setAudioOutput(self.audioOut)  ## 6     
        self.mediaPlayer.setSource((QUrl.fromLocalFile(fileName)))  ## 6
### ------------ uncomment for 5, comment out for 6 -----------------     
        # self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(fileName))))  ## 5
### ---------------------------- end --------------------------------
### ------------ uncomment for 6 ... comment out for 5 ----------------- 
    def playVideo(self):  ## 6
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:  ## 6
            self.mediaPlayer.pause()  ## 6
        else:  ## 6
            if self.backdrp == None:  ## 6
                self.videoWidget.setZValue(self.canvas.mapper.toFront(100))  ## 6
                self.setFrame()  ## 6
                time.sleep(.20)  ## 6
            self.mediaPlayer.play()  ## 6 
 
    def mediaStateChanged(self, status):  ## 6
        if status == QMediaPlayer.MediaStatus.EndOfMedia:  ## 6
            while not (self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.StoppedState):  ## 6
                time.sleep(.01)  ## 6
            self.stopVideo()  ## 6
                                           
### ------------ uncomment for 5 ... comment out for 6 -----------------
    # def playVideo(self):  ## 5
    #     if self.mediaPlayer.state() == QMediaPlayer.PlayingState:  ## 5
    #         self.mediaPlayer.pause()  ## 5
    #     else:  ## 5
    #         if self.backdrp == None:  ## 5
    #             self.videoWidget.setZValue(self.canvas.mapper.toFront(100)) ## 5
    #             self.setFrame()  ## 5
    #             time.sleep(.20)  ## 5
    #         self.mediaPlayer.play()  ## 5 
   
    # def mediaStateChanged(self, status):  ## 5
    #     if status == QMediaPlayer.MediaStatus.EndOfMedia:  ## 5
    #         while not (self.mediaPlayer.state() == QMediaPlayer.State.StoppedState):  ## 5
    #             time.sleep(.01)  ## 5
    #         self.stopVideo()  ## 5
### ---------------------------- end --------------------------------
### -----------------------------------------------------------------
    def setFrame(self):   
        self.mediaPlayer.setPosition(0)
        self.mediaPlayer.pause()
        QTimer.singleShot(200, self.copyFrame) 

    def copyFrame(self):       
        pix = self.canvas.view.grab(QRect(QPoint(0,0),QSize()))
        self.backdrp = Ball(pix.toImage(), self.canvas)  ## subclass - borrowed
        self.backdrp.setZValue(-100)  ## copy is a graphics pixmapItem 
        self.scene.addItem(self.backdrp)        
        self.videoWidget.setZValue(-99)  ## reset behind sprites
        if self.tag == 'dnd': self.mediaPlayer.play()  
        
    def handleError(self):
        MsgBox(self.mediaPlayer.errorString())
        return

    def stopVideo(self):
        try:
            self.mediaPlayer.stop() 
            if self.canvas.animation == False and  \
                self.canvas.openPlayFile not in ('snakes', 'bats', 'hats'):            
                self.canvas.showWorks.enablePlay()  
        except:
            return

    def setVideo(self, tmp, pix):  ## some of which is filler
        pix.fileName = tmp['fileName']  ## the better to fit in
        pix.type =  'video'           
        pix.x   = float(f"{tmp['x']:.2f}")
        pix.y   = float(f"{tmp['y']:.2f}")
        pix.setZValue(-99)
        pix.tag     = tmp['tag']        
        pix.locked  = False  
        pix.loops   = tmp['loops']

    def saveVideo(self):      
        tmp = {
            'fileName':      os.path.basename(self.canvas.videoPlayer.fileName),
            'type':         'video',     
            'x':            float(f'{0:.2f}'),
            'y':            float(f'{0:.2f}'),
            'z':            -99,
            'tag':          'Vertigo',
            'locked':       False,
            'loops':        self.loops,    
        }
        return tmp
 
### --------------------------------------------------------        
class AVideoWidget(QWidget):   ## so as not confused with the videoWidget
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()

        self.canvas = parent
        self.factor  = self.canvas.videoPlayer.loops
        
        self.playfile = os.path.basename(self.canvas.openPlayFile) 
     
        self.type = 'widget' 
        self.setAccessibleName('widget')
   
        self.WidgetW, self.WidgetH = 320.0, 220.0
        
        vbox = QVBoxLayout()     
        self.label = QLabel(self.canvas.videoPlayer.fileName, alignment=Qt.AlignmentFlag.AlignCenter)        
        vbox.addWidget(self.label)
       
        hbox = QHBoxLayout() 
        hbox.addWidget(self.sliderGroup())  
        hbox.addWidget(self.buttonGroup())
        
        hbox.addSpacing(10)   
        vbox.addLayout(hbox)
        
        self.playfile = QLabel(self.playfile, alignment=Qt.AlignmentFlag.AlignHCenter)
        vbox.addWidget(self.playfile)
        self.setLayout(vbox)
    
        self.setFixedHeight(int(self.WidgetH))  
        self.setStyleSheet('background-color: transparent')
      
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.Window| \
            Qt.WindowType.CustomizeWindowHint| \
            Qt.WindowType.WindowStaysOnTopHint)
                                
        x, y = getVuCtr(self.canvas) 
        self.move(x-int(self.WidgetW/2),y-160)
                                                                                    
        self.show()

### --------------------------------------------------------
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)   
        rect = QRectF(2, 2, self.WidgetW-4, self.WidgetH-4)                   
        painter.setPen(QPen(QColor(0, 80, 255), 5, Qt.PenStyle.SolidLine,            
            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QColor(225, 100, 30, 255))
        painter.drawRoundedRect(rect, 15, 15)
    
    def setLoopCount(self, val):
        self.factor = val
        self.loopSlider.setValue(val)
        self.factorValue.setText(f'{val}')
        self.canvas.videoPlayer.loops = val
  
    def sliderGroup(self):
        groupBox = QGroupBox()
        groupBox.setFixedWidth(150) 
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')

        self.title =  QLabel('Set Loops', alignment=Qt.AlignmentFlag.AlignHCenter)
     
        self.loopSlider = QSlider(Qt.Orientation.Horizontal)   
        self.loopSlider.setMinimum(1)
        self.loopSlider.setMaximum(10)
        self.loopSlider.setSingleStep(1)
        self.loopSlider.setValue(self.factor)
        self.loopSlider.setTickInterval(1)  
        self.loopSlider.valueChanged.connect(self.setLoopCount)   

        self.factorValue = QLabel(str(self.factor),  alignment=Qt.AlignmentFlag.AlignHCenter)
        self.factorValue.setFixedWidth(40)
      
        vbox = QVBoxLayout()    
        vbox.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        vbox.addSpacing(5)   
        vbox.addWidget(self.loopSlider, alignment=Qt.AlignmentFlag.AlignCenter) 
        vbox.addSpacing(5)     
        vbox.addWidget(self.factorValue, alignment=Qt.AlignmentFlag.AlignCenter)
      
        groupBox.setLayout(vbox)
        return groupBox     
    
    def buttonGroup(self):
        groupBox = QGroupBox()
        groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        groupBox.setFixedWidth(115)
        groupBox.setStyleSheet('background: rgb(245, 245, 245)')
      
        deleteBtn = QPushButton('Delete') 
        runBtn    = QPushButton('Run')     
        saveBtn   = QPushButton('Save') 
        quitBtn   = QPushButton('Close') 
                                
        deleteBtn.clicked.connect(self.delete)
        runBtn.clicked.connect(lambda: self.canvas.setKeys('R'))
        saveBtn.clicked.connect(self.save)
        quitBtn.clicked.connect(self.bye)
          
        vbox = QVBoxLayout(self)
        vbox.addWidget(deleteBtn)
        vbox.addWidget(runBtn)
        vbox.addWidget(saveBtn)
        vbox.addWidget(quitBtn)
                
        groupBox.setLayout(vbox)
        return groupBox 
   
### -------------------------------------------------------- 
    def save(self):  
        self.canvas.showbiz.showtime.savePlay()
    
    def delete(self):  
        name, fsize = '', 0
        name = os.path.basename(self.canvas.openPlayFile) 
        if name != '':
            fsize = len(self.canvas.showbiz.showRunner.openPlay(self.canvas.openPlayFile))   
        if fsize == 1:
            try:
                os.remove(self.canvas.openPlayFile)     
            except IOError:
                MsgBox('Error deleting file ' + name, 5)
            MsgBox('The file ' + name + ' has been deleted', 7)  
        elif fsize > 1:
            MsgBox('Save the play file to finalize removing the video', 7)
        self.canvas.sideCar.videoOff() 
           
    def bye(self):
        self.canvas.sideCar.closeVideoWidget()
      
### ------------------ dotsVideoPlayer --------------------- 


