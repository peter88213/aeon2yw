[![Screenshot: Example](Screenshots/screen01.png)](https://raw.githubusercontent.com/peter88213/aeon2yw/main/docs/Screenshots/screen01.png)

[yWriter](http://spacejock.com/yWriter7.html) is a free word processor written by Australian author and programmer Simon Haynes. yWriter's strengths are structuring novels and controlling the progress during the writing process. With the *aeon2yw* Python script, you can convert a novel outline created with Aeon Timeline 2 into a new yWriter project.

## Features

- The release comes with a template for Aeon Timeline 2 that provides characters, locations and items, as well as yWriter's scene properties such as description and notes.
- With this template, events get a "Scene" checkbox. Events marked as scenes are converted to regular scenes; other events become "Notes" scenes.
- The aeon2yw Python script converts Aeon's *.aeonzip* project file into a new yWriter project.
- Events marked as scenes are converted to scenes in one single chapter.
- Other events are converted to "Notes" scenes in another chapter.
- The scenes have a start time, if the year is between 100 and 9999.
- The scenes have a duration.
- The scenes are sorted chronologically.
- Characters, locations and items are imported, if any.
- Scene descriptions and scene notes are imported, if any.
- Scene tags are imported, if any.
- If a yWriter project with the same name as the timeline already exists, The date, time, and duration of scenes with a matching title are updated from the timeline.

 
## Requirements

- Windows.
- [Python 3.7+](https://www.python.org).
- [yWriter](http://spacejock.com/yWriter7.html).
- Aeon Timeline 2. Note: There is now a separate [converter for Aeon Timeline 3](https://peter88213.github.io/aeon3yw). 


## Download and install

[Download the latest release (version 0.19.2)](https://raw.githubusercontent.com/peter88213/aeon2yw/main/dist/aeon2yw_v0.19.2.zip)

- Unzip the downloaded zipfile "aeon2yw_v0.19.2.zip" into a new folder.
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


 




