<br><br><a id="top"></a>
Thought this might be helpful for anyone interested in digging a little deeper
into the apps in **extras.**  Some of the videos may only mention the app as I 
usually have more than one set of changes by the time I'm ready to put a video 
together.

---

Current apps in **extras**:

1. [dropShadow.py](#dropshadow)
2. [slideShow.py](#slideshow)
3. [vhx.py](#vhx)

4. [outline.py](#outline) *
5. [spriteMaker.py](#spritemaker) *
6. [videoPlayerOne.py and clipsMaker.py](#videoplayerone) *
7. [videoPlayerTwo.py and clipsMaker.py](#videoplayertwo) *
8. [wrapper.py](#wrapper) *

\*opencv



## <a id="dropshadow"></a>1. dropShadow.py
*   **April 17 2024:** Updated dropshadow.py and outline.py to PyQt6.

## <a id="slideshow"></a>2. slideShow.py
*   **August 5 2026:** Added a delete to slideShow in case you need it and a key to the storyBoard.menu to add a flat. SlideShow and wrapper are located in the dots/extras/src directory.<br>
    New video: <https://youtu.be/HGU-3Ia_nm8?si=WxEdQ61a61Pf699G>

*   **June 2026:** Added drag and drop to slideShow and wrapper.<br>
    New video: <https://youtu.be/fhKTW_m-gaI?si=TBuxp1mpwGIiFpGI>

*   **March 15 2026:** Shift-B in SlideShow now hides both the button and title bar.<br>
    New video: <https://youtu.be/fW8V4639t5w>

*   **January 19 2026:** Added 'Select Files' to SlideShow triggered by Shift-S or selected from its help menu.<br>
    New video: <https://youtu.be/W2OrZz24YAM>

*   **December 25 2025:** Changed the FramelessWindowHint toggle in slideshow so it no longer jumps up or down depending on visibility.

*   **December 19 2025:** Added 'Menus' to the videoPlayers helpMenus to display videoPlayer and slideShow help, though not implemented in slideShow's helpMenu yet. Fixed a menu bug so rotate now works in either direction in slideShow as does opening layout.

*   **December 15 2025:** The helpMenus for both videoPlayers and slideShow can be found in VideoPlayerHelp.

*   **November 29 2025:** Shift-B hides or shows the slideShow button group, while Shift-F toggles the window title bar off and on.<br>
    New video: <https://youtu.be/ydgb43BSDv8>

*   **July 10 2025:** Made sure the pop-up menu in slideShow closed and reopened correctly and set a default to display the current directory on open if no buttons have been set.

*   **July 5 2025:** Added three global variables to slideshow to configure hiding the buttons, hiding the title bar, or filling the frame with a background color. Changes remember which photos were rotated and redisplay them properly if the textitem is showing. Added a right-mouse click to pop-up the slideShow help menu and wired selections to run when clicked.<br>
    New video: <https://youtu.be/9hMyVmDN-UA>

*   **May 20 2025:** Added keyboard commands for zoom/scaling (greater/less keys, plus/underscore keys) to slideShow.py and others. Rotating a photo in slideShow.py now stays rotated throughout the session, and typing 'O' resets to opening display.

*   **January 27 2025:** The slideShow app now runs in PySide6.

*   **January 15 2025:** Introduced slideShow.py to visualize photo books, featuring a zoom function, and including bits of code originated by Google Gemini.<br>
    New video: <https://youtu.be/7CWd5Z7IfK4>


[⬆ Return to Top](#top)



## <a id="vhx"></a>3. vhx.py
*   **March 15 2026:** Fixed a long-standing issue with VHX's cursor.<br>
    New video: <https://youtu.be/fW8V4639t5w>

*   **May 20 2025:** Added zoom/scaling keyboard commands to vhx.py. Updated vhx.py to anchor an end and expand/collapse in one direction (right or down) rather than both.

*   **January 27 2025:** Updated VHX to anchor the beginning of the ruler when holding down the 'command' key on a Mac while adjusting length with square brackets. VHX now runs in PySide6.

*   **January 15 2025:** Switched to square brackets in VHX replacing '<' and '>'.<br>
    New video: <https://youtu.be/7CWd5Z7IfK4>

*   **May 8 2024:** Set the opening horizontal width to 1200px and vertical to 900px in VHX.

*   **February 10 2023:** Removed the VHX pixel ruler Shift-V start key; recommended adding the VHX desktop app to the dock/taskbar instead.<br>
    New video: <https://youtu.be/-mpV2f8Qj6w>

*   **October 2022:** VHX can run in PyQt5 with minor edits.<br>
    New video: <https://youtu.be/CLOVUHtD-Ts>

*   **September 2021:** Added screen pixel ruler, vhx.py, running in Dots and as a Mac desktop widget (vhx.app) replacing the JavaFx version.<br>
    New video: <https://youtu.be/98m-fNB16-w>


[⬆ Return to Top](#top)



## <a id="outline"></a>4. outline.py
*   **June 2026:** A new opencv function replaced one originally written in pygame for use in outline.py.<br>
    New video: <https://youtu.be/fhKTW_m-gaI?si=TBuxp1mpwGIiFpGI>

*   **April 17 2024:** Updated dropshadow.py and outline.py to PyQt6 and increased the coverage of the loupeWidget to make it easier to use.

*   **February 22 2022:** Updated outline.py to display a larger image and set the point limit up to 350.<br>
    New video: <https://youtu.be/eAsH9412Bww>

*   **January 2022:** Added outline.py, combining Pygame (required) and PyQt as a way to outline a transparent .png and save the result as an SVG file.<br>
    New video: <https://youtu.be/leTFR89YxA4>


[⬆ Return to Top](#top)



## <a id="spritemaker"></a>5. spriteMaker.py
*   **December 2022:** See SpriteMaker.md for the latest news, especially for later model iPhone owners.<br>
    New video: <https://youtu.be/9i8w6DsY1Ys>

*   **October 2022:** SpriteMaker can run in PyQt5 with minor edits. Open-cv and numpy are required to run Shadows and SpriteMaker.<br>
    New video: <https://youtu.be/CLOVUHtD-Ts>

*   **July 2022:** Broke SpriteMaker out of dots (see SpriteMaker.md for current changes); it can run in PyQt5.3.1 and PyQt5 with minor edits.<br>
    New video: <https://youtu.be/bGYBj_bjEJU>

*   **May 2022:** Added SpriteMaker.py as a standalone app requiring cv2 and numpy, based largely on pathMaker code.<br>
    New video: <https://youtu.be/sySmphW7bYA>


[⬆ Return to Top](#top)



## <a id="videoplayerone"></a>6. videoPlayerOne.py and clipsMaker.py
*   **August 31 2026:** Added code to ctrOnBackground and assembler for videoPlayer. Noted an issue where QVideoWidget in videoPlayerOne didn't update same-name files.

*   **August 26 2026:** Fixed a bug where videoPlayer didn't fill the screen if image width was less than screen width. Added 'Shift-O' to open files and turn clipsMaker off to allow auto-detect to work.

*   **August 15 2026:** Fixed a bug where clipsMaker dropped the directory name and left invisible .mov files on Mac.

*   **January 27 2026:** Added a 'Make a Clip' button to ClipsMaker Settings.

*   **December 25 2025:** Fixed a bug in clipsMaker if running 'Nth' frame.

*   **December 19 2025:** Added 'Menus' to the videoPlayers helpMenus to display videoPlayer help and clipsMaker settings.

*   **December 15 2025:** Created VideoPlayerHelp for videoPlayers; moved MediaPlayer class from videoPlayerOne and Two into videoPlayerShared.

*   **December 10 2025:** Added lines to both videoPlayers to optionally hide the slider on open.

*   **December 9 2025:** Reworked videoPlayerTwo, videoPlayerOne, and videoClipsMaker, resulting in videoPlayerShared.

*   **December 1 2025:** Fixed looping blips in VideoPlayerOne for PyQt6/PySide6; the loop button now only affects PyQt5.

*   **November 29 2025:** VideoPlayerOne can now resize by dragging from the bottom; Shift-S toggles the slider. All three players now share a MediaPlayer class.<br>
    New video: <https://youtu.be/ydgb43BSDv8>

*   **November 23 2024:** Backed out an edit on videoPlayerOne and included it in both the source and extras directories.

*   **November 30 2024:** Script comments out open-cv reference lines in videoPlayerOne if not installed.

*   **September 3 2025:** Added videoClipsMaker and videoClipsWidget alongside videoPlayerOne to assemble stop-motion video clips via OpenCV. ClipsMaker requires OpenCV 4.12+ and outputs a '.mov' file to the working directory. Added three video formats to videoPlayerOne.<br>
    New video: <https://youtu.be/DPYu2mdDE7E>

*   **July 5 2025:** Overhauled VideoPlayerOne to auto-resize and properly display videos on a Mac regardless of aspect ratio using the 'mdls' command in getVideoWidthHeight. Added PlayVideo and AspectRationOn global variables.<br>
    New video: <https://youtu.be/9hMyVmDN-UA>

*   **May 20 2025:** Added zoom/scaling keyboard controls (greater/less keys, plus/underscore keys) to videoPlayerOne.py.

*   **March 2 2025:** Added a first frame display to videoPlayerOne but without screen capture.

*   **January 27 2025:** videoPlayerOne now runs in PySide6.

*   **January 15 2025:** script-qt6.py now works for videoPlayerOne if only running PyQt6; added a zoom feature using square brackets to videoPlayerOne. Included Gemini-originated code in videoPlayerOne.<br>
    New video: <https://youtu.be/7CWd5Z7IfK4>


[⬆ Return to Top](#top)



## <a id="videoplayertwo"></a>7. videoPlayerTwo.py and clipsMaker.py
*   **August 31 2026:** videoPlayerTwo uses QGraphicsVideoItem which avoids the QVideoWidget update issue found in player one.

*   **August 26 2026:** Added 'Shift-O' to open files and turn clipsMaker off to allow auto-detect to work.

*   **August 15 2026:** Fixed a bug where clipsMaker dropped the directory name and left invisible .mov files. Added a clear screen button to videoPlayerTwo.

*   **February 10 2026:** Added Shift-F frameless hint toggle to hide the window title bar in videoPlayerTwo.

*   **January 27 2026:** Added a 'Make a Clip' button to ClipsMaker Settings.

*   **December 25 2025:** Fixed a bug in clipsMaker if running 'Nth' frame.

*   **December 19 2025:** Added 'Menus' to the videoPlayers helpMenus to display videoPlayer help and clipsMaker settings.

*   **December 15 2025:** Created VideoPlayerHelp for videoPlayers; moved MediaPlayer class from videoPlayerOne and Two into videoPlayerShared.

*   **December 10 2025:** Added lines to both videoPlayers to optionally hide the slider on open.

*   **December 9 2025:** Reworked videoPlayerTwo, videoPlayerOne, and videoClipsMaker, merging clipsMaker and its widget into videoPlayerTwo, resulting in videoPlayerShared. Right-mouse-click in videoPlayerTwo now brings up the same help menu as videoPlayerOne.

*   **November 29 2025:** Introduced VideoPlayerTwo (using GraphicsVideoItem) to test features; all three players now share a MediaPlayer class.<br>
    New video: <https://youtu.be/ydgb43BSDv8>


[⬆ Return to Top](#top)


## <a id="wrapper"></a>8. wrapper.py
*   **August 5 2026:** Added wrapperFilters.py containing filter functions that modify blendedImage using sliders based on Google Gemini prompts. Added guides that appear when ready to save the blendedImage. Wrapper is located in dots/extras/src.<br>
    New video: <https://youtu.be/HGU-3Ia_nm8?si=WxEdQ61a61Pf699G>

*   **June 2026:** Introduced the new app wrapper, an OpenCV project (assisted by Gemini Pro and Claude) that creates continuous scrolling backgrounds by blending opposite ends of a photo. Added drag and drop to wrapper.<br>
    New video: <https://youtu.be/fhKTW_m-gaI?si=TBuxp1mpwGIiFpGI>


[⬆ Return to Top](#top)