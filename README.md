# iRacing-Application-Manager

I was tired of manually starting all of the associated programs for iRacing that I use everytime i restart my computer.
This simple tool lets you configure what tools you use, for example, SimHub and Garage61, and then start/stop or set them to 
autostart whenever you run the application manager.

This solved my problem of: \
A) not wanting to set programs to autostart with windows \
B) constantly forgetting to start Garage61 

It is a little buggy right now with some programs not playing nice, for example iOverlay likes to stay open after we tell it to close.
The code is also pretty ugly, I am working on it. 
## KNOWN ISSUE: sometimes when adding programs to the list via the UI the application locks up. I am working on it. 
for now if it is a problem, just add then to the json file manually, or just close the program and restart it if it locks up.

### how to use/install
To use the software, go to releases on the right and then select the most recent release.
download either the source code, or the prepackaged release.

if you don't have python and/or don't want to install the required packages, the EXE version has everything prepacked.

Once you have downloaded the tool. you can either: \
add programs through the GUI, give the program a name and point the file dialog to the executable location. \
or: \
manually add the file paths to the json file.

