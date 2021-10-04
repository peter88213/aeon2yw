[![Screenshot: Example](Screenshots/screen01.png)](https://raw.githubusercontent.com/peter88213/aeon2yw/main/docs/Screenshots/screen01.png)

[yWriter](http://spacejock.com/yWriter7.html) is a free word processor written by Australian author and programmer Simon Haynes. yWriter's strengths are structuring novels and controlling the progress during the writing process. With the *aeon2yw* Python script, you can convert a novel outline created with Aeon Timeline 2 into a new yWriter project.

## Features

- A template for Aeon Timeline 2 that provides characters, locations and items, as well as yWriter's scene properties such as description, notes and viewpoint.
- With this template, events get a "Scene" checkbox. Events marked as scenes are converted to regular scenes; other events become "Notes" scenes.
- A Python script that converts Aeon's csv export into a new yWriter project.
- Events are converted to scenes in one single chapter.
- The scenes have a start time and a duration, if the year is between 100 and 9999.
- The scenes are sorted chronologically.
- Characters, locations and items are imported, if any.
- Scene descriptions and scene notes are imported, if any.
- Scene tags are imported, if any.

 
## Requirements

- Windows.
- [Python 3](https://www.python.org). Python 3.4 or more recent will work. However, Python 3.7 or above is highly recommended.
- [yWriter](http://spacejock.com/yWriter7.html).
- Aeon Timeline 2.


## Download and install

[Download the latest release (version 0.14.0)](https://raw.githubusercontent.com/peter88213/aeon2yw/main/dist/aeon2yw_v0.14.0.zip)

- Unzip the downloaded zipfile "aeon2yw_v0.14.0.zip" into a new folder.
- Move into this new folder and launch **install.bat**. This installs the script for the local user.
- Create a shortcut on the desktop when asked.
- Open "README.md" for usage instructions.

[Changelog](changelog)

## Usage

- [Instructions for use](usage)
- [Tutorial](tutorial)

## Credits

- Frederik Lundh published the [xml pretty print algorithm](http://effbot.org/zone/element-lib.htm#prettyprint).


## License

aeon2yw is distributed under the [MIT License](http://www.opensource.org/licenses/mit-license.php).


 




