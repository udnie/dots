## DotsQt  
**DotsQt** provides a canvas for creating **photo-collages** that can be run as **2D animations** using **transparent .pngs** as **sprites/clip-art** - think **"Monty Python's Flying Circus"**. It comes with some basic animations and paths that can be attached to sprite screen objects plus functions to create and modify paths, set backgrounds using photos or flat color, emulate cast shadows, and run animations with multiple scrolling backgrounds.

Currently **dots** is running on **PyQt 6.6.1**, **Python 3.11.7** and **Sonoma 14.5** on a M1 MacBook in **X86 mode.** As of **June 2024** you can now run **dots** on **Apple Silicon** using **PyQt5**. Definitely read the **June 2024** entry in **Changes.md** - it's not difficult.

You'll need to install **opencv-python** if you plan to use **SpriteMaker**, **ShadowMaker** or **Shadows** - **numpy** is included in **opencv**.  **StartHere.md** has also been updated to cover the latest on **scrolling backgrounds** and **shadows** as well as whatever else I thought might be useful.  
	  
## Stuff to know
The code can change over time and it does.  One of the few coding decisions I made was to try and keep my files, modules, under/around 300 lines whenever possible. I also use camel case after many years of coding in snake.

Sprites/clip-art can average up to 500-600 pixels per side and aren't necessarily square.  I reduce everything from drag and drop to somewhere around %30-%40 of its original size when displaying it. You can also set the starting width and height for any Sprite, see **dotsPixItem**.

The **background** image needs to reside in the **backgrounds** folder as **dots** only looks in the **background** and **demo** folders for backgrounds. I'd recommend making any changes, mainly sizing and orientation, prior to deploying it. 

Flat colors will be saved to the backgrounds folder using the save button in the backgrounds button dock. The file name is up to you with **'.bkg'** as the file extension.  Saving a **background** to a **'.play'** file will preserve any settings you might have made, such as for scrolling.

If you plan to run it on a Windows machine you'll need to edit the **paths** dictionary in **dotsShared.py**.   

**It's not advisable to attempt changes or make selections when running an animation as interesting and unwanted problems can occur.**   

The **star** in scrollPanel isn't currently designed to be dragged to the canvas, but without it none of this would exist.


## Requirements
* PyQt6 though you can probably still run PyQt5 with some edits 
* functools, though I'm sure it's built-in
* cv2 and numpy for Sprites and Shadows
* Your favorite program for creating transparent pngs if you have one or try **ShadowMaker**, it works and requires cv2 and numpy.

## Lastly
My background combines degrees in fine arts, photography and ceramics, work as a graphics artist, layout artist, photography teacher, and a 21 year career as a business application programmer. All procedural code and other than Fortran, languages you probably never heard of. 

Special thanks to Martin Fitzpatrick of <https://www.learnpyqt.com> for taking a look at the last update and for his recommendations and code contributions.  Thanks again, Martin
