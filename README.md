## DotsQt  
**DotsQt** is a program for creating photo-collage and 2D animations using transparent pngs as sprites/clip-art. It comes with some basic animations and paths that can be attached to the sprite screen objects plus a set of functions to create and modify paths as well as functions to set the background, either using photos or flat color.

The original dots was written in JavaFX which added animation to the photo-collage portion of the DotsFX app as well as providing a means to create sprites. The dots front end is no longer required as the screen objects, sprites, are now based on transparent pngs.

This is not a finished app - more of a toolkit, an artist's studio, a potter's kick-wheel. In building an animation from scratch the file **dotsAnimation.py** provides the starting point for the code necessary to create your own animations.See **keys.pdf, Changes.md, Start-Here.md** for updated documentation.
	  
#### I'd recommend running dots in **PyQt5.15** as it's already been prepped for **PyQt5.2**.  I've added all the necessary new enums required by 6.2 but 5.15 doesn't seem to notice them.  I can't speak for earlier versions.

## Stuff to know
The code can change over time.  One of the few coding decisions I made was to try and keep my files, modules, under 300 lines whenever possible, it doesn't always work. Also I use camel case after many years of coding in snake.

Sprites/clip-art can average up to 500-600 pixels per side and aren't necessarily square.  I reduce everything from drag and drop to somewhere around %25-%35 of its original size when displaying it on dropCanvas.

The upper right hand panel is a read only scrolling list of the keys, key combinations and their actions. The panel will switch the key assignments as you switch from DropCanvas to PathMaker or by entering **'k'**.

The **background** image doesn't need to reside in the backgrounds folder unless you're planning to reload it. You can save a copy of it to the backgrounds folder using the save button in the background group. The copy will have the first 15 characters of the file name plus **'-bkg'** and will set itself as the background replacing the original image.

An alternative is to have a **3:2** formatted photo in the backgrounds folder that doesn't need cropping. Adding it as a background and saving it with **play** will set it to the background when reloaded.  Once a background image has been **set** it can deleted, flopped, or sent to the back if more than one background was set.

If you plan to run it on a Windows machine you'll need to edit the **paths** dictionary in **dotsShared.py**.   

**It's not advisable to attempt changes or make selections when running an animation as interesting and unwanted problems can occur.**   

The **star** in scrollPanel isn't currently designed to be dragged to the canvas, but without it none of this would exist.

I use the graphicsitem **zValue()** as a means to order the graphic types which share the scene items list.  There are two functions, toFront() and lastZval() that help to make sure the different types I've created are good neighbors.

#### types and zValue range		
| scene.item  | type  | zValue |
|:------------- |:---------------:| -------------:|
| PointItem | pt | from topmost item+ |
| MapItem | map | 50.0 over top pixItem |
| TagItem | tag|25.0 over top pixItem|
| PixItem | pix  |  0.0 increasing by 1.0 | 
| Paths| path| -25.0 as a group 
| LineItem  | grid   | -50.0 as a group |
| BkgItem   | bkg | -99.0 decreasing by -1.0 |    
  
  

## Requirements
* PyQt5
* functools
* PyPubSub - only for testing 
* Any program that can create transparent pngs - lately I've been using Affinity on my iPad.

## Lastly
My background combines degrees in fine arts, photography and ceramics, work as a graphics artist, layout artist, photography teacher, and a 21 year career as a business application programmer. All procedural code and other than Fortran, languages you probably never heard of. 

This is my first pyqt app and it wouldn't have been possible without Stack OverFlow and Google Search. I can say pretty much the same about the Java version as well.

Special thanks to Martin Fitzpatrick of <https://www.learnpyqt.com> for taking a look at the last update and for his recommendations and code contributions.  Thanks again, Martin








  







##  **