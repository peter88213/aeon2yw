[Project home page](index) > Changelog

------------------------------------------------------------------------

## Changelog

### Planned features

See the [GitHub "features" project](https://github.com/peter88213/aeon2yw/projects/1).

### v0.18.0 Beta release

- Synchronize existing yWriter project: Scene date/time/duration is updated when scene titles match.

Based on paeon v0.10.2 and PyWriter v3.26.1

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

