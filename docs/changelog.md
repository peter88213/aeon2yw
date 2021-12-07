[Project home page](index) > Changelog

------------------------------------------------------------------------

## Changelog

### Planned features

See the [GitHub "features" project](https://github.com/peter88213/aeon2yw/projects/1).

### v0.34.0 Update yWriter characters, locations, and items from Aeon

- Add new characters, locations, and items, if assigned to events.
- Update relationships to characters, locations, and items.

Based on PyWriter v3.28.1.

### v0.32.1 Update deleted events from Aeon

- Mark scenes "unused" if the associated event is deleted in Aeon.

Based on PyWriter v3.28.1.

### v0.32.0 Update characters/locations/items and relationships from yWriter

- Add new characters, locations, and items from yWriter, if assigned to scenes.
- Update existing characters, locations, and items from yWriter.
- Update event relationships (roles) from yWriter.
- Remove events if the associated scene is deleted in yWriter.

Based on PyWriter v3.28.1.

### v0.30.0 Update scene tags and descriptions in both directions

- Updating "Notes" scenes is optional now.
- Create scenes from new events when updating yw7.
- Update scene descriptions and tags in both directions.
- Append event notes to scene notes when updating yw7.
- Add missing types and roles when updating the timeline.
- Check whether there is an "AD" era.
- Update the sample templates.

Based on PyWriter v3.28.0.

### v0.28.0 Update scene type in both directions

- Update yWriter scene type from Aeon.
- Update event assignment to "Narrative" arc from yWriter.

Based on PyWriter v3.28.0.

### v0.26.0 Update event date/time/duration from yWriter

- Update event date/time/span from yWriter, if the start year is 100 or above.

Based on PyWriter v3.28.0.

### v0.24.0 Optional beta release

Same functionality as v0.22.2.
Make the project independent from the paeon library.

Based on PyWriter v3.28.0.

### v0.22.2 Beta release

Enhance Aeon 2 update from yWriter

- Add "Arc" type, if missing.
- Add "Narrative" arc, if missing.

Based on paeon v0.14.2 and PyWriter v3.28.0.

### v0.22.1 Beta bugfix release

- Fix a bug where "Trash" scenes are converted to events.
- Fix a bug where unreadable timelines are generated if there is no "Narrative" arc.

Based on paeon v0.14.1 and PyWriter v3.28.0.

### v0.22.0 Beta release

- Make the colors keyword arguments.
- Create events not assigned to an arc from "Notes" scenes.
- Do not create events from unused and "Trash" scenes.
- Check source and target for ambiguous titles.

Based on paeon v0.14.0 and PyWriter v3.28.0.

### v0.20.0 Beta release

- Abandon the "Viewpoint" property.
- Abandon the "Scene" property. Scene events are to be assigned to the "Narrative" arc.
- Synchronize existing Aeon project
    - Scene date/time/duration is updated when scene titles match.
    - Generate events from new scenes and assign them to the "narrative" arc.

Based on paeon v0.12.0 and PyWriter v3.28.0

### v0.18.0 Beta release

- Synchronize existing yWriter project: Scene date/time/duration is updated when scene titles match.

Based on paeon v0.10.3 and PyWriter v3.26.1

### v0.16.2 Bugfix update

- Fix a bug where scene duration specified in years/months/weeks is calculated the wrong way.

Based on paeon v0.10.2 and PyWriter v3.26.1

### v0.16.1 Optional update

Apply paeon update to minimize the amount of unused code.

Based on paeon v0.10.1 and PyWriter v3.26.1

### v0.16.0 Process the native .aeonzip file format

- Process the Aeon Timeline 2 .aeonzip format.
- Create different chapters for scenes and non-scene events.
- Update the configuration.
- Update the Aeon 2 "yWriter" template.

Based on paeon v0.10.0 and PyWriter v3.26.1

### v0.14.3 Beta release 

- Change the default value for invalid date from "-0001-01-01" to "0001-01-01" in order to avoid isoformat errors.

Based on PyWriter v3.24.3

### v0.14.2 Beta release 

- Update documentation: Use the term "import" from yWriter's point of view.
- Rename the option "export_all_events" to "import_all_events".

Based on PyWriter v3.24.3

### v0.14.1 Beta release

- Restore the global configuration.

Based on PyWriter v3.24.3

### v0.14.0 Beta release

- Calculate scene duration.
- Process viewpoint, if any.
- Copy Aeon 2 "yWriter" template on installation.
- Adapt default settings to the "yWriter" Aeon template.
- Abandon the global configuration.
- Update the sample configuration file.
- Substitute all sorts of non-"AD" date/time.
- Abandon compatibility with Aeon Timeline version 3 (there is a new project for Aeon Timeline 3 conversion).

Based on PyWriter v3.24.3

### v0.12.0 compatible with Aeon Timeline version 3

- Aeon Timeline 3 csv export will work the same way, but the "narrative" is not supported yet.
- Improve error messages in case of csv structure mismatch.

Based on PyWriter v3.24.3

### v0.10.4 Bugfix release

- Fix a bug causing an exception when a new item is added to a scene.

Based on PyWriter v3.18.1

### v0.10.3 No automatic shortcut creation

- Due to sporadic security warnings, the automatic shortcut creation during installation is removed. The user is now guided to create the application shortcut manually.  

Based on PyWriter v3.16.0

### v0.10.1 Adjust installation script

- Try to avoid a "false positive" security warning caused by the powershell call in the installation batch script.

Based on PyWriter v3.16.0

### v0.10.0 Add option to disable scene filtering

- If the scene marker is left blank in the configuration, all events will be imported as normal scenes.

Based on PyWriter v3.14.0

### v0.8.0 Read configuration file

Based on PyWriter v3.14.0

### v0.6.4 Non-scene export is optional

- Export of events that are not tagged as scenes is optional.

Based on PyWriter v3.12.9

### v0.6.3 Allow an even more flexible csv structure

- Allow an even more flexible csv structure by passing all labels as parameters.

Based on PyWriter v3.12.9

### v0.6.2 Allow a flexible csv structure

- Process multiple events occurring at the same time.
- Allow a flexible csv structure by passing the identifiers as parameters.
- Import items, if any.
- Import scene notes, if any.

Based on PyWriter v3.12.9

### v0.6.1 Loosen the conventions

Tags that mark scenes are case-insensitive.

Based on PyWriter v3.12.9

### v0.6.0 Add Tkinter GUI

Based on PyWriter v3.12.9

### v0.4.0 Beta test release

Based on PyWriter v3.12.9

