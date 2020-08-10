## DotsQt
**DotsQt** is a work in progress and as it stands today, a program for creating photo-collages using transparent pngs.

The original dots was/is a program written in JavaFx that added animation to the photo-collage portion of the dots app I called storyboard as well as providing a means to create sprites. DotsQt is a pyqt implementation of storyboard and its attendant classes. There is no animation in this release.

**Note:** There is no dots in DotsQt either. Dots was the original front end and is no longer required as the pixitem screen objects are now based on transparent pngs.


## Why
I've a few reasons for posting this. 

* I've some questions that I'd like answered and having the code and supporting materials should help.

* I never got the chance to publish the original as Oracle killed off JavaFx. I've read it's not yet dead but I rather code in python.

* I wanted to share the fun. 

## Questions
I've rearranged them since I first published this as my priorities have changed.


* I'd like to add two gestures to my PixItem class, a **QGraphicsPixmapItem**.  One to scale it the other to rotate it.  The code to scale and rotate is already working in PixItem using keyboard commands, adding gestures would be a bonus. I found one example using a gesture to scale a widget but couldn't get the code to work in the PixItem class. 

	How would I go about adding gestures to the PixItem class and could I do it without a major code overhaul?   I've gestures working in the Java PixItem version and it seems a more natural interface for scaling and rotating a screen object.

* I've slots and signals working in a few of the modules but was unable to make it work between the dotsDropCanvas.py and dotsPixItem.py files. There are stubs for PyPubSub that did work as a reference. The setPixKeys slot in PixItem is unchanged and all I've done is to replace the PyPubSub code in DropCanvas with the sendPixKeys function, my work around.

	How would I go about wiring up dropcanvas to talk to setPixKeys in pixitem using a signal from dropcanvas?  Would using pyqt slots and signals be any more efficient then my work around? 

* I'm looking for samples or documentation on animation, svg, paths. Are there any sources to recommend besides the latest pyside docs?


## Stuff to know
One of the few coding decisions I made was to try and keep my files, modules, under 300 lines.  Also, I use camel case after many years of coding in snake case.

Sprites in dots can average up to 500-600 pixels per side and don't have to be square.

The upper right hand panel of dotsQt is a read only scrolling list of the keys, key combinations and their actions. Consider that **help**. 

The background image doesn't have to reside in the backgrounds folder unless you're planning to reload it. You can save a copy of it to the backgrounds folder using the save button in the background group. The copy will have the first 15 characters of the file name plus **'-bkg'** and will set itself as the background replacing the original image.

An alternative is to have a **3:2** formatted photo in the backgrounds folder that doesn't need cropping. Adding it as a background and saving it with play will set it to the background when reloaded. 

Once a background image has been **set** it can only be deleted or flopped.

This app is written on a Mac, if you plan to run it on a Windows machine you'll need to reset the **paths** in DotsQt.py.  You can't miss them.  


The **star** in scrollPanel isn't currently designed to be dragged to the canvas, but without it, none of this would exist.

Currently I'm using the graphics item **zValue()** as a means to order the four types which share the scene items list.

#### types and zValue range		
| scene.item  | type  | zValue |
|:------------- |:---------------:| -------------:|
| MapItem | map | 10.0 over top pixitem |
| PixItem | pix  |  0.0 increasing by 1.0 |  
| LineItem  | grid   | -33.0 as a group |
| BkgItem   | bkg | -99.0 decreasing by -1.0 |  
   
 
## Changes
**June 2020:**  
Inital posting followed by minor bug fixes and fussy changes.

**August 2020:**  
Added two new buttons. The save button maps the canvas items, pixitems and background to a json file written to the ./plays directory as a .play file.  The load button reconstructs the saved canvas layout from the named .play file. 

**August 2020.09:**  
Changed delete from the shift key to the actual delete key. Seems it shows up as a backspace key on some installs which is why I may not have used it earlier. 

##Videos	
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

Hope you enjoy it.








  







 