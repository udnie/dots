## DotsQt  
**DotsQt** provides a canvas for creating photo-collage and 2D animations using transparent .pngs as sprites/clip-art, think **"Monty Python's Flying Circus"**. It comes with some basic animations and paths that can be attached to sprite screen objects plus functions to create and modify paths, set backgrounds using photos or flat color, emulate cast shadows, run animations and create sprites.  **SpriteMaker** is now stand-alone and is easily converted to run in **PyQt6** - see **SpiteMaker.md**.

As of **May 2023** dots was updated to **PyQt 6.5**, **Python 3.11.3** and **Ventura 13.4**.  DotsQt can still run in **PyQt 5.17** with minor edits. You will need to install **numpy** and **open-cv** as well if using **SpriteMaker** or **ShadowMaker**.  Dots doesn't currently run in **PySide6**.


**StartHere.md** is next in line for an update so I'd ignore it for now. See **Changes.md** and **keys.pdf** for further documentation and links to videos - earlier ones best watched with closed captions as I was very intimated by having to speak into a very visible microphone. 
	  
## Stuff to know
The code can change over time.  One of the few coding decisions I made was to try and keep my files, modules, under/around 300 lines whenever possible. 400 lines now seems to the current average. I also use camel case after many years of coding in snake.

Sprites/clip-art can average up to 500-600 pixels per side and aren't necessarily square.  I reduce everything from drag and drop to somewhere around %30-%40 of its original size when displaying it. You can also set the starting width and height for any Sprite, see **dotsPixItem**.

The right hand panel is a scrolling list of the keys, key combinations and their actions. The key assignments will change as you switch between StoryBoard and PathMaker or by entering **'K'**.

The **background** image should reside in the backgrounds folder if you're planning to reuse it. You can also save a copy of it to the backgrounds folder using the save button in the button dock or widget. The copy will have the first 15 characters of the file name plus **'-bkg'** and will set itself as the background image replacing the original. Mainly used if you cropped the original and don't want to save it cropped.

An alternative is to have a formatted photo in the backgrounds folder that doesn't need cropping. Adding it as a background and saving it with **play** will set it to the background when reloaded.  Once a background image has been **set** it can deleted, flopped, or sent to the back if more than one background was set.

If you plan to run it on a Windows machine you'll need to edit the **paths** dictionary in **dotsShared.py**.   

**It's not advisable to attempt changes or make selections when running an animation as interesting and unwanted problems can occur.**   

The **star** in scrollPanel isn't currently designed to be dragged to the canvas, but without it none of this would exist.

I use the graphicsitem **zValue()** as a means to order the dots graphic types which share the scene items list.  There are two functions, toFront() and lastZval() that help to make sure the different types I've created are good neighbors.

#### types and zValue range		
| scene.item  | type  | zValue |
|:------------- |:---------------:| -------------:|
| PointItem | pt | 200 from topmost item+ |
| MapItem | map | 50 over top pixItem |
| TagItem | tag|45 over top pixItem|
| Paths| path| 35 over top pixItem
| PixItem | pix  | **\*see below**
| Shadow  |shadow| 50|
| Points  |point | 40|
| Outline |  none   | 30| 
| LineItem  | grid   | -50 as a group |
| BkgItem   | bkg | -99 decreasing by -1 |  

 
**\***   number of screen items + 100 decreasing by 1 per item


## Requirements
* PyQt6
* functools
* cv2 and numpy for Sprites and Shadows
* Your favorite program for creating transparent pngs if you have one or try **ShadowMaker**, it works.

## Lastly
My background combines degrees in fine arts, photography and ceramics, work as a graphics artist, layout artist, photography teacher, and a 21 year career as a business application programmer. All procedural code and other than Fortran, languages you probably never heard of. 

This is my first pyqt app and it wouldn't have been possible without Stack OverFlow and Google Search.

Special thanks to Martin Fitzpatrick of <https://www.learnpyqt.com> for taking a look at the last update and for his recommendations and code contributions.  Thanks again, Martin
