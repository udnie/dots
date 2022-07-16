## Changes
**July 2022:**		 
**Qt-warnings** are gone - thanks to **Qt** for providing a one-line fix, setting a QGraphicsView attribute took care of it. **SpriteMaker** is now fully standalone-alone other than using the **demo sprites** and **txy folders.**  It's also now able to run in **PySide6.3.1** with some minor edits.  You will need to edit the path locations in **spriteWorks** if you plan to use **spriteMaker** outside of the **demo** directory. Both **numpy** and **cv2** are required. See the video: <https://youtu.be/NjMg-95ecgw>
       
          
       
**Edits for PySide6:**     
    1. In all **sprite*.py** files, change **PyQt6** to **PySide6**  
    2. in **spriteMaker.py** - change **e.pos()** to **e.position()**      
    3. In **spriteWorks.py** - change **pyqtSignal(s)** to **Signal** and comment out line **181**, look for **comment**    
    4. In  **spriteLoupe.py**- change **pyqtSlot(s)** to **Slot**  
    5. Make sure you're in the right directory

 **Edits for PyQt5.15:**     
    ... In all **sprite.py** files, change **PyQt6** to **PyQt5**     
    
 

Keys I'm tracking. I added the Apple **Command** key to toggle the points on and off, it makes it easier to see the contour that way, especially against the gray background. I've also added the **up** and **down arrow keys** to help navigate the points either forward or backward.

        if e.key() in ExitKeys:
            self.aclose()
        elif e.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):  ## can vary
            self.setKey('del')
        elif e.key() == Qt.Key.Key_Alt:
            self.setKey('opt')    
        elif e.key() == Qt.Key.Key_Control:
            self.works.edit()      
        elif self.loupe.times2:    
            if e.key() == Qt.Key.Key_Up:
                self.loupe.nextPoint('up')
            elif e.key() == Qt.Key.Key_Down:
                self.loupe.nextPoint('down')

**May 2022:**       
I've added a sprite-maker, spriteMaker.py, currently standalone as it requires cv2 and numpy. I decided to leave it outside of dots for the present, however it does rely on dotsQt for some data, functions, and directories(folders), so it's not totally standalone. A good deal of its code is based on pathMaker, including being able to add or delete points so it may prove familiar. See the demo: <https://youtu.be/sySmphW7bYA>

**Old News - should no longer be an issue.**  
If you're on a Mac laptop running either Big Sur or Monterey and you _*_**don't**_*_ use a mouse there's good change you'll see this warning many times.        
 
    qt.pointer.dispatch: delivering touch release to same window QWindow(0x0) not QWidgetWindow(0x7f888e691040, name="CasterClassWindow")
    qt.pointer.dispatch: skipping QEventPoint(id=1 ts=0 pos=0,0 scn=789.445,580.564 gbl=789.445,580.564 Released ellipse=(1x1 ∡ 0) vel=0,0 press=-789.445,-580.564 last=-789.445,-580.564 Δ 789.445,580.564) : no target window

The easiest way to make it go away is to use a mouse. At the beginning of June I filed a bug report with Qt, looks like it didn't make it for 6.3.1 but it doesn't matter now.
