## Changes
**April 2022:**	
### The News: I finally updated to PyQt6.3 and Python 3.10.4###

If you're on a Mac laptop running either Big Sur or Monterey you may experience this qt warning. 

    qt.pointer.dispatch: delivering touch release to same window QWindow(0x0) not QWidgetWindow(0x7f888e691040, name="CasterClassWindow")
    qt.pointer.dispatch: skipping QEventPoint(id=1 ts=0 pos=0,0 scn=789.445,580.564 gbl=789.445,580.564 Released ellipse=(1x1 ∡ 0) vel=0,0 press=-789.445,-580.564 last=-789.445,-580.564 Δ 789.445,580.564) : no target window

The easiest way to make it go away is to use a mouse. Read on.
  
I've added shadow emulation to the mix but have it turned off as some folks may not share my interests in shadows and having it on adds 10-12 seconds to dots' startup time which may not be a great first-time user experience.  The two examples below give you the file names and snapshots of what code needs to tweaked inorder to have shadows working.  Comment one line off, uncomment the other line on. Save the files and restart dots. Next load shadowdemo.play and you should have 8 screen items and 8 shadows appearing as in the video. The time can vary but on my 6 year old Mac it's taking around 4 seconds for the shadows to appear once the screen items are up.  I'm using asyncio to restore shadows which has help to make the process 2 to 3 times faster then my first attempts. **cv2 and numpy are required** in order to add shadows.

#### dotsPixItem.py

```
# from dotsShadowMaker    import ShadowMaker  ## add shadows
from dotsShadow_Dummy    import ShadowMaker  ## turns off shadows

```
##### dotsSideShow.py

```
# from dotsShadowWorks    import Shadow  ## adds shadows
from dotsShadow_Dummy    import Shadow  ## turns off shadows

```
To create a shadow right-mouse click on a screen item and click on the top button labeled 'Shadow' which appears on the pixItem widget. This will work if there are no screen items selected.  See the keys.pdf for more on right-mouse click usage. If you right-mouse click on the shadow it's widget will appear.  I've colored the widgets yellow for pixItems and blue for the shadows to more easily tell them apart. There's only shadow per pixItem and deleting a pixItem deletes it's shadow.  You can't add shadows to frames or bats and you can't add animations to shadows. **Shift-W** will clear all widgets rather than closing them one at a time.  

I added a few lines to dotsSideShow.py that can output the keys and values of a play file as it's loaded and format it for csv.  There's a shadowdemo.csv in the play folder of the output to view in your default spreadsheet app, makes it more readable. Also added a mouse-over tag to alert you if a pixItem is locked. Beats wondering why you can't move it. Lastly, the bat-wing has been replaced with the actual screen bat. Yet another video: <https://youtu.be/rbFCvU9_IUs>

**March 2022:**  
I'm pretty sure **castShadow4.py**, is the last of the shadow apps. It requires both **numpy** and **cv2.** I didn't bother to demo **castShadow3.py** as it was more of an interim process. These two files and the other **'shadow'** files starting with **shadow.py** have been moved to their own folder, **dots/shadows**.  Thanks to Stack Over Flow for rounded corners and borders.  Latest video: <https://youtu.be/yqCDZHhBBww>

**February 27-28, 2022:**  
Replaced **PIL** with **cv2**.  Still runs slow from a dead start but one less library to load.  Changes to insure only .pngs get loaded with the **Files** button.

**February 22, 2022:**   
 **cast_shadow2.py**, another cast shadow emulator. This one uses points rather than pixels to create a shadow - as a result I updated **outline.py** to display a larger image, I also set the point limit up to 350. It didn't help the shadow look any better, too edgy, but a good learning experience, more to share. It works best with apple.png - cv2 and numpy required.
Video at: <https://youtu.be/eAsH9412Bww>

**February 14, 2022:**  
One more stand-alone app, **cast_shadow.py**, a cast shadow emulator.
Requires, PIL, cv2, and numpy - consequently it takes a while to start when first run but it's worth it. My opinion. Another new video: <https://youtu.be/1VWjhypf0xk>

**January 2022:**      	
Yet another stand-alone app, **outline.py**. Combines Pygame **(required)** and PyQt as a way to outline a transparent .png and save the result as a SVG file.  This is a rewrite of the my pygame original of 3-4 years ago. It also features a SVG viewer. New video: <https://youtu.be/leTFR89YxA4>
  
**December 2021:**    
I've added another stand-alone app, **shadow.py**, a PyQt dropshadow visualizer. It's either run from the command line or thru an editor. It's written to work with transparent .png and .jpg files while also as a template for future such apps. Another new video. <https://youtu.be/V-kkzuURsjg>

I've added two new functions/keys to editing a path in pathMaker.
**L** in **edit** changes the cursor to a crosshair to let you know that things have changed. Holding down the mouse button while moving the mouse draws a closed shape to either select or unselect selected pointItems. Once selected you can use the arrow keys to move the selected points or using the other new key, **shift-D**, to delete them.  Lastly, you can easily move between **editing points** and **waypoints** and and not lose any points you previously selected in **edit** by toggling between **E** and **W** or **W** to **E**.  New video: <https://youtu.be/AMTV3umYyuc>

Additionally, some key reassignments in dropCanvas. I replaced **{/}** for rotating a sprite 45 degrees with **[/]** to match the same command in pathMaker. I also reassigned the keys that increment or decrement a sprite's **ZValue** back to front position. A **comma** sets a sprite back one **ZValue** and **period** up one value.  The four keys that are used to change a sprites **ZValue** are much closer together now. Big Win.

**November 2021:**  
Added a right-mouse click to dropCanvas to trigger the **play** load dialog and to pathMaker to trigger **path chooser**.  Added a path edit function to pathMaker. Entering **E** after choosing a path allows you move, delete, or add a point and also re-distribute or half the number of points that make up the path. Some of these functions are also in wayPoints but not the ability to move individual points. Entering **W** from **edit** will put you into wayPoints and conversely **E** in **wayPoints** drops you into edit.  More work on bat-wings. They're now easier to select and move by clicking anywhere on the bats body but not the wings. Added **Shift U** to unlock all screen items in dropCanvas.

**October 2021:**   
I've done some more work on wings and have some observations concerning the tendency for them to drift when stopped. The only differences I can see is using or not using the file chooser somehow affects the reprise animation for the wings screen objects.  

**September 2021:**			
**Bonus...**  I've added a screen pixel ruler, **vhx.py** to the mix.  It runs both in Dots and on my Mac as a desktop widget - **vhx.app**, created using the MacOS Automator, the same utility that lets me run Dots as a desktop app. **Note:** Also on my Mac, **vhx.py** only runs in Dots when in VSCode, otherwise you can run it from the command line. This finally replaces my JavaFx version. See **keys.pdf** for updates. New video:  <https://youtu.be/98m-fNB16-w> 

**Runs on Linux.**
I wanted to see what it would take to set up a VM, a virtual machine, and run dots in Ubuntu 20.4 Linux. So I used VirtualBox, as recommended by Martin Fitzpatrick, as the VM of choice. After downloading and installing Ubuntu I gradually came to realize that no matter how many more times I downloaded and installed PyQt it was going to land in the python3.8 directory.  So I ran Dots in python3.8 with no problems other than not having dots displayed full size and having to use the control key in place of the Mac command key. I probably spent half my time with this project in the VM trying to find the menu bar which had disappeared - not an uncommon problem. I was finally able to resize the linux window to pretty much my Mac view and by setting the scaled setting to 200% dots opened up to the same size as I run it in MacOS though it could use a few small 10-15 pixels tweaks to reposition the inner side panels.  **Done.**

See **keys.pdf** for the current key assignments and hopefully some clarity. I added a **45 degree** toggle to pathMaker and changed the **half path** function to evenly distribute the new points. It looks better that way, uses less data though it may alter the path slightly. In dropCanvas, selecting screen objects will now be outlined by an actually visible lime green boundingRect. Lastly, I posted a remake of the last video I created in DotsJavaFx, **Tableau 2018**, recreated now in DotsQt as **Tableau 2021**, which was sort of the idea and why I spent the last two years writing in PyQt. I've included the code for wings 
in DotsSideCar. Two videos follow, **Tableau 2021** <https://youtu.be/h70MO0V7CNw> and **DotsQt Wings** <https://youtu.be/HtOaDZfeCzg>

**August 2021:**  
The annoyance is no more. It's taken a while and the fix was easier to apply once I had isolated pathMaker from the rest of dots. The solution bothers me some - otherwise an interesting programming challenge.  Moving on, more key changes and additions.  I've moved the **-/= scale Y** keys to **;** and **'** to line up with **scale X :/"**.  The old **-/= scale Y** keys are now rotate **-/+15** degrees.  Also, the highest positioned pixItem by zValue is now tagged in yellow if you show tags by pressing **T**. The latest video. <https://youtu.be/cBvLJh02LgQ>
   
**July 2021:**		
Changed, holding down the **space-bar** and a **left-mouse click** will show the pixItem tag.  **T** still displays all the tags and a **shift-T** will display the tags of everything that's been **selected**.  I've also added three methods to lock and unlock pixItem screen positions. The first, **shift-L** works to toggle **selected pixItems** locked or unlocked. The second method, **shift-R**, locks **all pixItems**. The last method, **apostrophe** and a **mouse-click** toggles individual pixItems. You will need to save the changes for them to take effect. There's a new file, as of August, **dotsDrawsPaths**, that isolates the code that draws the path and displays pointItems. The annoyance still persists. Still working on it.

**June 2021:**  
Decided to change things around again and reassigned some keys from February changes. In dropCanvas **'R'**, for run, replaces **'P'** for play. Typing **'R'** on a blank screen will run the demo or any play file you've set in dotsShared under 'runThis'. **'P'** will toggle paths replacing **'O'** - from February again. In pathMaker **'P'**, under wayPoint to show pointItems, has been replaced with **'V'** to view pointItems. Changed status-bar color. No video. The annoyance still persists.  Still working on it.

**April 2021:**  
 Changed the single zValue keys to **'['** and **']'** as the **option-click** key was conflicting with the **option-double click**.  Added a display for a single **ztag** when right-mouse clicking over a pixItem. Changed the **single-click** to **enter/return** to eliminate any accidental or unnecessary movement back to front. Reduced the screen width of dots and added one more sprite selection to the scrollPanel. Blocked any mouse actions to a pixItem while running an animation - this will prevent any screen items from getting lost. The **'C-key** can quit pathMaker if the screen is empty and no longer requires a click on the pathMaker button to do so. See dotsDropCanvas.py starting at line 96 for a fuller explanation of what I call an annoyance.
Video at: <https://youtu.be/AI1E8hszBbk>

**March 2021:**  
Added the **Color** button to launch a color picker *widget. A color can be saved to the backgrounds directory as a named file that ends in **'.bkg'**, this allows it to be recalled and added to a play file as a regular background object. The expected color token is a hex string - **#FFFFFF**, there is no saved image file. Also added the pixItems zValue to tags and keys to send a pixItem back one zValue using **option-click** or forward one zValue using **command-click**. Frames are now a special case sprite rather than a background item.  DropCanvas now 1080X720 pixels.  See Video: <https://youtu.be/yUzqY7p9X3I>

**February 2021:**	
Added the **'O'** key to the main window to toggle the paths prior to running animations as the **'P'** is now the **play** hot-key. Both keys can toggle the paths display once the animations are running. Also updated the parent window from a QGroupBox widget to QMainWindow adding QDockWidgets, a CentralWidget and a statusBar.  Currently running in Python 3.9.2 and PyQt 5.15.3 on a Mac, OSX  10.14.6.  QFileDialog in native mode no longer lets the user delete files. 

**December 2020:**	
Added the **'L','P','S'** keys to dropCanvas to Load, Play, and Stop animations, same as the buttons - also reinstated **'C'** to clear the screen in dropCanvas. Clicking on the clear button will close pathMaker and as well as clicking on the pathMaker button if it's green. The **'C'** key is also used in pathMaker to center a path.

The **'P'** key still toggles paths but only after play begins. It's either that or start play and immediately show the paths. In wayPoints, under pathMaker, I've added another **'P'**  key that toggles the points used to draw the path. If you mouse over a point a yellow tag with the points x,y value, percent, and index will appear - mouse away to clear it. 	

The method used to calculate percents has changed. The old method was based on a fixed percentage which returned a point value position along the path but not necessarily an actual point, especially if the total number of points wasn't evenly divisible by 10. There's a fix for that if you desire an actual 10% correspondence. Mouse over a point to display the tag, hold down the delete key and click to **delete** the point or option click on it to **add** a new point midway from the point you're on to the next point down the path. Either approach will update the path and the percents.

**November 2020:**  
Added **'P'** key to toggle paths if found in a play file or if assigned when running and the **'K'** key to toggle the help keyList from dropCanvas to pathMaker.  Added a new **button** for pathMaker functions.  Reassigned some dropKeys to match up with similar functions in pathMaker and pixItems. Added **'R'** key to run the animation path demo. It's looks a little odd when it starts but the end result matches the original. It required a few work arounds to get the effect I was after.   
  
Use the **'!'** key in **pathMaker** to reduce the path points size. I found that around 200 points should be sufficient in most cases. Also, you can use the snapshot button to record the waypoint tags and paths, plus any background. See video: <https://youtu.be/kalDltrQkWs>

**September 2020:**   
Added the play, pause/resume and stop buttons to run animations. Added **paths** to animations.  Added a right-click **context menu** for adding animations to screen selections.  

Added **tags** to show a screen items current animation. After selecting an animation you can type 'T' to toggle the tags on and off. Tags will be orange initially if there are no animations running.  Once running and if set to Random, tags will appear green and display the animation that was randomly assigned. The **context menu** only works if something is selected, even to clear **tags**. A video showing some basic animations and how to add them to a screen object - pixitem. <https://youtu.be/SHDmcySukGg>

**August 2020:**  
Added two new buttons. The save button maps the canvas items, pixItems and background to a Json file written to the ./plays directory as a .play file.  The load button reconstructs the saved canvas layout from the named .play file. Changed delete from the shift key to the actual delete key. Seems it shows up as a backspace key on some installs which is why I may not have used it earlier. Video to illustrate the save and load functions. <https://youtu.be/RPwEjgAcITk> 
 
**June 2020:**  
Initial posting followed by minor bug fixes and fussy changes. The original video that illustrates some of the features of this app. <https://youtu.be/rd4LtR88UjE> 
