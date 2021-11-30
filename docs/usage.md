[Project homepage](https://peter88213.github.io/aeon2yw)

------------------------------------------------------------------

The aeon2yw Python script 
- creates a new yWriter 7 project from Aeon Timeline 2, or 
- updates date/time/duration in an existing yWriter 7 project from a timeline, or
- updates date/time/duration and creates new events in a timeline from a yWriter 7 project.

## Instructions for use

You might want to have a look at the [tutorial](https://peter88213.github.io/aeon2yw/tutorial)

### Intended usage

The included installation script prompts you to create a shortcut on the desktop. 
- If you drag an *.aeonzip* file onto it and drop it, either a new yWriter project is generated or an existing one is synchronized. 
- If you drag a yWriter project and drop it on the icon, an existing *.aeonzip* file is synchronized. 

### Command line usage

Alternatively, you can

- launch the program on the command line passing the *.aeonzip* or *.yw7* file as an argument, or
- launch the program via a batch file.

usage: `aeon2yw.pyw [--silent] Sourcefile`

#### positional arguments:

`Sourcefile` 

The path of the *.aeonzip* or *.yw7* file.

#### optional arguments:

`--silent`  suppress error messages and the request to confirm overwriting

## Prepare your timeline for export

The included installation script installs a "yWriter" template in the Aeon 2 configuration folder. 
The easiest way is to create new timelines based on this template. It provides the entities and event properties that are converted to yWriter by default.

For existing timelines you have two choices:

- Option 1: Add or rename the required entities and event properties in the Timeline settings.
- Option 2: Customize the *aeon2yw* configuration to fit your timeline (see below).


## Custom configuration

You can override the default settings by providing a configuration file. Be always aware that faulty entries may cause program errors. 

### Global configuration

An optional global configuration file can be placed in the configuration directory in your user profile. It is applied to any project. Its entries override aeon2yw's built-in constants. This is the path:
`c:\Users\<user name>\AppData\Roaming\PyWriter\aeon2yw\config\aeon2yw.ini`
  
### Local project configuration

An optional project configuration file named `aeon2yw.ini` can be placed in your project directory, i.e. the folder containing your yWriter and Aeon Timeline project files. It is only applied to this project. Its entries override aeon2yw's built-in constants as well as the global configuration, if any.

### How to provide/modify a configuration file

The aeon2yw distribution comes with a sample configuration file located in the `sample` subfolder. It contains aeon2yw's default settings and options. You can copy this file to the global configuration folder and edit it.

- The SETTINGS section mainly refers to custom property, role, and type names. 
- Comment lines begin with a `#` number sign. In the example, they refer to the code line immediately above.

This is the configuration explained: 

```
[SETTINGS]

narrative_arc = Narrative

# Name of the user-defined "Narrative" arc.

property_description = Description

# Name of the user-defined scene description property.

property_notes = Notes

# Name of the user-defined scene notes property.

role_location = Location

# Name of the user-defined role for scene locations.

role_item = Item

# Name of the user-defined role for items in a scene.

role_character = Participant

# Name of the user-defined role for characters in a scene.

type_character = Character

# Name of the user-defined "Character" type

type_location = Location

# Name of the user-defined "Location" type

type_item = Item

# Name of the user-defined "Item" type

```

Note: Your custom configuration file does not have to contain all the entries listed above. 
The changed entries are sufficient. 

## Conversion rules for newly created yWriter projects

The names/column labels refer to timelines based on the "yWriter" template. 

-   All events assigned to the "Narrative" arc are converted to regular scenes and placed in a regular chapter (*).
-   All events not assigned to the "Narrative" arc are converted to "Notes" scenes and placed in a "Notes" chapter (*).
-   All scenes are sorted chronologically. 
-   The scene status is "Outline". 
-	The event title is used as scene title (*).
- 	The start date is used as scene date/time, if the start year is 100 or above.
-	The scene duration is calculated, if the start year is 100 or above.
-	Event tags are converted to scene tags, if any (*).
-   "Descriptions" are imported as scene descriptions, if any (*).
-   "Notes" are used as scene notes, if any (*).
-	"Participants" are imported as characters, if any (*).
-	"Locations" are imported, if any (*).
-	"Items" are imported, if any (*).

(*) Applies to the default configuration, but can be customized. 

## Update rules for existing yWriter projects

-   Only scenes that have the same title as an event are updated.
-   If a scene title occurs more than once, the program aborts with an error message.
-   Only scene date, scene time, and scene duration are updated.
- 	The start date is overwritten, if the start year is 100 or above.
-	The scene duration overwritten, if the start year is 100 or above.


## Update rules for Aeon Timeline 2 projects

-   Only events that have the same title as a scene are updated.
-   If a yWriter scene title occurs more than once, the program aborts with an error message.
-   Only event date/time, and event duration are updated.
- 	The start date is overwritten, if the start year is 100 or above.
-	The scene duration overwritten, if the start year is 100 or above.
-   Events are created from new scenes and assigned to the *Narrative* arc.


## Installation path

The **install.bat** installation script installs *aeon2yw.pyw* in the user profile. This is the installation path: 

`c:\Users\<user name>\AppData\Roaming\PyWriter\aeon2yw`
    