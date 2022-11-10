## DotsQt  
**DotsQt** provides a canvas for creating photo-collage and 2D animations using transparent .pngs as sprites/clip-art, think **"Monty Python's Flying Circus"**. It comes with some basic animations and paths that can be attached to sprite screen objects plus functions to create and modify paths, set backgrounds using photos or flat color, emulate cast shadows, run animations and create sprites.  **SpriteMaker** is now stand-alone and is easily converted to run in **PySide6** - see **SpiteMaker.md**.

As of **October 2022** dots updated to **PyQt 6.4** and **Python 3.11**, runs in **PyQt 5.17** with minor edits.  Needed to re-install **open-cv** as well.


The files **StartHere.md** and  **dotsAnimation.py** provide a starting point for coding your own animations. See **Changes.md** and **keys.pdf** for further documentation and links to videos - best watched with closed captions - except for the last few.
	  
## Stuff to know
The code can change over time.  One of the few coding decisions I made was to try and keep my files, modules, under/around 300 lines whenever possible, it doesn't always work. Also I use camel case after many years of coding in snake.

Sprites/clip-art can average up to 500-600 pixels per side and aren't necessarily square.  I reduce everything from drag and drop to somewhere around %25-%35 of its original size when displaying it on StoryBoard. You can easily override it for specific sprites.

The upper right hand panel is a **read only** scrolling list of the keys, key combinations and their actions. The panel will switch the key assignments as you switch from StoryBoard to PathMaker or by entering **'k'**. 

The **background** image doesn't need to reside in the backgrounds folder unless you're planning to reload it. You can save a copy of it to the backgrounds folder using the save button in the background group. The copy will have the first 15 characters of the file name plus **'-bkg'** and will set itself as the background replacing the original image.

An alternative is to have a **3:2** formatted photo in the backgrounds folder that doesn't need cropping. Adding it as a background and saving it with **play** will set it to the background when reloaded.  Once a background image has been **set** it can deleted, flopped, or sent to the back if more than one background was set.

If you plan to run it on a Windows machine you'll need to edit the **paths** dictionary in **dotsShared.py**.   

**It's not advisable to attempt changes or make selections when running an animation as interesting and unwanted problems can occur.**   

The **star** in scrollPanel isn't currently designed to be dragged to the canvas, but without it none of this would exist.

I use the graphicsitem **zValue()** as a means to order the graphic types which share the scene items list.  There are two functions, toFront() and lastZval() that help to make sure the different types I've created are good neighbors.

#### types and zValue range		
| scene.item  | type  | zValue |
|:------------- |:---------------:| -------------:|
| PointItem | pt | 200 from topmost item+ |
| MapItem | map | 50 over top pixItem |
| TagItem | tag|25 over top pixItem|
| PixItem | pix  | **\*see below**
| Shadow  |shadow| 50|
| Points  |point | 35|
| Outline |  none   | 30| 
| Paths| path| -25 as a group |
| LineItem  | grid   | -50 as a group |
| BkgItem   | bkg | -99 decreasing by -1 |  

  
**\***   number of screen items + 100 decreasing by 1 per item

  

## Requirements
* PyQt6
* functools
* cv2 and numpy for Sprites and Shadows
* Any program that can create transparent pngs

## Lastly
My background combines degrees in fine arts, photography and ceramics, work as a graphics artist, layout artist, photography teacher, and a 21 year career as a business application programmer. All procedural code and other than Fortran, languages you probably never heard of. 

This is my first pyqt app and it wouldn't have been possible without Stack OverFlow and Google Search.

Special thanks to Martin Fitzpatrick of <https://www.learnpyqt.com> for taking a look at the last update and for his recommendations and code contributions.  Thanks again, Martin
