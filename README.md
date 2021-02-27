## DotsQt  
**DotsQt** is a program for creating photo-collage and 2D animations using transparent pngs as sprites/clip-art. It comes with some basic animations and paths that can be attached to the sprite screen objects plus a set of functions to create and modify paths.

The original dots was/is a program written in JavaFX that added animation to the photo-collage portion of the dotsFX app as well as providing a means to create sprites. DotsQt is a PyQt implementation of the storyboard, animations and pathMaker sections. 

**Note:** Dots was the original front end and is no longer required as the pixItem screen objects are now based on transparent pngs.

## Why
 

* I did have some questions, I think I've answered them myself for now.

* I never got the chance to publish the original JavaFX version as Oracle stopped supporting FX in 2018.  I felt it was worth the effort to try once again in Python. I haven't been disappointed.



## Stuff to know
One of the few coding decisions I made was to try and keep my files, modules, under 300 lines when possible. Also, I use camel case after many years of coding in snake.

Sprites/clip-art can average up to 500-600 pixels per side and aren't necessarily square.  I reduce everything from drag and drop to somewhere around %25-%35 of its original size when displaying it on dropCanvas.

The upper right hand panel is a read only scrolling list of the keys, key combinations and their actions. Key assignments have changed with the addition of pathMaker. The scrolling lists and this ReadMe file serve as your **help** documentation.    

The **background** image doesn't need to reside in the backgrounds folder unless you're planning to reload it. You can save a copy of it to the backgrounds folder using the save button in the background group. The copy will have the first 15 characters of the file name plus **'-bkg'** and will set itself as the background replacing the original image.

An alternative is to have a **3:2** formatted photo in the backgrounds folder that doesn't need cropping. Adding it as a background and saving it with **play** will set it to the background when reloaded.  Once a background image has been **set** it can deleted, flopped, or sent to the back if more than one background was set.

If you plan to run it on a Windows machine you'll need to edit the **paths** dictionary in DotsShared.py.   

It's not advisable to make changes in the pause mode as interesting, unwanted problems can occur.   

The **star** in scrollPanel isn't currently designed to be dragged to the canvas, but without it none of this would exist.

I use the graphicsitem **zValue()** as a means to order the six graphic types which share the scene items list.  There are two functions, toFront() and lastZval() that help to make sure the different types I've created are good neighbors.

#### types and zValue range		
| scene.item  | type  | zValue |
|:------------- |:---------------:| -------------:|
| MapItem | map | 50.0 over top pixItem |
| TagItem | tag|25.0 over top pixItem|
| pixItem | pix  |  0.0 increasing by 1.0 | 
| Paths| path| -25.0 as a group 
| LineItem  | grid   | -50.0 as a group |
| BkgItem   | bkg | -99.0 decreasing by -1.0 |    
  
  
## Changes

**February 2021:**	
Added the **'O'** key to the main window to toggle the paths prior to running animations as the **'P'** is now the **play** hot-key. Both keys can toggle the paths display once the animations are running. Also updated the parent window from a QGroupBox widget to QMainWindow adding QDockWidgets, a CentralWidget and a statusBar.  This update now running in Python 3.9.2 and PyQt 5.15.3 on Mac OSX  10.14.6.  The file dialog in native mode no longer lets the user delete a file thru the context menu. 

Some bug fixes. Relocated code. No new videos.

**December 2020:**	
Added the **'L','P','S'** keys to dropCanvas to Load, Play, and Stop animations, same as the buttons - also reinstated **'C'** to clear the screen in dropCanvas. Clicking on the clear button will close pathMaker and as well as clicking on the pathMaker button if it's green. The **'C'** key is also used in pathMaker to center a path.

The **'P'** key still toggles paths but only after play begins. It's either that or start play and immediately show the paths. In wayPoints, under pathMaker, I've added another **'P'**  key that toggles the points used to draw the path. If you mouse over a point a yellow tag with the points x,y value, percent, and index will appear - mouse away to clear it. 	

The method used to calculate percents has changed. The old method was based on a fixed percentage which returned a point value position along the path but not necessarily an actual point, especially if the total number of points wasn't evenly divisible by 10. There's a fix for that if you desire an actual 10% correspondence. Mouse over a point to display the tag, hold down the delete key and click to **delete** the point or option click on it to **add** a new point midway from the point you're on to the next point down the path. Either approach will update the path and the percents.

**November 2020:**  
Added **'P'** key to toggle paths if found in a play file or if assigned when running and the **'K'** key to toggle the help keyList from dropCanvas to pathMaker.  Added a new **button** for pathMaker functions.  Reassigned some dropKeys to match up with similar functions in pathMaker and pixItems. Added **'R'** key to run the animation path demo. It's looks a little odd when it starts but the end result matches the original. It required a few work arounds to get the effect I was after.   
  
Use the **'!'** key in **pathMaker** to reduce the path points size. I found that around 200 points should be sufficient in most cases.
Also, you can use the snapshot button to record the waypoint tags and paths, plus any background.

**September 2020:**   
Added the play, pause/resume and stop buttons to run animations. Added **paths** to animations.  Added a right-click **context menu** for adding animations to screen selections.  

Added **tags** to show a screen items current animation. After selecting an animation you can type 'T' to toggle the tags on and off. Tags will be orange initially if there are no animations running.  Once running and if set to Random, tags will appear green and display the animation that was randomly assigned. The **context menu** only works if something is selected, even to clear **tags**.

**August 2020:**  
Added two new buttons. The save button maps the canvas items, pixItems and background to a Json file written to the ./plays directory as a .play file.  The load button reconstructs the saved canvas layout from the named .play file. 
 
Changed delete from the shift key to the actual delete key. Seems it shows up as a backspace key on some installs which is why I may not have used it earlier. 


**June 2020:**  
Initial posting followed by minor bug fixes and fussy changes.

##Videos	
* The original video that illustrates some of the features of this app. <https://youtu.be/rd4LtR88UjE> 

* Demonstrates some basic animations and how to add them to a screen pixItem. <https://youtu.be/SHDmcySukGg>

* Demonstrates the save and load functions. <https://youtu.be/RPwEjgAcITk>

* Introduces pathMaker. <https://youtu.be/kalDltrQkWs>

## Requirements
* PyQt5
* functools
* PyPubSub - only for testing 
* Any program that can create transparent pngs

## Lastly
My background combines degrees in fine arts, photography and ceramics, work as a graphics artist, layout artist, photography teacher, and a 21 year career as a business application programmer. All procedural code and other than Fortran, languages you probably never heard of. 

This is my first pyqt app and it wouldn't have been possible without Stack OverFlow and Google Search. I can say pretty much the same about the Java version as well.

Special thanks to Martin Fitzpatrick of <https://www.learnpyqt.com> for taking a look at the last update and for his recommendations and code contributions.  Thanks again, Martin








  







##  