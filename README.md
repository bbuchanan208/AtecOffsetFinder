# AtecOffsetFinder
The Offset finder currently only works for the children's version of ATEC, assessments 10-21.

## How to properly build the Offset Finder:
1. Clone Repo and install all requirements.
2. Unzip FFMPEG and extract content to project directory
3. Run the offsetFinder.py file

## How to properly use the Offset Finder:

### A folder of videos
0. Ensure that the folder/directory contains folders labeled 10,11, ..., 21. Inside each folder that is numbered, it should contain a .mp4 video
1. Press the "Load Folder" button and select the appropriate folder.
2. Play the input audio and select the first word that you hear
3. Press the "Play comaprison Audio" button. If you do not hear an echo, press the "Confirm Offset & and get next video in folder". If you do hear an echo, continue to step 4.
4. Use the "<--" and "-->" buttons adjust the offset. Attempt to line up the peaks of the graph. Go to Step 3.
5. Repeat steps 3 and 4 until tasks 10-21 display a green color, indicating you have found the all of the offsets.
6. Press the "save results to file" button to view the offset in the Python console.

### An individual video
1. Select the appropriate video
2. Play the input audio and select the first word that you hear
3. Press the "Play comaprison Audio" button. If you do not hear an echo, press the "Confirm Offset & reset button". If you do hear an echo, continue to step 4.
4. Use the "<--" and "-->" buttons adjust the offset. Attempt to line up the peaks of the graph. Go to Step 5. 
5. Press the "save results to file" button to view the offset in the Python console.

## Important notes:
* If the offset is negative, the graph may not be accurate, but the audio tracks will be accurate when "play comparison audio" is pressed.
* The "Save results to file" button will print the results to the python console. This was found to be faster then saving the results to a text file and having to open the file to view the results. This can be reversed by commenting/uncommenting the code in the _save_file function.
