[Project homepage](https://peter88213.github.io/aeon2yw)

------------------------------------------------------------------

The aeon2yw Python script creates a yWriter 7 project from a csv file exported by Aeon Timeline 2.

## Instructions for use

### Intended usage

The included installation script prompts you to create a shortcut on the desktop. You can launch the program by dragging a csv file and dropping it on the shortcut icon. 

### Command line usage

Alternatively, you can

- launch the program on the command line passing the yWriter project file as an argument, or
- launch the program via a batch file.

usage: `aeon2yw.pyw [--silent] Sourcefile`

#### positional arguments:

`Sourcefile` 

The path of the Aeon Timeline 2 csv export file.

#### optional arguments:

`--silent`  suppress error messages and the request to confirm overwriting


## csv export from Aeon Timeline 2

- The csv file exported by Aeon Timeline 2 must be **comma**-separated.
- Date format is like **1940-11-27**.
- Time format is like **17:43**.


![Aeon 2 csv export settings](Screenshots/Aeon2_export_settings.png)


## Custom configuration

You can override the default settings by providing a configuration file. Be always aware that faulty entries may cause program errors. 

### Global configuration

An optional global configuration file can be placed in the configuration directory in your user profile. It is applied to any project. Its entries override aeon2yw's built-in constants. This is the path:
`c:\Users\<user name>\AppData\Roaming\PyWriter\aeon2yw\config\aeon2yw.ini`
  
The **install.bat** installation script installs a sample configuration file containing aeon2yw's default values. You can modify or delete it. 

### Local project configuration

An optional project configuration file named `aeon2yw.ini` can be placed in your project directory, i.e. the folder containing your yWriter and Timeline project files. It is only applied to this project. Its entries override aeon2yw's built-in constants as well as the global configuration, if any.

### How to provide/modify a configuration file

The aeon2yw distribution comes with a sample configuration file located in the `sample` subfolder. It contains aeon2yw's default settings and options. This file is also automatically copied to the global configuration folder during installation. You best make a copy and edit it.

- The SETTINGS section mainly refers to "labels", i.e. The csv field contents of the first row, which denote the columns. They might have to be adapted to your specific Aeon project and export settings. If you change them, the program might behave differently than described in the description of the conversion rules below. Make sure the indicated csv fields contain data that can be processed by yWriter.
- The OPTIONS section comprises options for regular program execution. 
- Comment lines begin with a `#` number sign. In the example, they refer to the code line immediately above.

This is the configuration explained: 

```
[SETTINGS]

scene_marker = Scene

# String that indicates an event to be exported as normal
# scene, if "export_all_events" is "No"
# If the scene marker is left blank, all events will be
# imported as normal scenes.
# In this case, the entry looks like "scene_marker ="

scene_label = Tags

# Label of the csv field that contains the "scene_marker"
# indicator.

title_label = Title

# Label of the csv field whose contents are exported
# as the scene's title to yWriter.

date_time_label = Start Date

# Label of the csv field whose contents are exported
# as the scene's date/time to yWriter.

description_label = Description

# Label of the csv field whose contents are exported
# as the scene's description to yWriter.

notes_label = Notes

# Label of the csv field whose contents are exported
# as the scene's notes to yWriter.

tag_label = Arc

# Label of the csv field whose contents are exported
# as the scene's tags to yWriter.

location_label = Location

# Label of the csv field whose contents are exported
# as the scene's locations to yWriter.

item_label = Item

# Label of the csv field whose contents are exported
# as the scene's items to yWriter.

character_label = Participant

# Label of the csv field whose contents are exported
# as the scene's characters to yWriter.

[OPTIONS]

export_all_events = Yes

# Yes: Export non-scene events as "Notes" type scenes
#      to yWriter.
# No:  Do not export non-scene events to yWriter.
# This option exists only if the scene marker is not
# left blank.

```

## Conversion rules

The column labels refer to the example timeline "Murder on the Orient Express". 

-   All events tagged as "Scene" (*) (case sensitive) are converted to regular scenes.
-   All events not tagged as "Scene" (*) are converted to "Notes" scenes.
-   All scenes are placed in a single chapter.
-   All scenes are sorted chronologically (Note: "BC" is not evaluated). 
-   The scene status is "Outline". 
-	The event title is used as scene title (*).
- 	The start date is used as scene date/time (*).
-	Duration and end date are not used.
-   "Descriptions" are used as scene descriptions, if any (*).
-   "Notes" are used as scene notes, if any (*).
-	"Arcs" are converted to scene tags, if any (*).
-	"Participants" are imported as characters, if any (*).
-	"Locations" are imported, if any (*).
-	"Items" are imported, if any (*).

(*) Applies to the default configuration, but can be customized. 


## Installation path

The **install.bat** installation script installs *aeon2yw.pyw* in the user profile. This is the installation path: 

`c:\Users\<user name>\AppData\Roaming\PyWriter\aeon2yw`
    