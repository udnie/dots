
import sys
import os
import math

from PyQt6.QtCore    import Qt, QPoint, QPointF, QTimer
from PyQt6.QtGui     import QImage, QPixmap, QGuiApplication, QFont, QColor
from PyQt6.QtWidgets import QWidget, QApplication, QGraphicsView, \
                            QGraphicsScene, QGraphicsPixmapItem, QLabel, \
                            QHBoxLayout,  QVBoxLayout, QPushButton, QMessageBox, \
                            QFileDialog, QFrame, QGraphicsTextItem, QTableWidget, \
                            QTableWidgetItem, QAbstractItemView

Width, Height = 1400,    900 ## widget size and SceneRectSize - see pixXY
ViewW, ViewH  = 1360,    860 ## scene size - for a moment
MaxW, MaxH, MaxV = 1100, 650, 770 

# Width, Height = 900,    900 ## widget size and SceneRectSize - see pixXY
# ViewW, ViewH  = 860,    860 ## scene size - for a moment
# MaxW, MaxH, MaxV = 550, 550, 550

# Width, Height = 1500,   1000 ## widget size  ## reset setGeometry(x, y = to 150  from 200
# ViewW, ViewH  = 1460,    960 ## scene size
# MaxW, MaxH, MaxV = 1200, 650, 800 

# Width, Height    = 1300,  800  ## widget size
# ViewW, ViewH     = 1260,  760  ## scene size - widget height and width - 40 for framing
# MaxW, MaxH, MaxV = 1060,  560, 660  ## max width, height and vertical

helpKeys = {
    'C':                'Clear Screen',  
    'F ':               'File Chooser', 
    'H ':               'Help Menu On/Off',
    'Right Arrow, N':   'Next Slide',
    'Left Arrow, B':    'Previous Slide',
    'O':                'Opening Layout',
    'R, L':             'Rotate 90.0',
    'S, SpaceBar':      'Slide Show',
    'T':                'Text On/Off',   
    'W':                'Where am I?', 
    'Square Brackets [ ]':  'Zoom In/Out',
    'X, Q, Escape':     'Quit/Exit',
}

### --------------------- slideShow.py ---------------------
''' slideShow.py: works with '.png', '.jpg', '.jpeg', '.tif', '.tiff', '.webp' '''
### --------------------------------------------------------
class SlideShow(QWidget): 
### --------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__()
    
        self.setWindowTitle("SlideShow")
            
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(0, 0, ViewW, ViewH)
         
        self.view.setScene(self.scene)                 

        self.view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)   
        self.view.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus);  self.setFocus()
        
        self.ctr = QGuiApplication.primaryScreen().availableGeometry().center()    
        x = int(((self.ctr.x() * 2 ) - Width)/2)
     
        # self.setStyleSheet("QWidget {\n"  ##  makes widget one color <<< -------------[3]
        #     "background-color: rgb(250,250,250);\n"
        #     "border: 1px solid rgb(250,250,250);\n"
        #     "color: rgb(250,250,250);\n"      
        #     "}")
        
        ## in qt5 framelessWindow won't resize with mouse - use zoom keys instead   <<<---------------[2]
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
   
        self.setGeometry(x, 200, Width, Height)   
        
        self.init()
        
        self.delay   = 2000  ## slide show 
        self.setTags = True  ## toggle textItems <<<------------------------[4]
        self.buttons = False ## set to true if setButtons added to layout
        
        vbox = QVBoxLayout()      
        vbox.addWidget(self.view)
        vbox.addWidget(self.setButtons())  ## will hide tags when visible <<<------------[1]
        self.setLayout(vbox)
    
        self.grabKeyboard()
        
        QTimer.singleShot(25, self.openFiles)  ## always

        self.show()
        
### --------------------------------------------------------
    def init(self):  ## on each new directory
        self.files       = []   
        self.txtlst     = []
        self.fileName    = ''
        self.path       = ''  
        self.current    = 0
        self.rot        = 0
        self.running    = False  ## used by slideshow
        self.save       = QPointF()
        self.pixmap     = None 
        self.textItem   = None
        self.table      = None
     
    def keyPressEvent(self, e):
        mod = e.modifiers()
        if e.key() in (Qt.Key.Key_X, Qt.Key.Key_Q, Qt.Key.Key_Escape):
            self.clearScene()
            self.close()
        elif e.key() in (Qt.Key.Key_N, Qt.Key.Key_Right):
            self.nextSlide()
        elif  e.key() in (Qt.Key.Key_B, Qt.Key.Key_Left):
            self.backOne()
        elif e.key() == Qt.Key.Key_C:
            self.clearScene()
        elif e.key() == Qt.Key.Key_F:
            self.openFiles()
        elif e.key() == Qt.Key.Key_H:
            self.helpMenu()    
        elif e.key() in (Qt.Key.Key_L, Qt.Key.Key_R):
            self.rotateThis(90)
        elif e.key() == Qt.Key.Key_O:
            self.openingLayout()   
        elif e.key() in (Qt.Key.Key_S, Qt.Key.Key_Space):
            self.slideShow()
        elif e.key() == Qt.Key.Key_T:
            self.toggleText()
        elif e.key() == Qt.Key.Key_W:
            if self.path != '': self.errMsg(self.path) 
        elif e.key() in (Qt.Key.Key_BracketRight, Qt.Key.Key_BracketLeft):
            self.zoom(1.10) if e.key() == Qt.Key.Key_BracketRight else self.zoom(.90)
          
    def mousePressEvent(self, e):
        self.save = e.globalPosition() 
        e.accept()
        
    def mouseMoveEvent(self, e):
        self.moveThis(e)
        e.accept()
     
    def mouseReleaseEvent(self, e):
        self.moveThis(e)
        e.accept()       
      
    def moveThis(self, e):
        dif = e.globalPosition() - self.save      
        self.move(self.pos() + QPoint(int(dif.x()), int(dif.y())))
        self.save = e.globalPosition()
      
### --------------------------------------------------------       
    def addPixmap(self, file):  ## the scene is cleared each new file  
        if self.pixmap != None:
            self.scene.removeItem(self.pixmap)
            del self.pixmap
            
        if self.table != None: self.helpStop()  ## close help menu   
              
        self.fileName = self.path + '/' + file  
        try:
            img = QImage(self.fileName) 
        except:
            self.errMsg('addPixMap: problem with ' + file)
            return
    
        maxH = MaxH  ## set default       
        self.txtlst = [file, img.width(), img.height()]  ## save it for textItem
     
        if self.rot in (90, 270) and abs(img.width() - img.height()) > 5:  ## swap width to height for rotatation
            img = img.scaled(MaxV, int(ViewH * (self.height()/Height)),  ## limit height
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation) 
        else:
            if img.height() > img.width() and abs(img.width() - img.height()) > 5:
                maxH = MaxV   ## set height for vertical
            img = img.scaled(MaxW, int(maxH * (self.height()/Height)),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)  
    
        self.pixmap = QGraphicsPixmapItem()          
        self.pixmap.setPixmap(QPixmap(img))  
         
        self.pixmap.setZValue(0)
        self.pixmap.setPos(self.pixXY())
        
        self.scene.addItem(self.pixmap)
  
        if self.setTags == True and int(ViewH * (self.height()/Height ) > 500): ## optional
            self.addTextItem()           
        del img
    
        self.update()    
     
### --------------------------------------------------------    
    def pixXY(self):          
        self.scene.setSceneRect(0.0, 0.0, \
            float(self.width()),\
            float(self.height()))   
   
        scaleH = self.height()/Height
  
        self.setOrigin()  
                      
        self.pixmap.setRotation(self.rot) 
        self.pixmap.setScale(scaleH) 
                                                   
        # print(f'Height {Height}\t height() {self.height()}\t sceneH {self.scene.height()}\t viewH {int(ViewH*scaleH)}')
                                                                                               
        w, W = int(self.pixmap.boundingRect().width()),  int(self.width()) 
        h, H = int(self.pixmap.boundingRect().height()), int(self.height())  ## more framing
   
        x = int(W/2)- int(w/2)  
        y = int(H/2)- int(h/2)
        
        return QPointF(x-20, y-20)  ## subtract framing
                             
### --------------------------------------------------------  
    def zoom(self, zoom):
        if self.pixmap != None: 
            self.scene.setSceneRect(0.0, 0.0, \
                float(self.width()),\
                float(self.height()))  
            
            p, width = self.pos(), self.width()        
            self.resize(int(self.width()* zoom), int(self.height()* zoom))  
             
            dif = int((self.width() - width)/2) 
            self.move(p.x()-dif, p.y())     
            self.updTextItem()  
         
    def openingLayout(self):
        if self.pixmap != None:
            self.scene.setSceneRect(0.0, 0.0, \
                float(self.width()),\
                float(self.height()))    
            x = int(((self.ctr.x() * 2 ) - Width)/2)
            self.setGeometry(x, 200, Width, Height) 
            self.pixmap.setPos(self.pixXY())
           
### --------------------------------------------------------               
    def resizeEvent(self, e):  
        if self.pixmap != None:  
            self.pixmap.setPos(self.pixXY())
            self.updTextItem()
        e.accept()
          
    def rotateThis(self, r=0):
        if self.pixmap != None:  
            if self.rot != 0:
                r = r + self.rot
            if r > 270: r = 0
            self.rot = r
            self.addPixmap(self.files[self.current])  ## needs a refresh          
                        
    def nextSlide(self):
        if length := len(self.files):
            if self.current >= 0 and self.current < length:
                self.current += 1
                if self.current == length:
                    self.current = 0   
            self.rot = 0
            self.addPixmap(self.files[self.current])
            
    def backOne(self):
        if length := len(self.files):
            if self.current >= 0 and self.current <= length:
                self.current -= 1
                if self.current < 0:
                    self.current = length -1
            self.rot = 0
            self.addPixmap(self.files[self.current])
                   
### --------------------------------------------------------
    def addTextItem(self):   
        if self.buttons == True:  
            return
        elif self.textItem != None:
            self.scene.removeItem(self.textItem)
            del self.textItem 
        self.textItem = self.tagIt()   
        if self.textItem == None: 
            return     
        self.textItem.setZValue(100) 
        self.textItem.setPos(self.textXY()) 
        self.scene.addItem(self.textItem)
        
    def textXY(self):    
        self.scene.setSceneRect(0.0, 0.0, \
            float(self.width()),\
            float(self.height()))    
           
        scaleH = self.height()/Height     
      
        w, W = self.textItem.boundingRect().width(),  int(self.width())  
        h, H = self.textItem.boundingRect().height(), int(ViewH * scaleH)
        x, y = int((W - w)/2),  int((H-(h)))

        return QPointF(x, y)
    
    def updTextItem(self):
        if self.setTags == True and self.textItem != None:
            if int(ViewH * (self.height()/Height )) > 400: 
                self.textItem.setPos(self.textXY()) 
                
### --------------------------------------------------------         
    def clearScene(self):
        self.helpStop()
        self.scene.clear()  
        self.init() 
            
    def errMsg(self, str=''):
        msg = QMessageBox()
        msg.setText(str)
        msg.exec()
        
    def helpMenu(self):
        if self.table != None: 
            self.table.tableClose()
            self.table = None
        else:
            self.table = Help(self)
            
    def helpStop(self):
        if self.table != None:
            self.table.tableClose()
            self.table = None
                                   
    def setOrigin(self):   
        b = self.pixmap.boundingRect()
        op = QPointF(b.width()/2, b.height()/2)
        self.pixmap.setTransformOriginPoint(op)
        self.pixmap.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                                                                                                                 
    def slideShow(self):     
        self.showtime() if self.running == False else self.timerStop()
      
    def showtime(self):
        self.running = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.nextSlide)
        self.timer.start(self.delay)
  
    def timerStop(self):
        self.timer.stop()
        self.running = False
        
    def tagIt(self):   
        try:
            file, width, height = self.txtlst[0], self.txtlst[1], self.txtlst[2]   
            asp = math.floor(width/height *100)/100.0  
        except:
            self.errMsg('tagIt: problem with ' + file)
            return None
        textItem = QGraphicsTextItem(f"{file} {width}X{height} asp {asp}")
        font = QFont("Arial", 14)
        textItem .setFont(font)
        return textItem
    
    def toggleText(self):   
        if self.pixmap != None:    
            if self.setTags == False:
                self.setTags = True
                self.addTextItem()
            elif self.textItem != None:
                self.scene.removeItem(self.textItem)
                self.textItem = None
                self.setTags = False
        
### --------------------------------------------------------
    def openFiles(self):
        self.clearScene()  ## calls self.init()
        if list := self.getPathList():
            files = self.getFileNames(list)
            if files != None:
                self.files = sorted(files)
                self.addPixmap(self.files[0]) 
                if len(self.files) == 1:
                    self.errMsg('openFiles: Only One Matching File')
                              
    def getPathList(self):
        if len(sys.argv) > 1:  ## set starting directory
            self.path = sys.argv[1]
        else:
            self.path = os.getcwd()  
        self.path = QFileDialog.getExistingDirectory(self, '', self.path)
        if self.path == '':
            return None
        else:
            try:                        
                files = os.listdir(self.path)
                return files
            except IOError:
                self.errMsg('getPathList: Error on Directory')
                return None
                  
    def getFileNames(self, files):       
        filenames = []
        for file in files: 
            path = os.path.join(self.path, file)
            if os.path.isdir(path):  ## ignore directories
                continue
            file = file.lower();  ext = file[file.rfind('.'):]
            if ext in ('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.webp'):                  
                filenames.append(file)
        if len(filenames) == 0:
            self.errMsg('getFileNames: No Files Found')
            return None
        return filenames
                                         
### --------------------------------------------------------    
    def setButtons(self): 
        self.buttonGroup = QLabel()
        self.buttonGroup.setFixedHeight(50)
        self.buttons = True
 
        self.buttonGroup.setStyleSheet("QPushButton {\n"               
            "max-width:   200px;\n"
            "max-height:  40px;\n"  ## 30 must be the default
            "font-size:    13px;\n"
            "}")   
        
        self.filesBtn = QPushButton("Files")  
        self.helpBtn = QPushButton("Help")
        self.clearBtn = QPushButton("Clear")
        self.quitBtn = QPushButton("Quit")        
          
        self.filesBtn.clicked.connect(self.openFiles)
        self.helpBtn.clicked.connect(self.helpMenu)
        self.clearBtn.clicked.connect(self.clearScene)
        self.quitBtn.clicked.connect(self.close)
        
        hbox = QHBoxLayout(self)
        hbox.addSpacing(50)       
        hbox.addWidget(self.filesBtn)
        hbox.addSpacing(50)        
        hbox.addWidget(self.helpBtn)
        hbox.addSpacing(50)       
        hbox.addWidget(self.clearBtn)
        hbox.addSpacing(50)
        hbox.addWidget(self.quitBtn)
            
        self.buttonGroup.setLayout(hbox)
        self.buttonGroup.setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
        self.buttonGroup.setLineWidth(1)
  
        return self.buttonGroup

### --------------------------------------------------------     
class Help(QWidget): 
### -------------------------------------------------------- 
    def __init__(self, parent): 
        super().__init__()  
        
        self.parent = parent
         
        self.table = QTableWidget()
        self.table.setRowCount(len(helpKeys)+1)
        self.table.setColumnCount(2)
     
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
      
        self.table.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) 
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.table.setHorizontalHeaderLabels(["Key", "Function"])
        stylesheet = "::section{Background-color: lightgray; font-size:14px;}"
        self.table.horizontalHeader().setStyleSheet(stylesheet)
        
        self.table.setStyleSheet('QTableWidget{\n'   
            'background-color: rgb(250,250,250);\n'                 
            'font-size: 13pt;\n' 
            'font-family: Arial;\n' 
            'border: 3px solid dodgerblue;\n'
            'gridline-color: silver;}') 
                                                                                                             
        self.table.setColumnWidth(0, 130) 
        self.table.setColumnWidth(1, 130)

        width, height = 267, 421
        self.table.setFixedSize(width, height)  
        
        self.table.verticalHeader().setVisible(False) 
        self.table.clicked.connect(self.bye)  
         
        row = 0
        for k,  val in helpKeys.items():
            item = QTableWidgetItem(k)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item)
            item = QTableWidgetItem(val)
            self.table.setItem(row, 1, item)      
            row += 1
                  
        item = QTableWidgetItem("Enter 'H' or Click Here to Close")
        item.setBackground(QColor('lightgray'))
        item.setFont(QFont("Arial", 14))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.table.setSpan(row, 0, 1, 2)  
        self.table.setItem(row, 0, item)   
        
        p, pwidth, pheight = self.parent.pos(), self.parent.width(), self.parent.height()
        
        x = int(p.x() + (pwidth/2)) - int(width/2)   
        y = int(p.y() + (pheight/2)) - int(height/2)   
        
        self.table.move(x,y)  ## no matter where you go, there you are - Jim, Taxi
        self.table.show()

    def tableClose(self):
        self.table.close()
        
    def bye(self):
        QTimer.singleShot(0, self.parent.helpStop)

### -------------------------------------------------------- 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    slides = SlideShow()
    sys.exit(app.exec())

### ---------------------- that's all ----------------------
    

 
    