## DotsQt  
**DotsQt** provides a canvas for creating **photo-collages** that can be run as **2D animations** using **transparent .pngs** as **sprites/clip-art** - think **"Monty Python's Flying Circus"**. It comes with some basic animations and paths that can be attached to sprite screen objects plus functions to create and modify them, set backgrounds using photos, videos or flat color, emulate cast shadows, and run animations with multiple scrolling backgrounds.  

As of **April 2025**, **dots** can now run in either **PyQt6.8.1**, **PyQt5.15** or **PySide6.8.2** as developed  on a **M1 MacBookPro** in **arm64 mode** on **Apple Silicon**, **Python 3.13.2**.
See **Start Here** for converting **Dots** from **PyQt6** to **PyQt5** or **PySide6**  - there are scripts for that. 

**August 2024** had **dots** up and running including **shadows** in **Windows 11**. Some of the type wasn't showing as well as it does on my Mac - otherwise it seemed to run fine.

You'll need to install **opencv-python** if you plan to use **Shadows** - **numpy** is included.   I've included some materials, sprites and dopey backgrounds to play with and to help get you started but it would be more informative and entertaining if you added your own.  


	  
## Stuff to know
The code can change over time and it does.  One of the few coding decisions I made was to try and keep my files, modules, under/around 300 lines whenever possible. I also use camel case after many years of coding in snake.

Sprites/clip-art can average up to 500-600 pixels per side and aren't necessarily square.  I reduce everything from drag and drop to somewhere around %30-%40 of its original size when displaying it. You can also set the starting width and height for any Sprite, see **dotsPixItem**.

The **background** image needs to reside in the **backgrounds** folder as **dots** only looks in the **background** and **demo** folders for backgrounds. I'd recommend making any changes, mainly sizing and orientation, prior to deploying it. 

Flat colors will be saved to the backgrounds folder using the save button in the **backgrounds** button dock. The file name is up to you with **'.bkg'** as the file extension.  Saving a **background** to a **'.play'** file will preserve any settings you might have made, such as for scrolling and a flat color without needing to save the color.

The **star** in scrollPanel isn't currently designed to be dragged to the canvas, but without it none of this would exist.


## Requirements
* **PyQt6**, **PyQt5** or **PySide6** -- see **Start Here**
* **Python 3.10** or above for walrus operators and async
* There are two scripts that require a unix/linux shell, bash or zsh, and sed 
* functools, though I'm sure it's built-in
* **opencv-python** if you're planning to use **Shadows**, **ShadowMaker** or **videoPlayerOne**, it includes **numpy**
* Your favorite program for creating transparent pngs if you have one or try **ShadowMaker** 

## Lastly
My background combines degrees in fine arts, photography and ceramics, work as a graphics artist, layout artist, photography teacher, and a 21 year career as a business application programmer. All procedural code and other than Fortran, languages you probably never heard of. 

Special thanks to Martin Fitzpatrick of <https://www.learnpyqt.com> for taking a look at the last update and for his recommendations and code contributions.  Thanks again, Martin
