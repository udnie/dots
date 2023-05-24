## Changes      
**December 2022:**      
I've made some small changes -- the smaller green square no longer disappears when switching to the **loupe/magnifier** and a small color filled circle now appears once you begin to edit. It shows the current outline color which starts with **lime** rather than **white** as I find it easier to see, especially against a light color background.
 
        
So this is going to be strange but I now have an easier way to produce **transparent .pngs** rather than using **SpriteMaker**. **SpriteMaker** is now my fallback as **Apple IOS 16.2** will easily allow you to create a **transparent .png** in **Photos**, at least on my **IPhone 11Pro**.
Not all the time - and some touch up may be required, but I found that most of the time it will produce a very usable image. I recommend scaling the resulting image to around **1MB** or less as **2MB** to **4MB** files can slow **Dots** down. 

**September 2022:**
Minor edits to make it more compatible with PySide6.

**July 2022 - part 2:**
The enlargement is now **2.5** times the selected area and no longer jumps around trying to avoid the mouse. Once it appears you can move it using the loupe's border to anywhere that's convenient for you and it will stay there till you move or delete it. Look for **initial setting** in **spriteLoupe.py** to customize its location.  I've also dumped the gauze like background and set preview to toggle between gray and the image using the **'P'** key.  Most importantly the **Shift** key will now toggle the loupe magnifier to remain fixed making it much easier to do any edits. I've added the new **spriteMaker** keys to the **keys.pdf**.  Lastly, both **numpy** and **cv2** are **required**.  A new video: <https://youtu.be/bGYBj_bjEJU>

**July 2022 - part 1:**
**Qt-warnings** are gone - thanks to **Qt** for providing a one-line fix. Seems only to effect Mac laptop users who don't use a mouse.

 **SpriteMaker** is now fully standalone-alone other than using the **demo sprites** and **txy folders.**  It's also now able to run with some minor edits in **PySide 6.3.1**  and **PyQt5** as well.  You will need to edit the path locations in **spriteWorks** if you plan to use **spriteMaker** outside of the **demo** directory. Both **numpy** and **cv2** are required. See the video: <https://youtu.be/NjMg-95ecgw>
              
**Edits for PySide6:**     
    1. In all **sprite*.py** files, change **PyQt6** to **PySide6**  
    2. in **spriteMaker.py** - change **e.pos()** to **e.position()**      
    3. In **spriteWorks.py** - comment out the line **## comment out for pyside**    
    4. Make sure you're in the right directory

 **Edits for PyQt5:**     
    1. In all **sprite*.py** files, change **PyQt6** to **PyQt5**   
    2. In  **spriteLoupe.py** - change **e.globalPosition()** to **e.globalPos()**  
    

Keys I'm tracking. I added the Apple **Command** key to toggle the points on and off, it makes it easier to see the contour that way, especially against the gray background. I've also added the **up** and **down arrow keys** to help navigate the points either forward or backward.  See **keys.pdf** as well.

 
**May 2022:**       
I've added a sprite-maker, spriteMaker.py, currently standalone as it requires **cv2** and **numpy**. I decided to leave it outside of dots for the present, however it does rely on dotsQt for some data, functions, and directories(folders), so it's not totally standalone. A good deal of its code is based on pathMaker, including being able to add or delete points so it may prove familiar. See the demo: <https://youtu.be/sySmphW7bYA>

**Requirements:**
In case you missed it,  **cv2** and **numpy**. 

**Old News - should no longer be an issue.**  
If you're on a Mac laptop running either Big Sur or Monterey and you _*_**don't**_*_ use a mouse there's good change you'll see this warning many times.        
 
    qt.pointer.dispatch: delivering touch release to same window QWindow(0x0) not QWidgetWindow(0x7f888e691040, name="CasterClassWindow")
    qt.pointer.dispatch: skipping QEventPoint(id=1 ts=0 pos=0,0 scn=789.445,580.564 gbl=789.445,580.564 Released ellipse=(1x1 ∡ 0) vel=0,0 press=-789.445,-580.564 last=-789.445,-580.564 Δ 789.445,580.564) : no target window

The easiest way to make it go away is to use a mouse. At the beginning of June I filed a bug report with Qt, looks like it didn't make it for 6.3.1 but it doesn't matter now.
