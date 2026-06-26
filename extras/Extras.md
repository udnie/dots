**June 2026**

I've moved **slideShow, videoPlayer**, and **vhx** to **extras** from **dots** and added a new app, **wrapper**.  I removed **castShadow.py** from extras  as there's a more up to date version in **dots**.  Added drag and drop to **slideShow** and **wrapper**.

Current apps in **extras**:

    1. dropShadow.py
    2. slideShow.py
    3. vhx.py 
    
    4. outline.py *
    5. spriteMaker.py *
    6. videoPlayerOne.py and clipsMaker.py *
    7. videoPlayerTwo.py and clipsMaker.py *
    8. wrapper.py *
 

  *opencv 


Plus four scripts, similar to the four in **dots**. One pair for converting the **PyQt6** code to run in **PyQt5** - **script-pyqt5.sh**, the other pair to convert **PyQt6** to run in **PySide6** - **script-ps6.sh**.  A unix/linux is operating system is required to run the **.sh** files.

**Extras** apps can be run without needing to install **dots**.


Most of what you'd need to know about the .py apps not covered by *.md files in the **extras** directory can be found in **/dots/README.md** starting around **July 2025**.  The other dates to see are **September 3**, **November 29 2025** and **April 2024** for **scrolling backgrounds**.  The there are videos for each date along with the write-ups. The more ambitious apps have help menus. Besides these dates there are further references to these apps and videos continuing to the present.

---
A few words on **wrapper**.  

I recommend a minimum image size of **1280X640 pixels** or resizing with the height set to **640 pixels** - the cropping guide seems to works better by doing so.

The image that pops up when saving to a file is the same as the file you're saving which gives you a heads up if the crop location needs to change provided you haven't turned it off.  See the **self.first** and **self.showCropped** variables in **init()** to turn off the guides on each new file and not displaying the saved image.  

The **-wrp** file needs to be in the **/backgrounds** directory in order to run it as a scrolling background as **dots** only knows to look for it in **/backgrounds** or **/demo**.

The **space-bar** button toggles the guides on and off, **'H'** toggles the blended image and  **'D'** deletes it. The sliders on the right are for possible future and currently won't affect anything. Initially I thought I might be able to use them - but what I had planned to use them for didn't work out.








