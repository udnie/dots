
import sys
import platform
import os
     
from PyQt6.QtCore       import QTimer  ### QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.QtWidgets    import QStatusBar, QMainWindow, QApplication

from dotsScreens        import *   ## including pathMod
from dotsShared         import common, Verts

import dotsStoryBoard   as canvas

### ----------------------- dotsQt -------------------------
''' dotsQt: parent container for the major widgets.
    See dotsShared.py for common,,,,, shared variables and      
    dictionaries shared across classes and files''' 
### --------------------------------------------------------
class DotsQt(QMainWindow):
### --------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__()

        self.msg = ''  ## just in case there's something to add 
        self.Vertical = False
                                                            
        p = QGuiApplication.primaryScreen().availableGeometry()

        ## make sure it can be displayed
        if len(sys.argv) > 1 and sys.argv[1] in MaxScreens and p.width() < MaxWidth:  
            sys.argv[1] = '1080'
            self.msg = sys.argv[1]  ## default to 1080, too wide for display
                             
        self.saveCommon = common.copy()  ## refreshes common - see switch
                   
        if len(sys.argv) > 1:  ## if there's no match it defaults to 1080
            self.screen = setCommon(sys.argv[1])  ## setCommon in screens
        else:
            self.screen = setCommon()  ## default - 1080X720 
           
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar) 
                  
        self.init()
        
        # print("\n" + "PyQt version:", PYQT_VERSION_STR) 
        # print(f'Python: {platform.python_version()}'+ "\n")
     
    def init(self):  
        self.setWindowTitle('DotsQt:  ' +  f'{pathMod((os.getcwd()))} ~ {self.screen}')
  
        self.setStyleSheet(open('./dotsStyle.css').read())   
        self.setFixedSize(common['DotsW'], common['DotsH'])
                               
        self.canvas = canvas.StoryBoard(self)
        self.setCentralWidget(self.canvas)

        ## adjusted for app size and display, see getY() for '900' screen
        vert = 50 if self.Vertical == True else 150 ## was 150
        if common['Screen'] == 'SQV': vert = 150
        self.move(getX(), vert)   ###getY()-int(vert/4))  ## functions in screens 

        ## can't all happen at once
        QTimer.singleShot(100, self.canvas.scroll.loadSprites)
        QApplication.setQuitOnLastWindowClosed(True)  ## always
                         
        QTimer.singleShot(100, self.show)
                     
### -------------------------------------------------------
    def closeEvent(self, e):
        self.canvas.exit()
   
    def closeAll(self):  ## close all app widgets
        self.canvas.close()   
        self.canvas.keysPanel.close()
        self.canvas.scroll.close()     
        self.canvas.keysDock.close()
        self.canvas.scrollDock.close()
        self.canvas.buttonDock.close()    
                   
    def switch(self, key):  ## from screenMenu in screens
        QApplication.setQuitOnLastWindowClosed(False)
        self.closeAll()
        if key in Verts: 
            self.Vertical = True
        else:
            self.Vertical = False               
        common = self.saveCommon.copy()  ## copy it back
        self.screen = setCommon(key)  ## in dotsScreens   
        self.init()
                                                                                                 
### --------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)  
    dots = DotsQt(sys.argv)
    sys.exit(app.exec())    

### ------------------------- dotsQt ----------------------








