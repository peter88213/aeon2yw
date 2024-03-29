[Project homepage](https://peter88213.github.io/aeon2yw)

------------------------------------------------------------------

The aeon2yw Python script 
- creates a new yWriter 7 project from Aeon Timeline 2, or 
- updates an existing yWriter 7 project from a timeline, or
- updates an existing timeline from a yWriter 7 project.

## Instructions for use

You might want to have a look at the [tutorial](https://peter88213.github.io/aeon2yw/tutorial)

### Intended usage

The included installation script prompts you to create a shortcut on the desktop. 
- If you drag an *.aeonzip* file onto it and drop it, either a new yWriter project is generated or an existing one is synchronized. 
- If you drag a yWriter project and drop it on the icon, an existing *.aeonzip* file is synchronized. 

### Context menu (Windows only)

Under Windows, you optionally can launch *aeon2yw* via context menu.

After installation, you can add the context menu entries by double-clicking  `add_context_menu.reg`. 
You may be asked for approval to modify the Windows registry. Please accept.

- On right-clicking a *.yw7* file, a **Sync with Aeon Timeline 2** option appears.
- On right-clicking an *.aeonzip* file, a **Sync with yWriter** option appears.

You can remove the context menu entries by double-clicking  `rem_context_menu.reg`.

Please note that these context menus depend on the currently installed Python version. After a major Python update you may need to run the setup program again and renew the registry entries.

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
- Option 2: Customize the *aeon2yw* configuration to fit your timeline, see [Custom configuration](#custom-configuration).


## Synchronization in detail

### Known limitations

- "Narrative" events that begin before 0100-01-01 in the timeline, will not be synchronized with yWriter, because yWriter can not handle these dates.
- The same applies to the scene duration in this case, i.e. the event duration in Timeline and the scene duration in yWriter may differ.

### Conversion rules for newly created yWriter projects

The names/column labels refer to timelines based on the "yWriter" template. 

- If an Aeon event title occurs more than once, the program aborts with an error message.
- Events assigned to the "Narrative" arc are converted to regular scenes (*).
- Optionally, events not assigned to the "Narrative" arc are converted to "Notes" scenes (**).
- New scenes are put into a new chapter named "New scenes". 
- All scenes are sorted chronologically. 
- The scene status is "Outline". 
- The event title is used as scene title (*).
- The start date is used as scene date/time, if the start year is 100 or above.
- The scene duration is calculated, if the start year is 100 or above.
- Event tags are converted to scene tags, if any (*).
- "Descriptions" are imported as scene descriptions, if any (*).
- "Notes" are used as scene notes, if any (*).
- "Participants" are imported as characters, if any (*).
- "Locations" are imported, if any (*).
- "Items" are imported, if any (*).

### Update rules for existing yWriter projects

- Only scenes that have the same title as an event are updated.
- If an Aeon event title occurs more than once, the program aborts with an error message.
- If a yWriter scene title occurs more than once, the program aborts with an error message.
- Scenes are marked "unused" if the associated event is deleted in Aeon.
- Scene date, scene time, and scene duration are updated.
- Non-empty scene description and scene tags are updated.
- Notes of events with a matching title are appended to the scene notes.
- The start date is overwritten, if the start year is 100 or above.
- The scene duration is overwritten, if the start year is 100 or above.
- New "Normal" type scenes are created from "Narrative" events, if missing (*).
- Optionally, new "Notes" type scenes are created from non-"Narrative" events, if missing (**).
- New scenes are put into a new chapter named "New scenes". 
- New arcs, characters, locations, and items are added, if assigned to "Narrative" events.
- Arc, character, location, and item relationships are updated, if the entity names match.
- When processing unspecific "day/hour/minute" information, a reference date that can be set in the configuration is used.


### Update rules for Aeon Timeline 2 projects

- If an Aeon event title occurs more than once, the program aborts with an error message.
- If a yWriter scene title occurs more than once, the program aborts with an error message.
- Event date/time and event span are updated, if the start year is 100 or above.
- Updated event span is specified in days/hours/minutes as in yWriter.
- Non-empty event description and event tags are updated.
- Event properties "Description" and "Notes" are created, if missing.
- Events created or updated from "Normal" scenes are assigned to the *Narrative* arc (*).
- "Narrative" events are removed if the associated scene is deleted in yWriter.
- Optionally, events are created or updated from "Notes" scenes (not assigned to the *Narrative* arc)(**).
- Entity types "Arc", "Character", "Location", and "Item" are created, if missing.
- A "Narrative" arc is created, if missing.
- A "Storyline" arc role is created, if missing.
- New arcs, characters, locations, and items are added, if assigned to scenes.
- Arc, character, location, and item relationships are updated, if the entity names match.
- When creating events from scenes without any date/time information, they get the default date from the configuration, and are sorted in reading order.
- When processing unspecific "day/hour/minute" information, a reference date that can be set in the configuration is used.

(*) Applies to the default configuration, but can be customized.

(**) To be set in the configuration file.


## Custom configuration

You can override the default settings by providing a configuration file. Be always aware that faulty entries may cause program errors. 

### Global configuration

An optional global configuration file can be placed in the configuration directory in your user profile. It is applied to any project. Its entries override aeon2yw's built-in constants. This is the path:
`c:\Users\<user name>\.pywriter\aeon2yw\config\aeon2yw.ini`
  
### Local project configuration

An optional project configuration file named `aeon2yw.ini` can be placed in your project directory, i.e. the folder containing your yWriter and Aeon Timeline project files. It is only applied to this project. Its entries override aeon2yw's built-in constants as well as the global configuration, if any.

### How to provide/modify a configuration file

The aeon2yw distribution comes with a sample configuration file located in the `sample` subfolder. It contains aeon2yw's default settings and options. You can copy this file to the global configuration folder and edit it.

- The SETTINGS section mainly refers to custom property, role, and type names. 
- Comment lines begin with a `#` number sign. In the example, they refer to the code line immediately above.

This is the configuration explained: 

```ini
[SETTINGS]

default_date_time = 2023-01-01 00:00:00

# Date/time used for new events and for converted events
# where the scene has no date/time information at all.
# The date is also used as a reference when converting 
# unspecific scene "days" into event dates.
# The format must be yyyy-mm-dd hh:mm:ss
# If the format is invalid, the current date/time is used instead.

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

color_scene = Red

# Color of new scene events

color_event = Yellow

# Color of new non-scene events

[OPTIONS]

scenes_only = Yes

# Yes: Create new scenes from "narrative" events only.
# No: Additionally create "Notes scenes" from "non-narrative" events.

add_moonphase = No

# Yes: Add the moon phase to the event properties.
# No: Update moon phase, if already defined as event property.
```

Note: Your custom configuration file does not have to contain all the entries listed above. 
The changed entries are sufficient. 

## Installation path

The setup script installs *aeon2yw.pyw* in the user profile. This is the installation path on Windows: 

`c:\Users\<user name>\.pywriter\aeon2yw`
    
