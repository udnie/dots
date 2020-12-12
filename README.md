## DotsQt
**DotsQt** is a program for creating photo-collage and animations using transparent pngs as clip-art. It comes with some basic animations and paths that can be attached to the screen objects, and with this update, a set of functions to create and modify paths.

The original dots was/is a program written in JavaFX that added animation to the photo-collage portion of the dots app as well as providing a means to create sprites. DotsQt is a pyqt implementation of the storyboard, animations and pathMaker sections. 

**Note:** Dots was the original front end and is no longer required as the pixItem screen objects are now based on transparent pngs.

## Why
I've a few reasons for posting this. 

* I've some questions that I'd like answered and having the code and supporting materials should help.

* I never got the chance to publish the original as Oracle stopped supporting JavaFX beginning with Java9, 2018.


* I wanted to share the fun and I felt it was worth the effort to try again in pyqt. I haven't been disappointed.

## Questions, only two - still no answers

* I'd like to add two gestures to my pixItem class, a **QGraphicsPixmapItem**.  One to scale it the other to rotate it.  The code to scale and rotate is already working in pixItem using keyboard commands, adding gestures would be a bonus. I found one example using a gesture to scale a widget but couldn't get the code to work in the pixItem class. 

	How would I go about adding gestures to the pixItem class and could I do it without a major overhaul?   I've gestures working in the Java pixItem version and it seems a more natural interface for scaling and rotating a screen object.

* I've slots and signals working in a few of the modules but was unable to make it work between the dotsDropCanvas.py and dotsPixItem.py files. There are stubs for PyPubSub that did work as a reference. The setPixKeys slot in pixItem is unchanged and all I've done is to replace the PyPubSub code in dropCanvas with the sendPixKeys function, my work around.

	How would I go about wiring up dropCanvas to talk to setPixKeys in pixItem using a signal from dropCanvas?  Would using pyqt slots and signals be any more efficient then my work around? 


## Stuff to know
One of the few coding decisions I made was to try and keep my files, modules, under 300 lines - I've let a few go longer as it made sense to have like code in one place. Also, I use camel case after many years of coding in snake.

Sprite clip-art can average up to 500-600 pixels per side and doesn't need to be square.  I reduce everything from drag and drop to somewhere around %25-%35 when displaying it in dropCanvas.

The upper right hand panel of dotsQt is a read only scrolling list of the keys, key combinations and their actions. Some key assignments have changed with the addition of pathMaker. The scrolling lists and this ReadMe file serve as your **help** documentation.    

The **background** image doesn't need to reside in the backgrounds folder unless you're planning to reload it. You can save a copy of it to the backgrounds folder using the save button in the background group. The copy will have the first 15 characters of the file name plus **'-bkg'** and will set itself as the background replacing the original image.

An alternative is to have a **3:2** formatted photo in the backgrounds folder that doesn't need cropping. Adding it as a background and saving it with **play** will set it to the background when reloaded.  Once a background image has been **set** it can deleted, flopped, or sent to the back if more than one background was set.

This app is written on a Mac, Python 3.8, PyQt 5.13.  If you plan to run it on a Windows machine you'll need to edit the **paths** dictionary in DotsShared.py.   

It's not advisable to make changes in the pause mode as interesting, unwanted problems can occur.   

The **star** in scrollPanel isn't currently designed to be dragged to the canvas, but without it, none of this would exist.

I use the graphicsitem **zValue()** as a means to order the five graphic types which share the scene items list.  There are two functions, toFront() and lastZval() that help to make sure the different types I've created are good neighbors.

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
**June 2020:**  
Initial posting followed by minor bug fixes and fussy changes.

**August 2020:**  
Added two new buttons. The save button maps the canvas items, pixItems and background to a json file written to the ./plays directory as a .play file.  The load button reconstructs the saved canvas layout from the named .play file. 
 
Changed delete from the shift key to the actual delete key. Seems it shows up as a backspace key on some installs which is why I may not have used it earlier. 

**September 2020:**   
Added the play, pause/resume and stop buttons to run animations. Added **paths** to animations.  Added a right-click **context menu** for adding animations to screen selections.  

Added **tags** to show a screen items current animation. After selecting an animation you can type 'T' to toggle the tags on and off. Tags will be orange initially if there are no animations running.  Once running and if set to Random, tags will appear green and display the animation that was randomly assigned. The **context menu** only works if something is selected, even to clear **tags**.

**November 2020:**  
Added **'P'** key to toggle paths if found in a play file or if assigned when running and the **'K'** key to toggle the help keyList from dropCanvas to pathMaker.  Added a new **button** for pathMaker functions.  Reassigned some dropKeys to match up with similar functions in pathMaker and pixItems. Added **'R'** key to run the animation path demo. It's looks a little odd when it starts but the end result matches the original. It required a few work arounds to get the effect I was after.   
  
Use the **'!'** key in **pathMaker** to reduce the path points size. I found that around 200 points should be sufficient in most cases.
Also, you can use the snapshot button to record the waypoint tags and paths, plus any background.

**December 2020:**	
Added the **'L','P','S'** keys to dropCanvas to Load, Play, and Stop animations, same as the buttons - also reinstated **'C'** to clear the screen in dropCanvas. Clicking on the clear button will close pathMaker and as well as clicking on the pathMaker button if it's green. The **'C'** key is used in pathMaker to center a path.

The **'P'** key still toggles paths but only after play begins. It's either that or start play and immediately show the paths. In wayPoints, under pathMaker, I've added another **'P'**  key that toggles the points used to draw the path. If you mouse over a point a yellow tag with the points x,y value, percent, and index will appear - mouse away to clear it. 	

The way percents were calculated has changed. The old method was based on a fixed percentage which returned a point value position along the path but not necessarily an actual point, especially if the total number of points wasn't evenly divisible by 10. There's a fix for that if you desire an actual 10% correspondence. Mouse over a point to display the tag, hold down the delete key and click to **delete** the point or option click on it to **add** a new point midway from the point you're on to the next point down the path. 

	
Some bug fixes. Relocated code. No videos for this update.


##Videos	

* Introduces pathMaker. <https://youtu.be/kalDltrQkWs>

* Demonstrates some basic animations and how to add them to a screen pixItem. <https://youtu.be/SHDmcySukGg>


* Demonstrates the save and load functions. <https://youtu.be/RPwEjgAcITk>


* The original video that illustrates some of the features of this app. <https://youtu.be/rd4LtR88UjE> 

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