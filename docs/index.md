[![Screenshot: Example](Screenshots/screen01.png)](https://raw.githubusercontent.com/peter88213/aeon2yw/main/docs/Screenshots/screen01.png)

[yWriter](http://spacejock.com/yWriter7.html) is a free word processor written by Australian author and programmer Simon Haynes. yWriter's strengths are structuring novels and controlling the progress during the writing process. With the *aeon2yw* Python script, you can convert a novel outline created with Aeon Timeline 2 into a new yWriter project.

## Features

### Create a new yWriter project from a timeline

- The release comes with a template for Aeon Timeline 2 that provides characters, locations and items, as well as yWriter's scene properties such as description and notes.
- Events assigned to the *Narrative* arc are considered scenes.
- The aeon2yw Python script converts Aeon's *.aeonzip* project file into a new yWriter project.
- Scene date, time, and duration are imported, if the year is between 100 and 9999.
- Scene characters, locations, items, relationships, descriptions, notes, and tags are imported.

### Update an existing yWriter project from a timeline

- Update scene date, time, duration, description, tags, and relationships.
- Missing scenes, characters, locations, and items are created.
- Scenes are marked "unused" if the associated event is deleted in Aeon.

### Update an existing timeline from a yWriter project

- Update event date, time, duration, description, tags, and relationships.
- Entity types "Arc", "Character", "Location", and "Item", and a *Narrative* arc are created, if missing.
- Event properties "Description" and "Notes" are created, if missing.
- Missing events, characters, locations, and items are created.
- "Narrative" events are removed if the associated scene is deleted in yWriter.

### Create a new timeline from a yWriter project

- Just update an empty timeline from a yWriter project.

Optionally, a [novelyst](https://peter88213.github.io/novelyst/) plugin can be installed.

 
## Requirements

- [Python 3.6+](https://www.python.org).
- [yWriter](http://spacejock.com/yWriter7.html).
- Aeon Timeline 2. Note: There is now a separate [converter for Aeon Timeline 3](https://peter88213.github.io/aeon3yw). 


## Download and install

[Download the latest release (version 1.6.3)](https://raw.githubusercontent.com/peter88213/aeon2yw/main/dist/aeon2yw_v1.6.3.zip)

- Unzip the downloaded zipfile "aeon2yw_v1.6.3.zip" into a new folder.
- Move into this new folder and launch **setup.pyw**. This installs the script for the local user.
- Create a shortcut on the desktop when asked.
- Open "README.md" for usage instructions.

### Note for Linux users

Please make sure that your Python3 installation has the *tkinter* module. On Ubuntu, for example, it is not available out of the box and must be installed via a separate package. 

------------------------------------------------------------------

[Changelog](changelog)

## Usage

- [Instructions for use](usage)
- [Tutorial](tutorial)

## Credits

- Frederik Lundh published the [xml pretty print algorithm](http://effbot.org/zone/element-lib.htm#prettyprint).


## License

aeon2yw is distributed under the [MIT License](http://www.opensource.org/licenses/mit-license.php).


 




