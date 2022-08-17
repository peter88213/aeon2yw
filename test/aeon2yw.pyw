#!/usr/bin/env python3
"""Synchronize Aeon Timeline 2 and yWriter

Version @release
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse
from pathlib import Path
import sys
import gettext
import locale

ERROR = '!'

# Initialize localization.
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
CURRENT_LANGUAGE = locale.getdefaultlocale()[0][:2]
try:
    t = gettext.translation('pywriter', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message

__all__ = ['ERROR', '_', 'LOCALE_PATH', 'CURRENT_LANGUAGE']


class Ui:
    """Base class for UI facades, implementing a 'silent mode'.
    
    Public methods:
        ask_yes_no(text) -- return True or False.
        set_info_what(message) -- show what the converter is going to do.
        set_info_how(message) -- show how the converter is doing.
        start() -- launch the GUI, if any.
        show_warning(message) -- Stub for displaying a warning message.
        
    Public instance variables:
        infoWhatText -- buffer for general messages.
        infoHowText -- buffer for error/success messages.
    """

    def __init__(self, title):
        """Initialize text buffers for messaging.
        
        Positional arguments:
            title -- application title.
        """
        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        """Return True or False.
        
        Positional arguments:
            text -- question to be asked. 
            
        This is a stub used for "silent mode".
        The application may use a subclass for confirmation requests.    
        """
        return True

    def set_info_what(self, message):
        """Show what the converter is going to do.
        
        Positional arguments:
            message -- message to be buffered. 
        """
        self.infoWhatText = message

    def set_info_how(self, message):
        """Show how the converter is doing.
        
        Positional arguments:
            message -- message to be buffered.
            
        Print the message to stderr, replacing the error marker, if any.
        """
        if message.startswith(ERROR):
            message = f'FAIL: {message.split(ERROR, maxsplit=1)[1].strip()}'
            sys.stderr.write(message)
        self.infoHowText = message

    def start(self):
        """Launch the GUI, if any.
        
        To be overridden by subclasses requiring
        special action to launch the user interaction.
        """

    def show_warning(self, message):
        """Stub for displaying a warning message."""
import tkinter as tk
from tkinter import messagebox


class UiTk(Ui):
    """UI subclass implementing a Tkinter facade.
    
    Public methods:
        ask_yes_no(text) -- query yes or no with a pop-up box.
        set_info_what(message) -- show what the converter is going to do.
        set_info_how(message) -- show how the converter is doing.
        start() -- start the Tk main loop.
        show_warning(message) -- Display a warning message box.

    Public instance variables: 
        root -- tk root window.
    """

    def __init__(self, title):
        """Initialize the GUI window.
        
        Positional arguments:
            title -- application title to be displayed at the window frame.
            
        Extends the superclass constructor.
        """
        super().__init__(title)
        self._title = title
        self.root = tk.Tk()
        self.root.minsize(400, 150)
        self.root.resizable(width=tk.FALSE, height=tk.FALSE)
        self.root.title(title)
        self._appInfo = tk.Label(self.root, text='')
        self._appInfo.pack(padx=20, pady=5)
        self._processInfo = tk.Label(self.root, text='', padx=20)
        self._processInfo.pack(pady=20, fill='both')
        self.root.quitButton = tk.Button(text=_("Quit"), command=quit)
        self.root.quitButton.config(height=1, width=10)
        self.root.quitButton.pack(pady=10)

    def ask_yes_no(self, text):
        """Query yes or no with a pop-up box.
        
        Positional arguments:
            text -- question to be asked in the pop-up box. 
            
        Overrides the superclass method.       
        """
        return messagebox.askyesno(_("WARNING"), text)

    def set_info_what(self, message):
        """Show what the converter is going to do.
        
        Positional arguments:
            message -- message to be displayed. 
            
        Display the message at the _appinfo label.
        Overrides the superclass method.
        """
        self.infoWhatText = message
        self._appInfo.config(text=message)

    def set_info_how(self, message):
        """Show how the converter is doing.
        
        Positional arguments:
            message -- message to be displayed. 
            
        Display the message at the _processinfo label.
        Overrides the superclass method.
        """
        if message.startswith(ERROR):
            self._processInfo.config(bg='red')
            self._processInfo.config(fg='white')
            self.infoHowText = message.split(ERROR, maxsplit=1)[1].strip()
        else:
            self._processInfo.config(bg='green')
            self._processInfo.config(fg='white')
            self.infoHowText = message
        self._processInfo.config(text=self.infoHowText)

    def start(self):
        """Start the Tk main loop."""
        self.root.mainloop()

    def show_open_button(self, open_cmd):
        """Add an 'Open' button to the main window.
        
        Positional argument:
            open_cmd -- subclass method that opens the file.
        """
        self.root.openButton = tk.Button(text=_("Open"), command=open_cmd)
        self.root.openButton.config(height=1, width=10)
        self.root.openButton.pack(pady=10)

    def show_warning(self, message):
        """Display a warning message box."""
        messagebox.showwarning(self._title, message)
from configparser import ConfigParser


class Configuration:
    """Application configuration, representing an INI file.

        INI file sections:
        <self._sLabel> - Strings
        <self._oLabel> - Boolean values

    Public methods:
        set(settings={}, options={}) -- set the entire configuration without writing the INI file.
        read(iniFile) -- read a configuration file.
        write(iniFile) -- save the configuration to iniFile.

    Public instance variables:    
        settings - dictionary of strings
        options - dictionary of boolean values
    """

    def __init__(self, settings={}, options={}):
        """Initalize attribute variables.

        Optional arguments:
            settings -- default settings (dictionary of strings)
            options -- default options (dictionary of boolean values)
        """
        self.settings = None
        self.options = None
        self._sLabel = 'SETTINGS'
        self._oLabel = 'OPTIONS'
        self.set(settings, options)

    def set(self, settings=None, options=None):
        """Set the entire configuration without writing the INI file.

        Optional arguments:
            settings -- new settings (dictionary of strings)
            options -- new options (dictionary of boolean values)
        """
        if settings is not None:
            self.settings = settings.copy()
        if options is not None:
            self.options = options.copy()

    def read(self, iniFile):
        """Read a configuration file.
        
        Positional arguments:
            iniFile -- str: path configuration file path.
            
        Settings and options that can not be read in, remain unchanged.
        """
        config = ConfigParser()
        config.read(iniFile, encoding='utf-8')
        if config.has_section(self._sLabel):
            section = config[self._sLabel]
            for setting in self.settings:
                fallback = self.settings[setting]
                self.settings[setting] = section.get(setting, fallback)
        if config.has_section(self._oLabel):
            section = config[self._oLabel]
            for option in self.options:
                fallback = self.options[option]
                self.options[option] = section.getboolean(option, fallback)

    def write(self, iniFile):
        """Save the configuration to iniFile.

        Positional arguments:
            iniFile -- str: path configuration file path.
        """
        config = ConfigParser()
        if self.settings:
            config.add_section(self._sLabel)
            for settingId in self.settings:
                config.set(self._sLabel, settingId, str(self.settings[settingId]))
        if self.options:
            config.add_section(self._oLabel)
            for settingId in self.options:
                if self.options[settingId]:
                    config.set(self._oLabel, settingId, 'Yes')
                else:
                    config.set(self._oLabel, settingId, 'No')
        with open(iniFile, 'w', encoding='utf-8') as f:
            config.write(f)


def open_document(document):
    """Open a document with the operating system's standard application."""
    try:
        os.startfile(os.path.normpath(document))
        # Windows
    except:
        try:
            os.system('xdg-open "%s"' % os.path.normpath(document))
            # Linux
        except:
            try:
                os.system('open "%s"' % os.path.normpath(document))
                # Mac
            except:
                pass


class YwCnv:
    """Base class for Novel file conversion.

    Public methods:
        convert(sourceFile, targetFile) -- Convert sourceFile into targetFile.
    """

    def convert(self, source, target):
        """Convert source into target and return a message.

        Positional arguments:
            source, target -- Novel subclass instances.

        Operation:
        1. Make the source object read the source file.
        2. Make the target object merge the source object's instance variables.
        3. Make the target object write the target file.
        Return a message beginning with the ERROR constant in case of error.

        Error handling:
        - Check if source and target are correctly initialized.
        - Ask for permission to overwrite target.
        - Pass the error messages of the called methods of source and target.
        - The success message comes from target.write(), if called.       
        """
        if source.filePath is None:
            return f'{ERROR}{_("File type is not supported")}: "{os.path.normpath(source.filePath)}".'

        if not os.path.isfile(source.filePath):
            return f'{ERROR}{_("File not found")}: "{os.path.normpath(source.filePath)}".'

        if target.filePath is None:
            return f'{ERROR}{_("File type is not supported")}: "{os.path.normpath(target.filePath)}".'

        if os.path.isfile(target.filePath) and not self._confirm_overwrite(target.filePath):
            return f'{ERROR}{_("Action canceled by user")}.'

        message = source.read()
        if message.startswith(ERROR):
            return message

        message = target.merge(source)
        if message.startswith(ERROR):
            return message

        return target.write()

    def _confirm_overwrite(self, fileName):
        """Return boolean permission to overwrite the target file.
        
        Positional argument:
            fileName -- path to the target file.
        
        This is a stub to be overridden by subclass methods.
        """
        return True


class YwCnvUi(YwCnv):
    """Base class for Novel file conversion with user interface.

    Public methods:
        export_from_yw(sourceFile, targetFile) -- Convert from yWriter project to other file format.
        create_yw(sourceFile, targetFile) -- Create target from source.
        import_to_yw(sourceFile, targetFile) -- Convert from any file format to yWriter project.

    Instance variables:
        ui -- Ui (can be overridden e.g. by subclasses).
        newFile -- str: path to the target file in case of success.   
    """

    def __init__(self):
        """Define instance variables."""
        self.ui = Ui('')
        # Per default, 'silent mode' is active.
        self.newFile = None
        # Also indicates successful conversion.

    def export_from_yw(self, source, target):
        """Convert from yWriter project to other file format.

        Positional arguments:
            source -- YwFile subclass instance.
            target -- Any Novel subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, os.path.normpath(source.filePath), target.DESCRIPTION, os.path.normpath(target.filePath)))
        message = self.convert(source, target)
        self.ui.set_info_how(message)
        if message.startswith(ERROR):
            self.newFile = None
        else:
            self.newFile = target.filePath

    def create_yw7(self, source, target):
        """Create target from source.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - Tf target already exists as a file, the conversion is cancelled,
          an error message is sent to the UI.
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Create a yWriter project file from {0}\nNew project: "{1}"').format(source.DESCRIPTION, os.path.normpath(target.filePath)))
        if os.path.isfile(target.filePath):
            self.ui.set_info_how(f'{ERROR}{_("File already exists")}: "{os.path.normpath(target.filePath)}".')
        else:
            message = self.convert(source, target)
            self.ui.set_info_how(message)
            if message.startswith(ERROR):
                self.newFile = None
            else:
                self.newFile = target.filePath

    def import_to_yw(self, source, target):
        """Convert from any file format to yWriter project.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Delete the temporay file, if exists.
        5. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, os.path.normpath(source.filePath), target.DESCRIPTION, os.path.normpath(target.filePath)))
        message = self.convert(source, target)
        self.ui.set_info_how(message)
        self._delete_tempfile(source.filePath)
        if message.startswith(ERROR):
            self.newFile = None
        else:
            self.newFile = target.filePath
            if target.scenesSplit:
                self.ui.show_warning(_('New scenes created during conversion.'))

    def _confirm_overwrite(self, filePath):
        """Return boolean permission to overwrite the target file.
        
        Positional arguments:
            fileName -- path to the target file.
        
        Overrides the superclass method.
        """
        return self.ui.ask_yes_no(_('Overwrite existing file "{}"?').format(os.path.normpath(filePath)))

    def _delete_tempfile(self, filePath):
        """Delete filePath if it is a temporary file no longer needed."""
        if filePath.endswith('.html'):
            # Might it be a temporary text document?
            if os.path.isfile(filePath.replace('.html', '.odt')):
                # Does a corresponding Office document exist?
                try:
                    os.remove(filePath)
                except:
                    pass
        elif filePath.endswith('.csv'):
            # Might it be a temporary spreadsheet document?
            if os.path.isfile(filePath.replace('.csv', '.ods')):
                # Does a corresponding Office document exist?
                try:
                    os.remove(filePath)
                except:
                    pass

    def _open_newFile(self):
        """Open the converted file for editing and exit the converter script."""
        open_document(self.newFile)
        sys.exit(0)
from datetime import datetime
from datetime import timedelta
from urllib.parse import quote


class Chapter:
    """yWriter chapter representation.
    
    Public instance variables:
        title -- str: chapter title (may be the heading).
        desc -- str: chapter description in a single string.
        chLevel -- int: chapter level (part/chapter).
        chType -- int: chapter type yWriter 7.0.7.2+ (Normal/Notes/Todo).
        isUnused -- bool: True, if the chapter is marked "Unused".
        suppressChapterTitle -- bool: uppress chapter title when exporting.
        isTrash -- bool: True, if the chapter is the project's trash bin.
        suppressChapterBreak -- bool: Suppress chapter break when exporting.
        srtScenes -- list of str: the chapter's sorted scene IDs.        
    """

    def __init__(self):
        """Initialize instance variables."""
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self.chLevel = None
        # int
        # xml: <SectionStart>
        # 0 = chapter level
        # 1 = section level ("this chapter begins a section")

        self.chType = None
        # int
        # xml: <ChapterType>
        # 0 = Normal
        # 1 = Notes
        # 2 = Todo
        # Applies to projects created by yWriter version 7.0.7.2+.
        #
        # xml: <Type>
        # 0 = chapter type (marked "Chapter")
        # 1 = other type (marked "Other")
        # Applies to projects created by a yWriter version prior to 7.0.7.2.

        self.isUnused = None
        # bool
        # xml: <Unused> -1

        self.suppressChapterTitle = None
        # bool
        # xml: <Fields><Field_SuppressChapterTitle> 1
        # True: Chapter heading not to be displayed in written document.
        # False: Chapter heading to be displayed in written document.

        self.isTrash = None
        # bool
        # xml: <Fields><Field_IsTrash> 1
        # True: This chapter is the yw7 project's "trash bin".
        # False: This chapter is not a "trash bin".

        self.suppressChapterBreak = None
        # bool
        # xml: <Fields><Field_SuppressChapterBreak> 0

        self.srtScenes = []
        # list of str
        # xml: <Scenes><ScID>
        # The chapter's scene IDs. The order of its elements
        # corresponds to the chapter's order of the scenes.

        self.kwVar = {}
        # dictionary
        # Optional key/value instance variables for customization.
import re


class Scene:
    """yWriter scene representation.
    
    Public instance variables:
        title -- str: scene title.
        desc -- str: scene description in a single string.
        sceneContent -- str: scene content (property with getter and setter).
        rtfFile -- str: RTF file name (yWriter 5).
        wordCount - int: word count (derived; updated by the sceneContent setter).
        letterCount - int: letter count (derived; updated by the sceneContent setter).
        isUnused -- bool: True if the scene is marked "Unused". 
        isNotesScene -- bool: True if the scene type is "Notes".
        isTodoScene -- bool: True if the scene type is "Todo". 
        doNotExport -- bool: True if the scene is not to be exported to RTF.
        status -- int: scene status (Outline/Draft/1st Edit/2nd Edit/Done).
        sceneNotes -- str: scene notes in a single string.
        tags -- list of scene tags. 
        field1 -- int: scene ratings field 1.
        field2 -- int: scene ratings field 2.
        field3 -- int: scene ratings field 3.
        field4 -- int: scene ratings field 4.
        appendToPrev -- bool: if True, append the scene without a divider to the previous scene.
        isReactionScene -- bool: if True, the scene is "reaction". Otherwise, it's "action". 
        isSubPlot -- bool: if True, the scene belongs to a sub-plot. Otherwise it's main plot.  
        goal -- str: the main actor's scene goal. 
        conflict -- str: what hinders the main actor to achieve his goal.
        outcome -- str: what comes out at the end of the scene.
        characters -- list of character IDs related to this scene.
        locations -- list of location IDs related to this scene. 
        items -- list of item IDs related to this scene.
        date -- str: specific start date in ISO format (yyyy-mm-dd).
        time -- str: specific start time in ISO format (hh:mm).
        minute -- str: unspecific start time: minutes.
        hour -- str: unspecific start time: hour.
        day -- str: unspecific start time: day.
        lastsMinutes -- str: scene duration: minutes.
        lastsHours -- str: scene duration: hours.
        lastsDays -- str: scene duration: days. 
        image -- str:  path to an image related to the scene. 
    """
    STATUS = (None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done')
    # Emulate an enumeration for the scene status
    # Since the items are used to replace text,
    # they may contain spaces. This is why Enum cannot be used here.

    ACTION_MARKER = 'A'
    REACTION_MARKER = 'R'
    NULL_DATE = '0001-01-01'
    NULL_TIME = '00:00:00'

    def __init__(self):
        """Initialize instance variables."""
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self._sceneContent = None
        # str
        # xml: <SceneContent>
        # Scene text with yW7 raw markup.

        self.rtfFile = None
        # str
        # xml: <RTFFile>
        # Name of the file containing the scene in yWriter 5.

        self.wordCount = 0
        # int # xml: <WordCount>
        # To be updated by the sceneContent setter

        self.letterCount = 0
        # int
        # xml: <LetterCount>
        # To be updated by the sceneContent setter

        self.isUnused = None
        # bool
        # xml: <Unused> -1

        self.isNotesScene = None
        # bool
        # xml: <Fields><Field_SceneType> 1

        self.isTodoScene = None
        # bool
        # xml: <Fields><Field_SceneType> 2

        self.doNotExport = None
        # bool
        # xml: <ExportCondSpecific><ExportWhenRTF>

        self.status = None
        # int
        # xml: <Status>
        # 1 - Outline
        # 2 - Draft
        # 3 - 1st Edit
        # 4 - 2nd Edit
        # 5 - Done
        # See also the STATUS list for conversion.

        self.sceneNotes = None
        # str
        # xml: <Notes>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.field1 = None
        # str
        # xml: <Field1>

        self.field2 = None
        # str
        # xml: <Field2>

        self.field3 = None
        # str
        # xml: <Field3>

        self.field4 = None
        # str
        # xml: <Field4>

        self.appendToPrev = None
        # bool
        # xml: <AppendToPrev> -1

        self.isReactionScene = None
        # bool
        # xml: <ReactionScene> -1

        self.isSubPlot = None
        # bool
        # xml: <SubPlot> -1

        self.goal = None
        # str
        # xml: <Goal>

        self.conflict = None
        # str
        # xml: <Conflict>

        self.outcome = None
        # str
        # xml: <Outcome>

        self.characters = None
        # list of str
        # xml: <Characters><CharID>

        self.locations = None
        # list of str
        # xml: <Locations><LocID>

        self.items = None
        # list of str
        # xml: <Items><ItemID>

        self.date = None
        # str
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.time = None
        # str
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.minute = None
        # str
        # xml: <Minute>

        self.hour = None
        # str
        # xml: <Hour>

        self.day = None
        # str
        # xml: <Day>

        self.lastsMinutes = None
        # str
        # xml: <LastsMinutes>

        self.lastsHours = None
        # str
        # xml: <LastsHours>

        self.lastsDays = None
        # str
        # xml: <LastsDays>

        self.image = None
        # str
        # xml: <ImageFile>

        self.kwVar = {}
        # dictionary
        # Optional key/value instance variables for customization.

    @property
    def sceneContent(self):
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text):
        """Set sceneContent updating word count and letter count."""
        self._sceneContent = text
        text = re.sub('--|—|–|…', ' ', text)
        # Make dashes separate words
        text = re.sub('\[.+?\]|\/\*.+?\*\/|\.|\,|-', '', text)
        # Remove comments and yWriter raw markup for word count; make hyphens join words
        wordList = text.split()
        self.wordCount = len(wordList)
        text = re.sub('\[.+?\]|\/\*.+?\*\/', '', self._sceneContent)
        # Remove yWriter raw markup for letter count
        text = text.replace('\n', '')
        text = text.replace('\r', '')
        self.letterCount = len(text)


class WorldElement:
    """Story world element representation (may be location or item).
    
    Public instance variables:
        title -- str: title (name).
        image -- str: image file path.
        desc -- str: description.
        tags -- list of tags.
        aka -- str: alternate name.
    """

    def __init__(self):
        """Initialize instance variables."""
        self.title = None
        # str
        # xml: <Title>

        self.image = None
        # str
        # xml: <ImageFile>

        self.desc = None
        # str
        # xml: <Desc>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.aka = None
        # str
        # xml: <AKA>

        self.kwVar = {}
        # dictionary
        # Optional key/value instance variables for customization.


class Character(WorldElement):
    """yWriter character representation.

    Public instance variables:
        notes -- str: character notes.
        bio -- str: character biography.
        goals -- str: character's goals in the story.
        fullName -- str: full name (the title inherited may be a short name).
        isMajor -- bool: True, if it's a major character.
    """
    MAJOR_MARKER = 'Major'
    MINOR_MARKER = 'Minor'

    def __init__(self):
        """Extends the superclass constructor by adding instance variables."""
        super().__init__()

        self.notes = None
        # str
        # xml: <Notes>

        self.bio = None
        # str
        # xml: <Bio>

        self.goals = None
        # str
        # xml: <Goals>

        self.fullName = None
        # str
        # xml: <FullName>

        self.isMajor = None
        # bool
        # xml: <Major>


class Novel:
    """Abstract yWriter project file representation.

    This class represents a file containing a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).

    Public methods:
        read() -- parse the file and get the instance variables.
        merge(source) -- update instance variables from a source instance.
        write() -- write instance variables to the file.

    Public instance variables:
        title -- str: title.
        desc -- str: description in a single string.
        authorName -- str: author's name.
        author bio -- str: information about the author.
        fieldTitle1 -- str: scene rating field title 1.
        fieldTitle2 -- str: scene rating field title 2.
        fieldTitle3 -- str: scene rating field title 3.
        fieldTitle4 -- str: scene rating field title 4.
        chapters -- dict: (key: ID; value: chapter instance).
        scenes -- dict: (key: ID, value: scene instance).
        srtChapters -- list: the novel's sorted chapter IDs.
        locations -- dict: (key: ID, value: WorldElement instance).
        srtLocations -- list: the novel's sorted location IDs.
        items -- dict: (key: ID, value: WorldElement instance).
        srtItems -- list: the novel's sorted item IDs.
        characters -- dict: (key: ID, value: character instance).
        srtCharacters -- list: the novel's sorted character IDs.
        projectName -- str: URL-coded file name without suffix and extension. 
        projectPath -- str: URL-coded path to the project directory. 
        filePath -- str: path to the file (property with getter and setter). 
    """
    DESCRIPTION = _('Novel')
    EXTENSION = None
    SUFFIX = None
    # To be extended by subclass methods.

    CHAPTER_CLASS = Chapter
    SCENE_CLASS = Scene
    CHARACTER_CLASS = Character
    WE_CLASS = WorldElement

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            
        """
        self.title = None
        # str
        # xml: <PROJECT><Title>

        self.desc = None
        # str
        # xml: <PROJECT><Desc>

        self.authorName = None
        # str
        # xml: <PROJECT><AuthorName>

        self.authorBio = None
        # str
        # xml: <PROJECT><Bio>

        self.fieldTitle1 = None
        # str
        # xml: <PROJECT><FieldTitle1>

        self.fieldTitle2 = None
        # str
        # xml: <PROJECT><FieldTitle2>

        self.fieldTitle3 = None
        # str
        # xml: <PROJECT><FieldTitle3>

        self.fieldTitle4 = None
        # str
        # xml: <PROJECT><FieldTitle4>

        self.chapters = {}
        # dict
        # xml: <CHAPTERS><CHAPTER><ID>
        # key = chapter ID, value = Chapter instance.
        # The order of the elements does not matter (the novel's order of the chapters is defined by srtChapters)

        self.scenes = {}
        # dict
        # xml: <SCENES><SCENE><ID>
        # key = scene ID, value = Scene instance.
        # The order of the elements does not matter (the novel's order of the scenes is defined by
        # the order of the chapters and the order of the scenes within the chapters)

        self.srtChapters = []
        # list of str
        # The novel's chapter IDs. The order of its elements corresponds to the novel's order of the chapters.

        self.locations = {}
        # dict
        # xml: <LOCATIONS>
        # key = location ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtLocations = []
        # list of str
        # The novel's location IDs. The order of its elements
        # corresponds to the XML project file.

        self.items = {}
        # dict
        # xml: <ITEMS>
        # key = item ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtItems = []
        # list of str
        # The novel's item IDs. The order of its elements corresponds to the XML project file.

        self.characters = {}
        # dict
        # xml: <CHARACTERS>
        # key = character ID, value = Character instance.
        # The order of the elements does not matter.

        self.srtCharacters = []
        # list of str
        # The novel's character IDs. The order of its elements corresponds to the XML project file.

        self._filePath = None
        # str
        # Path to the file. The setter only accepts files of a supported type as specified by EXTENSION.

        self.projectName = None
        # str
        # URL-coded file name without suffix and extension.

        self.projectPath = None
        # str
        # URL-coded path to the project directory.

        self.filePath = filePath

        self.kwVar = {}
        # dictionary
        # Optional key/value instance variables for customization.

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        """Setter for the filePath instance variable.
                
        - Format the path string according to Python's requirements. 
        - Accept only filenames with the right suffix and extension.
        """
        if self.SUFFIX is not None:
            suffix = self.SUFFIX
        else:
            suffix = ''
        if filePath.lower().endswith(f'{suffix}{self.EXTENSION}'.lower()):
            self._filePath = filePath
            head, tail = os.path.split(os.path.realpath(filePath))
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(f'{suffix}{self.EXTENSION}', ''))

    def read(self):
        """Parse the file and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a stub to be overridden by subclass methods.
        """
        return f'{ERROR}Read method is not implemented.'

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Novel subclass instance to merge.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a stub to be overridden by subclass methods.
        """
        return f'{ERROR}Merge method is not implemented.'

    def write(self):
        """Write instance variables to the file.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a stub to be overridden by subclass methods.
        """
        return f'{ERROR}Write method is not implemented.'

    def _convert_to_yw(self, text):
        """Return text, converted from source format to yw7 markup.
        
        Positional arguments:
            text -- string to convert.
        
        This is a stub to be overridden by subclass methods.
        """
        return text.rstrip()

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        This is a stub to be overridden by subclass methods.
        """
        return text.rstrip()
import zipfile
import codecs
import json


def open_timeline(filePath):
    """Unzip the project file and read 'timeline.json'.

    Positional arguments:
        filePath -- Path of the .aeon project file to read.
        
    Return a message beginning with the ERROR constant in case of error
    and a Python object containing the timeline structure.
    """
    try:
        with zipfile.ZipFile(filePath, 'r') as myzip:
            jsonBytes = myzip.read('timeline.json')
            jsonStr = codecs.decode(jsonBytes, encoding='utf-8')
    except:
        return f'{ERROR}Cannot read timeline data.', None
    if not jsonStr:
        return f'{ERROR}No JSON part found in timeline data.', None
    try:
        jsonData = json.loads(jsonStr)
    except('JSONDecodeError'):
        return f'{ERROR}Invalid JSON data in timeline.'
        None
    return 'Timeline data read in.', jsonData


def save_timeline(jsonData, filePath):
    """Write the timeline to a zipfile located at filePath.
    
    Positional arguments:
        jsonData -- Python object containing the timeline structure.
        filePath -- Path of the .aeon project file to write.
        
    Return a message beginning with the ERROR constant in case of error.
    """
    if os.path.isfile(filePath):
        os.replace(filePath, f'{filePath}.bak')
        backedUp = True
    else:
        backedUp = False
    try:
        with zipfile.ZipFile(filePath, 'w', compression=zipfile.ZIP_DEFLATED) as f:
            f.writestr('timeline.json', json.dumps(jsonData))
    except:
        if backedUp:
            os.replace(f'{filePath}.bak', filePath)
        return f'{ERROR}Cannot write "{os.path.normpath(filePath)}".'

    return f'"{os.path.normpath(filePath)}" written.'
from hashlib import pbkdf2_hmac

guidChars = list('ABCDEF0123456789')


def get_sub_guid(key, size):
    """Return a string generated from a bytes key.
    
    Positional arguments:
        key -- bytes: key.
        size -- length of the returned string.
    """
    keyInt = int.from_bytes(key, byteorder='big')
    guid = ''
    while len(guid) < size and keyInt > 0:
        guid += guidChars[keyInt % len(guidChars)]
        keyInt //= len(guidChars)
    return guid


def get_uid(text):
    """Return a GUID for Aeon Timeline.
    
    Positional arguments:
        text -- string to generate a GUID from.

    GUID format: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
    """
    text = text.encode('utf-8')
    sizes = [8, 4, 4, 4, 12]
    salts = [b'a', b'b', b'c', b'd', b'e']
    guid = []
    for i in range(5):
        key = pbkdf2_hmac('sha1', text, salts[i], 1)
        guid.append(get_sub_guid(key, sizes[i]))
    return '-'.join(guid)
import math


def get_moon_phase(dateStr):
    """Return a single value - the phase day (0 to 29, where 0=new moon, 15=full etc.) 
    for the selected date.
    Date format is 'yyyy-mm-dd'.
    This is based on a 'do it in your head' algorithm by John Conway. 
    In its current form, it's only valid for the 20th and 21st centuries.
    See: http://www.ben-daglish.net/moon.shtml
    """
    try:
        y, m, d = dateStr.split('-')
        year = int(y)
        month = int(m)
        day = int(d)
        r = year % 100
        r %= 19
        if r > 9:
            r -= 19
        r = ((r * 11) % 30) + month + day
        if month < 3:
            r += 2
        if year < 2000:
            r -= 4
        else:
            r -= 8.3
        r = math.floor(r + 0.5) % 30
        if r < 0:
            r += 30
    except:
        r = None
    return r


def get_moon_phase_plus(dateStr):
    """Return a string containing the moon phase plus a pseudo-graphic display.
    """
    s = '  ))))))))))))OOO(((((((((((( '
    p = '00¼¼¼¼½½½½¾¾¾¾111¾¾¾¾½½½½¼¼¼¼0'
    r = get_moon_phase(dateStr)
    if r is not None:
        result = f'{r} [  {s[r]}  ] {p[r]}'
    else:
        result = ''
    return result




class JsonTimeline2(Novel):
    """File representation of an Aeon Timeline 2 project. 

    Public methods:
        read() -- parse the file and get the instance variables.
        merge(source) -- update instance variables from a source instance.
        write() -- write instance variables to the file.

    Represents the .aeonzip file containing 'timeline.json'.
    """
    EXTENSION = '.aeonzip'
    DESCRIPTION = 'Aeon Timeline 2 project'
    SUFFIX = ''
    VALUE_YES = '1'
    # JSON representation of "yes" in Aeon2 "yes/no" properties
    DATE_LIMIT = (datetime(100, 1, 1) - datetime.min).total_seconds()
    # Dates before 100-01-01 can not be displayed properly in yWriter
    DEFAULT_TIMESTAMP = (datetime.today() - datetime.min).total_seconds()
    PROPERTY_MOONPHASE = 'Moon phase'

    _SCN_KWVAR = (
        'Field_SceneArcs',
        )

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Required keyword arguments:
            narrative_arc -- str: name of the user-defined "Narrative" arc.
            property_description -- str: name of the user-defined scene description property.
            property_notes -- str: name of the user-defined scene notes property.
            role_location -- str: name of the user-defined role for scene locations.
            role_item -- str: name of the user-defined role for items in a scene.
            role_character -- str: name of the user-defined role for characters in a scene.
            type_character -- str: name of the user-defined "Character" type.
            type_location -- str: name of the user-defined "Location" type.
            type_item -- str: name of the user-defined "Item" type.
            scenes_only -- bool: synchronize only "Normal" scenes.
            color_scene -- str: color of new scene events.
            color_event -- str: color of new non-scene events.
            add_moonphase -- bool: add a moon phase property to each event.
        
        If scenes_only is True: synchronize only "Normal" scenes.
        If scenes_only is False: synchronize "Notes" scenes as well.            
        Extends the superclass constructor.
        """
        super().__init__(filePath, **kwargs)
        self._jsonData = None

        # JSON[entities][name]
        self._entityNarrative = kwargs['narrative_arc']

        # JSON[template][properties][name]
        self._propertyDesc = kwargs['property_description']
        self._propertyNotes = kwargs['property_notes']

        # JSON[template][types][name][roles]
        self._roleLocation = kwargs['role_location']
        self._roleItem = kwargs['role_item']
        self._roleCharacter = kwargs['role_character']

        # JSON[template][types][name]
        self._typeCharacter = kwargs['type_character']
        self._typeLocation = kwargs['type_location']
        self._typeItem = kwargs['type_item']

        # GUIDs
        self._tplDateGuid = None
        self._typeArcGuid = None
        self._typeCharacterGuid = None
        self._typeLocationGuid = None
        self._typeItemGuid = None
        self._roleArcGuid = None
        self._roleStorylineGuid = None
        self._roleCharacterGuid = None
        self._roleLocationGuid = None
        self._roleItemGuid = None
        self._entityNarrativeGuid = None
        self._propertyDescGuid = None
        self._propertyNotesGuid = None
        self._propertyMoonphaseGuid = None

        # Miscellaneous
        self._scenesOnly = kwargs['scenes_only']
        self._addMoonphase = kwargs['add_moonphase']
        self._sceneColor = kwargs['color_scene']
        self._eventColor = kwargs['color_event']
        self._timestampMax = 0
        self._displayIdMax = 0.0
        self._colors = {}
        self._arcCount = 0
        self._characterGuidById = {}
        self._locationGuidById = {}
        self._itemGuidById = {}
        self._trashEvents = []
        self._arcGuidsByName = {}

    def read(self):
        """Parse the file and get the instance variables.
        
        Read the JSON part of the Aeon Timeline 2 file located at filePath, 
        and build a yWriter novel structure.
        - Events marked as scenes are converted to scenes in one single chapter.
        - Other events are converted to “Notes” scenes in another chapter.
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
        message, self._jsonData = open_timeline(self.filePath)
        if message.startswith(ERROR):
            return message

        #--- Get the color definitions.
        for tplCol in self._jsonData['template']['colors']:
            self._colors[tplCol['name']] = tplCol['guid']

        #--- Get the date definition.
        for tplRgp in self._jsonData['template']['rangeProperties']:
            if tplRgp['type'] == 'date':
                for tplRgpCalEra in tplRgp['calendar']['eras']:
                    if tplRgpCalEra['name'] == 'AD':
                        self._tplDateGuid = tplRgp['guid']
                        break

        if self._tplDateGuid is None:
            return f'{ERROR}"AD" era is missing in the calendar.'

        #--- Get GUID of user defined types and roles.
        for tplTyp in self._jsonData['template']['types']:
            if tplTyp['name'] == 'Arc':
                self._typeArcGuid = tplTyp['guid']
                for tplTypRol in tplTyp['roles']:
                    if tplTypRol['name'] == 'Arc':
                        self._roleArcGuid = tplTypRol['guid']
                    elif tplTypRol['name'] == 'Storyline':
                        self._roleStorylineGuid = tplTypRol['guid']
            elif tplTyp['name'] == self._typeCharacter:
                self._typeCharacterGuid = tplTyp['guid']
                for tplTypRol in tplTyp['roles']:
                    if tplTypRol['name'] == self._roleCharacter:
                        self._roleCharacterGuid = tplTypRol['guid']
            elif tplTyp['name'] == self._typeLocation:
                self._typeLocationGuid = tplTyp['guid']
                for tplTypRol in tplTyp['roles']:
                    if tplTypRol['name'] == self._roleLocation:
                        self._roleLocationGuid = tplTypRol['guid']
                        break

            elif tplTyp['name'] == self._typeItem:
                self._typeItemGuid = tplTyp['guid']
                for tplTypRol in tplTyp['roles']:
                    if tplTypRol['name'] == self._roleItem:
                        self._roleItemGuid = tplTypRol['guid']
                        break

        #--- Add "Arc" type, if missing.
        if self._typeArcGuid is None:
            self._typeArcGuid = get_uid('typeArcGuid')
            typeCount = len(self._jsonData['template']['types'])
            self._jsonData['template']['types'].append(
                {
                    'color': 'iconYellow',
                    'guid': self._typeArcGuid,
                    'icon': 'book',
                    'name': 'Arc',
                    'persistent': True,
                    'roles': [],
                    'sortOrder': typeCount
                })
        for entityType in self._jsonData['template']['types']:
            if entityType['name'] == 'Arc':
                if self._roleArcGuid is None:
                    self._roleArcGuid = get_uid('_roleArcGuid')
                    entityType['roles'].append(
                        {
                        'allowsMultipleForEntity': True,
                        'allowsMultipleForEvent': True,
                        'allowsPercentAllocated': False,
                        'guid': self._roleArcGuid,
                        'icon': 'circle text',
                        'mandatoryForEntity': False,
                        'mandatoryForEvent': False,
                        'name': 'Arc',
                        'sortOrder': 0
                        })
                if self._roleStorylineGuid is None:
                    self._roleStorylineGuid = get_uid('_roleStorylineGuid')
                    entityType['roles'].append(
                        {
                        'allowsMultipleForEntity': True,
                        'allowsMultipleForEvent': True,
                        'allowsPercentAllocated': False,
                        'guid': self._roleStorylineGuid,
                        'icon': 'circle filled text',
                        'mandatoryForEntity': False,
                        'mandatoryForEvent': False,
                        'name': 'Storyline',
                        'sortOrder': 0
                        })

        #--- Add "Character" type, if missing.
        if self._typeCharacterGuid is None:
            self._typeCharacterGuid = get_uid('_typeCharacterGuid')
            self._roleCharacterGuid = get_uid('_roleCharacterGuid')
            typeCount = len(self._jsonData['template']['types'])
            self._jsonData['template']['types'].append(
                {
                    'color': 'iconRed',
                    'guid': self._typeCharacterGuid,
                    'icon': 'person',
                    'name': self._typeCharacter,
                    'persistent': False,
                    'roles': [
                        {
                            'allowsMultipleForEntity': True,
                            'allowsMultipleForEvent': True,
                            'allowsPercentAllocated': False,
                            'guid': self._roleCharacterGuid,
                            'icon': 'circle text',
                            'mandatoryForEntity': False,
                            'mandatoryForEvent': False,
                            'name': self._roleCharacter,
                            'sortOrder': 0
                        }
                    ],
                    'sortOrder': typeCount
                })

        #--- Add "Location" type, if missing.
        if self._typeLocationGuid is None:
            self._typeLocationGuid = get_uid('_typeLocationGuid')
            self._roleLocationGuid = get_uid('_roleLocationGuid')
            typeCount = len(self._jsonData['template']['types'])
            self._jsonData['template']['types'].append(
                {
                    'color': 'iconOrange',
                    'guid': self._typeLocationGuid,
                    'icon': 'map',
                    'name': self._typeLocation,
                    'persistent': True,
                    'roles': [
                        {
                            'allowsMultipleForEntity': True,
                            'allowsMultipleForEvent': True,
                            'allowsPercentAllocated': False,
                            'guid': self._roleLocationGuid,
                            'icon': 'circle text',
                            'mandatoryForEntity': False,
                            'mandatoryForEvent': False,
                            'name': self._roleLocation,
                            'sortOrder': 0
                        }
                    ],
                    'sortOrder': typeCount
                })

        #--- Add "Item" type, if missing.
        if self._typeItemGuid is None:
            self._typeItemGuid = get_uid('_typeItemGuid')
            self._roleItemGuid = get_uid('_roleItemGuid')
            typeCount = len(self._jsonData['template']['types'])
            self._jsonData['template']['types'].append(
                {
                    'color': 'iconPurple',
                    'guid': self._typeItemGuid,
                    'icon': 'cube',
                    'name': self._typeItem,
                    'persistent': True,
                    'roles': [
                        {
                            'allowsMultipleForEntity': True,
                            'allowsMultipleForEvent': True,
                            'allowsPercentAllocated': False,
                            'guid': self._roleItemGuid,
                            'icon': 'circle text',
                            'mandatoryForEntity': False,
                            'mandatoryForEvent': False,
                            'name': self._roleItem,
                            'sortOrder': 0
                        }
                    ],
                    'sortOrder': typeCount
                })

        #--- Get arcs, characters, locations, and items.
        crIdsByGuid = {}
        lcIdsByGuid = {}
        itIdsByGuid = {}
        characterCount = 0
        locationCount = 0
        itemCount = 0
        for ent in self._jsonData['entities']:
            if ent['entityType'] == self._typeArcGuid:
                self._arcCount += 1
                if ent['name'] == self._entityNarrative:
                    self._entityNarrativeGuid = ent['guid']
                else:
                    self._arcGuidsByName[ent['name']] = ent['guid']
            elif ent['entityType'] == self._typeCharacterGuid:
                characterCount += 1
                crId = str(characterCount)
                crIdsByGuid[ent['guid']] = crId
                self.characters[crId] = self.CHARACTER_CLASS()
                self.characters[crId].title = ent['name']
                self.characters[crId].title = ent['name']
                self._characterGuidById[crId] = ent['guid']
                if ent['notes']:
                    self.characters[crId].notes = ent['notes']
                else:
                    ent['notes'] = ''
                self.srtCharacters.append(crId)
            elif ent['entityType'] == self._typeLocationGuid:
                locationCount += 1
                lcId = str(locationCount)
                lcIdsByGuid[ent['guid']] = lcId
                self.locations[lcId] = self.WE_CLASS()
                self.locations[lcId].title = ent['name']
                self.srtLocations.append(lcId)
                self._locationGuidById[lcId] = ent['guid']
            elif ent['entityType'] == self._typeItemGuid:
                itemCount += 1
                itId = str(itemCount)
                itIdsByGuid[ent['guid']] = itId
                self.items[itId] = self.WE_CLASS()
                self.items[itId].title = ent['name']
                self.srtItems.append(itId)
                self._itemGuidById[itId] = ent['guid']

        #--- Get GUID of user defined properties.
        hasPropertyNotes = False
        hasPropertyDesc = False
        for tplPrp in self._jsonData['template']['properties']:
            if tplPrp['name'] == self._propertyDesc:
                self._propertyDescGuid = tplPrp['guid']
                hasPropertyDesc = True
            elif tplPrp['name'] == self._propertyNotes:
                self._propertyNotesGuid = tplPrp['guid']
                hasPropertyNotes = True
            elif tplPrp['name'] == self.PROPERTY_MOONPHASE:
                self._propertyMoonphaseGuid = tplPrp['guid']

        #--- Create user defined properties, if missing.
        if not hasPropertyNotes:
            for tplPrp in self._jsonData['template']['properties']:
                tplPrp['sortOrder'] += 1
            self._propertyNotesGuid = get_uid('_propertyNotesGuid')
            self._jsonData['template']['properties'].insert(0, {
                'calcMode': 'default',
                'calculate': False,
                'fadeEvents': False,
                'guid': self._propertyNotesGuid,
                'icon': 'tag',
                'isMandatory': False,
                'name': self._propertyNotes,
                'sortOrder': 0,
                'type': 'multitext'
            })
        if not hasPropertyDesc:
            n = len(self._jsonData['template']['properties'])
            self._propertyDescGuid = get_uid('_propertyDescGuid')
            self._jsonData['template']['properties'].append({
                'calcMode': 'default',
                'calculate': False,
                'fadeEvents': False,
                'guid': self._propertyDescGuid,
                'icon': 'tag',
                'isMandatory': False,
                'name': self._propertyDesc,
                'sortOrder': n,
                'type': 'multitext'
            })
        if self._addMoonphase and self._propertyMoonphaseGuid is None:
            n = len(self._jsonData['template']['properties'])
            self._propertyMoonphaseGuid = get_uid('_propertyMoonphaseGuid')
            self._jsonData['template']['properties'].append({
                'calcMode': 'default',
                'calculate': False,
                'fadeEvents': False,
                'guid': self._propertyMoonphaseGuid,
                'icon': 'flag',
                'isMandatory': False,
                'name': self.PROPERTY_MOONPHASE,
                'sortOrder': n,
                'type': 'text'
            })

        #--- Get scenes.
        eventCount = 0
        scIdsByDate = {}
        scnTitles = []
        for evt in self._jsonData['events']:
            if evt['title'] in scnTitles:
                return f'{ERROR}Ambiguous Aeon event title "{evt["title"]}".'
            scnTitles.append(evt['title'])
            eventCount += 1
            scId = str(eventCount)
            self.scenes[scId] = self.SCENE_CLASS()
            self.scenes[scId].title = evt['title']
            displayId = float(evt['displayId'])
            if displayId > self._displayIdMax:
                self._displayIdMax = displayId
            self.scenes[scId].status = 1
            # Set scene status = "Outline".
            scnArcs = []

            #--- Initialize custom keyword variables.
            for fieldName in self._SCN_KWVAR:
                self.scenes[scId].kwVar[fieldName] = None

            #--- Evaluate properties.
            hasDescription = False
            hasNotes = False
            for evtVal in evt['values']:

                # Get scene description.
                if evtVal['property'] == self._propertyDescGuid:
                    hasDescription = True
                    if evtVal['value']:
                        self.scenes[scId].desc = evtVal['value']

                # Get scene notes.
                elif evtVal['property'] == self._propertyNotesGuid:
                    hasNotes = True
                    if evtVal['value']:
                        self.scenes[scId].sceneNotes = evtVal['value']

            #--- Add description and scene notes, if missing.
            if not hasDescription:
                evt['values'].append({'property': self._propertyDescGuid, 'value': ''})
            if not hasNotes:
                evt['values'].append({'property': self._propertyNotesGuid, 'value': ''})

            #--- Get scene tags.
            if evt['tags']:
                if self.scenes[scId].tags is None:
                    self.scenes[scId].tags = []
                for evtTag in evt['tags']:
                    self.scenes[scId].tags.append(evtTag)

            #--- Get date/time/duration
            timestamp = 0
            for evtRgv in evt['rangeValues']:
                if evtRgv['rangeProperty'] == self._tplDateGuid:
                    timestamp = evtRgv['position']['timestamp']
                    if timestamp >= self.DATE_LIMIT:
                        # Restrict date/time calculation to dates within yWriter's range
                        sceneStart = datetime.min + timedelta(seconds=timestamp)
                        startDateTime = sceneStart.isoformat().split('T')
                        self.scenes[scId].date = startDateTime[0]
                        self.scenes[scId].time = startDateTime[1]

                        # Calculate duration
                        if 'years' in evtRgv['span'] or 'months' in evtRgv['span']:
                            endYear = sceneStart.year
                            endMonth = sceneStart.month
                            if 'years' in evtRgv['span']:
                                endYear += evtRgv['span']['years']
                            if 'months' in evtRgv['span']:
                                endMonth += evtRgv['span']['months']
                                while endMonth > 12:
                                    endMonth -= 12
                                    endYear += 1
                            sceneEnd = datetime(endYear, endMonth, sceneStart.day)
                            sceneDuration = sceneEnd - datetime(sceneStart.year, sceneStart.month, sceneStart.day)
                            lastsDays = sceneDuration.days
                            lastsHours = sceneDuration.seconds // 3600
                            lastsMinutes = (sceneDuration.seconds % 3600) // 60
                        else:
                            lastsDays = 0
                            lastsHours = 0
                            lastsMinutes = 0
                        if 'weeks' in evtRgv['span']:
                            lastsDays += evtRgv['span']['weeks'] * 7
                        if 'days' in evtRgv['span']:
                            lastsDays += evtRgv['span']['days']
                        if 'hours' in evtRgv['span']:
                            lastsDays += evtRgv['span']['hours'] // 24
                            lastsHours += evtRgv['span']['hours'] % 24
                        if 'minutes' in evtRgv['span']:
                            lastsHours += evtRgv['span']['minutes'] // 60
                            lastsMinutes += evtRgv['span']['minutes'] % 60
                        if 'seconds' in evtRgv['span']:
                            lastsMinutes += evtRgv['span']['seconds'] // 60
                        lastsHours += lastsMinutes // 60
                        lastsMinutes %= 60
                        lastsDays += lastsHours // 24
                        lastsHours %= 24
                        self.scenes[scId].lastsDays = str(lastsDays)
                        self.scenes[scId].lastsHours = str(lastsHours)
                        self.scenes[scId].lastsMinutes = str(lastsMinutes)
                    break

            # Use the timestamp for chronological sorting.
            if not timestamp in scIdsByDate:
                scIdsByDate[timestamp] = []
            scIdsByDate[timestamp].append(scId)

            #--- Find scenes and get characters, locations, and items.
            self.scenes[scId].isNotesScene = True
            self.scenes[scId].isUnused = True
            for evtRel in evt['relationships']:
                if evtRel['role'] == self._roleArcGuid:
                    # Make scene event "Normal" type scene.
                    if self._entityNarrativeGuid and evtRel['entity'] == self._entityNarrativeGuid:
                        self.scenes[scId].isNotesScene = False
                        self.scenes[scId].isUnused = False
                        if timestamp > self._timestampMax:
                            self._timestampMax = timestamp
                if evtRel['role'] == self._roleStorylineGuid:
                    # Collect scene arcs.
                    for arcName in self._arcGuidsByName:
                        if evtRel['entity'] == self._arcGuidsByName[arcName]:
                            scnArcs.append(arcName)
                elif evtRel['role'] == self._roleCharacterGuid:
                    if self.scenes[scId].characters is None:
                        self.scenes[scId].characters = []
                    crId = crIdsByGuid[evtRel['entity']]
                    self.scenes[scId].characters.append(crId)
                elif evtRel['role'] == self._roleLocationGuid:
                    if self.scenes[scId].locations is None:
                        self.scenes[scId].locations = []
                    lcId = lcIdsByGuid[evtRel['entity']]
                    self.scenes[scId].locations.append(lcId)
                elif evtRel['role'] == self._roleItemGuid:
                    if self.scenes[scId].items is None:
                        self.scenes[scId].items = []
                    itId = itIdsByGuid[evtRel['entity']]
                    self.scenes[scId].items.append(itId)

            # Add arcs to the scene keyword variables.
            self.scenes[scId].kwVar['Field_SceneArcs'] = ';'.join(scnArcs)

        #--- Sort scenes by date/time and place them in chapters.
        chIdNarrative = '1'
        chIdBackground = '2'
        self.chapters[chIdNarrative] = self.CHAPTER_CLASS()
        self.chapters[chIdNarrative].title = 'Chapter 1'
        self.chapters[chIdNarrative].chType = 0
        self.srtChapters.append(chIdNarrative)
        self.chapters[chIdBackground] = self.CHAPTER_CLASS()
        self.chapters[chIdBackground].title = 'Background'
        self.chapters[chIdBackground].chType = 1
        self.srtChapters.append(chIdBackground)
        srtScenes = sorted(scIdsByDate.items())
        for __, scList in srtScenes:
            for scId in scList:
                if self.scenes[scId].isNotesScene:
                    self.chapters[chIdBackground].srtScenes.append(scId)
                else:
                    self.chapters[chIdNarrative].srtScenes.append(scId)
        if self._timestampMax == 0:
            self._timestampMax = self.DEFAULT_TIMESTAMP
        return 'Timeline data converted to novel structure.'

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Novel subclass instance to merge.
               
        Update date/time/duration from the source,
        if the scene title matches.
        Overrides the superclass method.
        """

        def get_display_id():
            self._displayIdMax += 1
            return str(int(self._displayIdMax))

        def build_event(scene):
            """Create a new event from a scene.
            """
            event = {
                'attachments': [],
                'color': '',
                'displayId': get_display_id(),
                'guid': get_uid(f'scene{scene.title}'),
                'links': [],
                'locked': False,
                'priority': 500,
                'rangeValues': [{
                    'minimumZoom':-1,
                    'position': {
                        'precision': 'minute',
                        'timestamp': self.DATE_LIMIT
                    },
                    'rangeProperty': self._tplDateGuid,
                    'span': {},
                }],
                'relationships': [],
                'tags': [],
                'title': scene.title,
                'values': [{
                    'property': self._propertyNotesGuid,
                    'value': ''
                },
                    {
                    'property': self._propertyDescGuid,
                    'value': ''
                }],
            }
            if scene.isNotesScene:
                event['color'] = self._colors[self._eventColor]
            else:
                event['color'] = self._colors[self._sceneColor]
            return event

        message = self.read()
        if message.startswith(ERROR):
            return message

        linkedCharacters = []
        linkedLocations = []
        linkedItems = []

        #--- Check the source for ambiguous titles.
        # Check scenes.
        srcScnTitles = []
        for chId in source.chapters:
            if source.chapters[chId].isTrash:
                continue

            for scId in source.chapters[chId].srtScenes:
                if source.scenes[scId].title in srcScnTitles:
                    return f'{ERROR}Ambiguous yWriter scene title "{source.scenes[scId].title}".'

                srcScnTitles.append(source.scenes[scId].title)

                #--- Collect characters, locations, and items assigned to scenes.
                if source.scenes[scId].characters:
                    linkedCharacters = list(set(linkedCharacters + source.scenes[scId].characters))
                if source.scenes[scId].locations:
                    linkedLocations = list(set(linkedLocations + source.scenes[scId].locations))
                if source.scenes[scId].items:
                    linkedItems = list(set(linkedItems + source.scenes[scId].items))

                #--- Collect arcs from source.
                try:
                    arcs = source.scenes[scId].kwVar['Field_SceneArcs'].split(';')
                    for arc in arcs:
                        if not arc in self._arcGuidsByName:
                            self._arcGuidsByName[arc] = None
                except:
                    pass

        # Check characters.
        srcChrNames = []
        for crId in source.characters:
            if not crId in linkedCharacters:
                continue

            if source.characters[crId].title in srcChrNames:
                return f'{ERROR}Ambiguous yWriter character "{source.characters[crId].title}".'

            srcChrNames.append(source.characters[crId].title)

        # Check locations.
        srcLocTitles = []
        for lcId in source.locations:
            if not lcId in linkedLocations:
                continue

            if source.locations[lcId].title in srcLocTitles:
                return f'{ERROR}Ambiguous yWriter location "{source.locations[lcId].title}".'

            srcLocTitles.append(source.locations[lcId].title)

        # Check items.
        srcItmTitles = []
        for itId in source.items:
            if not itId in linkedItems:
                continue

            if source.items[itId].title in srcItmTitles:
                return f'{ERROR}Ambiguous yWriter item "{source.items[itId].title}".'

            srcItmTitles.append(source.items[itId].title)

        #--- Check the target for ambiguous titles.
        # Check scenes.
        scIdsByTitle = {}
        for scId in self.scenes:
            if self.scenes[scId].title in scIdsByTitle:
                return f'{ERROR}Ambiguous Aeon event title "{self.scenes[scId].title}".'

            scIdsByTitle[self.scenes[scId].title] = scId

            #--- Mark non-scene events.
            # This is to recognize "Trash" scenes.
            if not self.scenes[scId].title in srcScnTitles:
                if not self.scenes[scId].isNotesScene:
                    self._trashEvents.append(int(scId) - 1)

        # Check characters.
        crIdsByTitle = {}
        for crId in self.characters:
            if self.characters[crId].title in crIdsByTitle:
                return f'{ERROR}Ambiguous Aeon character "{self.characters[crId].title}".'

            crIdsByTitle[self.characters[crId].title] = crId

        # Check locations.
        lcIdsByTitle = {}
        for lcId in self.locations:
            if self.locations[lcId].title in lcIdsByTitle:
                return f'{ERROR}Ambiguous Aeon location "{self.locations[lcId].title}".'

            lcIdsByTitle[self.locations[lcId].title] = lcId

        # Check items.
        itIdsByTitle = {}
        for itId in self.items:
            if self.items[itId].title in itIdsByTitle:
                return f'{ERROR}Ambiguous Aeon item "{self.items[itId].title}".'

            itIdsByTitle[self.items[itId].title] = itId

        #--- Update characters from the source.
        crIdMax = len(self.characters)
        crIdsBySrcId = {}
        for srcCrId in source.characters:
            if source.characters[srcCrId].title in crIdsByTitle:
                crIdsBySrcId[srcCrId] = crIdsByTitle[source.characters[srcCrId].title]
            elif srcCrId in linkedCharacters:
                #--- Create a new character if it is assigned to at least one scene.
                crIdMax += 1
                crId = str(crIdMax)
                crIdsBySrcId[srcCrId] = crId
                self.characters[crId] = source.characters[srcCrId]
                newGuid = get_uid(f'{crId}{self.characters[crId].title}')
                self._characterGuidById[crId] = newGuid
                self._jsonData['entities'].append(
                    {
                        'entityType': self._typeCharacterGuid,
                        'guid': newGuid,
                        'icon': 'person',
                        'name': self.characters[crId].title,
                        'notes': '',
                        'sortOrder': crIdMax - 1,
                        'swatchColor': 'darkPink'
                    })

        #--- Update locations from the source.
        lcIdMax = len(self.locations)
        lcIdsBySrcId = {}
        for srcLcId in source.locations:
            if source.locations[srcLcId].title in lcIdsByTitle:
                lcIdsBySrcId[srcLcId] = lcIdsByTitle[source.locations[srcLcId].title]
            elif srcLcId in linkedLocations:
                #--- Create a new location if it is assigned to at least one scene.
                lcIdMax += 1
                lcId = str(lcIdMax)
                lcIdsBySrcId[srcLcId] = lcId
                self.locations[lcId] = source.locations[srcLcId]
                newGuid = get_uid(f'{lcId}{self.locations[lcId].title}')
                self._locationGuidById[lcId] = newGuid
                self._jsonData['entities'].append(
                    {
                        'entityType': self._typeLocationGuid,
                        'guid': newGuid,
                        'icon': 'map',
                        'name': self.locations[lcId].title,
                        'notes': '',
                        'sortOrder': lcIdMax - 1,
                        'swatchColor': 'orange'
                    })

        #--- Update Items from the source.
        itIdMax = len(self.items)
        itIdsBySrcId = {}
        for srcItId in source.items:
            if source.items[srcItId].title in itIdsByTitle:
                itIdsBySrcId[srcItId] = itIdsByTitle[source.items[srcItId].title]
            elif srcItId in linkedItems:
                #--- Create a new Item if it is assigned to at least one scene.
                itIdMax += 1
                itId = str(itIdMax)
                itIdsBySrcId[srcItId] = itId
                self.items[itId] = source.items[srcItId]
                newGuid = get_uid(f'{itId}{self.items[itId].title}')
                self._itemGuidById[itId] = newGuid
                self._jsonData['entities'].append(
                    {
                        'entityType': self._typeItemGuid,
                        'guid': newGuid,
                        'icon': 'cube',
                        'name': self.items[itId].title,
                        'notes': '',
                        'sortOrder': itIdMax - 1,
                        'swatchColor': 'denim'
                    })

        #--- Update scenes from the source.
        totalEvents = len(self._jsonData['events'])
        for chId in source.chapters:
            for srcId in source.chapters[chId].srtScenes:
                if source.scenes[srcId].isUnused and not source.scenes[srcId].isNotesScene:
                    # Remove unused scene from the "Narrative" arc.
                    if source.scenes[srcId].title in scIdsByTitle:
                        scId = scIdsByTitle[source.scenes[srcId].title]
                        self.scenes[scId].isNotesScene = True
                    continue

                if source.scenes[srcId].isNotesScene and self._scenesOnly:
                    # Remove unsynchronized scene from the "Narrative" arc.
                    if source.scenes[srcId].title in scIdsByTitle:
                        scId = scIdsByTitle[source.scenes[srcId].title]
                        self.scenes[scId].isNotesScene = True
                    continue

                if source.scenes[srcId].title in scIdsByTitle:
                    scId = scIdsByTitle[source.scenes[srcId].title]
                else:
                    #--- Create a new scene.
                    totalEvents += 1
                    scId = str(totalEvents)
                    self.scenes[scId] = self.SCENE_CLASS()
                    self.scenes[scId].title = source.scenes[srcId].title
                    newEvent = build_event(self.scenes[scId])
                    self._jsonData['events'].append(newEvent)
                self.scenes[scId].status = source.scenes[srcId].status

                #--- Update scene type.
                self.scenes[scId].isNotesScene = source.scenes[srcId].isNotesScene
                self.scenes[scId].isUnused = source.scenes[srcId].isUnused

                #--- Update scene tags.
                if source.scenes[srcId].tags is not None:
                    self.scenes[scId].tags = source.scenes[srcId].tags

                #--- Update scene description.
                if source.scenes[srcId].desc is not None:
                    self.scenes[scId].desc = source.scenes[srcId].desc

                #--- Update scene characters.
                if source.scenes[srcId].characters is not None:
                    self.scenes[scId].characters = []
                    for crId in source.scenes[srcId].characters:
                        if crId in crIdsBySrcId:
                            self.scenes[scId].characters.append(crIdsBySrcId[crId])

                #--- Update scene locations.
                if source.scenes[srcId].locations is not None:
                    self.scenes[scId].locations = []
                    for lcId in source.scenes[srcId].locations:
                        if lcId in lcIdsBySrcId:
                            self.scenes[scId].locations.append(lcIdsBySrcId[lcId])

                #--- Update scene items.
                if source.scenes[srcId].items is not None:
                    self.scenes[scId].items = []
                    for itId in source.scenes[srcId].items:
                        if itId in itIdsBySrcId:
                            self.scenes[scId].items.append(itIdsBySrcId[itId])

                #--- Update scene start date/time.
                if source.scenes[srcId].date or source.scenes[srcId].time:
                    if source.scenes[srcId].date is not None:
                        self.scenes[scId].date = source.scenes[srcId].date
                    if source.scenes[srcId].time is not None:
                        self.scenes[scId].time = source.scenes[srcId].time
                elif source.scenes[srcId].minute or source.scenes[srcId].hour or source.scenes[srcId].day:
                    self.scenes[scId].date = None
                    self.scenes[scId].time = None
                if source.scenes[srcId].minute is not None:
                    self.scenes[scId].minute = source.scenes[srcId].minute
                if source.scenes[srcId].hour is not None:
                    self.scenes[scId].hour = source.scenes[srcId].hour
                if source.scenes[srcId].day is not None:
                    self.scenes[scId].day = source.scenes[srcId].day

                #--- Update scene duration.
                if source.scenes[srcId].lastsMinutes is not None:
                    self.scenes[scId].lastsMinutes = source.scenes[srcId].lastsMinutes
                if source.scenes[srcId].lastsHours is not None:
                    self.scenes[scId].lastsHours = source.scenes[srcId].lastsHours
                if source.scenes[srcId].lastsDays is not None:
                    self.scenes[scId].lastsDays = source.scenes[srcId].lastsDays

                #--- Update scene keyword variables.
                for fieldName in self._SCN_KWVAR:
                    try:
                        self.scenes[scId].kwVar[fieldName] = source.scenes[srcId].kwVar[fieldName]
                    except:
                        pass

        return 'Timeline updated from novel data.'

    def write(self):
        """Write instance variables to the file.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

        def get_timestamp(scene):
            """Return a timestamp integer from the scene date.
            
            Positional arguments:
                scene -- Scene instance
            """
            self._timestampMax += 1
            timestamp = int(self._timestampMax)
            try:
                if scene.date:
                    isoDt = scene.date
                    if scene.time:
                        isoDt = (f'{isoDt} {scene.time}')
                timestamp = int((datetime.fromisoformat(isoDt) - datetime.min).total_seconds())
            except:
                pass
            return timestamp

        def get_span(scene):
            """Return a time span dictionary from the scene duration.
            
            Positional arguments:
                scene -- Scene instance
            """
            span = {}
            if scene.lastsDays:
                span['days'] = int(scene.lastsDays)
            if scene.lastsHours:
                span['hours'] = int(scene.lastsHours)
            if scene.lastsMinutes:
                span['minutes'] = int(scene.lastsMinutes)
            return span

        #--- Add "Narrative" arc, if missing.
        if self._entityNarrativeGuid is None:
            self._entityNarrativeGuid = get_uid('entityNarrativeGuid')
            self._jsonData['entities'].append(
                {
                    'entityType': self._typeArcGuid,
                    'guid': self._entityNarrativeGuid,
                    'icon': 'book',
                    'name': self._entityNarrative,
                    'notes': '',
                    'sortOrder': self._arcCount,
                    'swatchColor': 'orange'
                })
            self._arcCount += 1
        narrativeArc = {
            'entity': self._entityNarrativeGuid,
            'percentAllocated': 1,
            'role': self._roleArcGuid,
        }

        #--- Add missing arcs.
        arcs = {}
        for arcName in self._arcGuidsByName:
            if self._arcGuidsByName[arcName] is None:
                guid = get_uid(f'entity{arcName}ArcGuid')
                self._arcGuidsByName[arcName] = guid
                self._jsonData['entities'].append(
                    {
                        'entityType': self._typeArcGuid,
                        'guid': guid,
                        'icon': 'book',
                        'name': arcName,
                        'notes': '',
                        'sortOrder': self._arcCount,
                        'swatchColor': 'orange'
                    })
                self._arcCount += 1
            arcs[arcName] = {
                'entity': self._arcGuidsByName[arcName],
                'percentAllocated': 1,
                'role': self._roleStorylineGuid,
            }

        #--- Update events from scenes.
        eventCount = 0
        for evt in self._jsonData['events']:
            eventCount += 1
            scId = str(eventCount)

            #--- Set event date/time/span.
            if evt['rangeValues'][0]['position']['timestamp'] >= self.DATE_LIMIT:
                evt['rangeValues'][0]['span'] = get_span(self.scenes[scId])
                evt['rangeValues'][0]['position']['timestamp'] = get_timestamp(self.scenes[scId])

            #--- Calculate moon phase.
            if self._propertyMoonphaseGuid is not None:
                eventMoonphase = get_moon_phase_plus(self.scenes[scId].date)
            else:
                eventMoonphase = ''

            #--- Set scene description, notes, and moon phase.
            hasMoonphase = False
            for evtVal in evt['values']:

                # Set scene description.
                if evtVal['property'] == self._propertyDescGuid:
                    if self.scenes[scId].desc:
                        evtVal['value'] = self.scenes[scId].desc

                # Set scene notes.
                elif evtVal['property'] == self._propertyNotesGuid:
                    if self.scenes[scId].sceneNotes:
                        evtVal['value'] = self.scenes[scId].sceneNotes

                # Set moon phase.
                elif evtVal['property'] == self._propertyMoonphaseGuid:
                        evtVal['value'] = eventMoonphase
                        hasMoonphase = True

            #--- Add missing event properties.
            if not hasMoonphase and self._propertyMoonphaseGuid is not None:
                evt['values'].append({'property': self._propertyMoonphaseGuid, 'value': eventMoonphase})

            #--- Set scene tags.
            if self.scenes[scId].tags:
                evt['tags'] = self.scenes[scId].tags

            #--- Update characters, locations, and items.
            # Delete assignments.
            newRel = []
            for evtRel in evt['relationships']:
                if evtRel['role'] == self._roleCharacterGuid:
                    continue

                elif evtRel['role'] == self._roleLocationGuid:
                    continue

                elif evtRel['role'] == self._roleItemGuid:
                    continue

                else:
                    newRel.append(evtRel)

            # Add characters.
            if self.scenes[scId].characters:
                for crId in self.scenes[scId].characters:
                    if self.scenes[scId].characters:
                        newRel.append(
                            {
                                'entity': self._characterGuidById[crId],
                                'percentAllocated': 1,
                                'role': self._roleCharacterGuid,
                            })

            # Add locations.
            if self.scenes[scId].locations:
                for lcId in self.scenes[scId].locations:
                    if self.scenes[scId].locations:
                        newRel.append(
                            {
                                'entity': self._locationGuidById[lcId],
                                'percentAllocated': 1,
                                'role': self._roleLocationGuid,
                            })

            # Add items.
            if self.scenes[scId].items:
                for itId in self.scenes[scId].items:
                    if self.scenes[scId].items:
                        newRel.append(
                            {
                                'entity': self._itemGuidById[itId],
                                'percentAllocated': 1,
                                'role': self._roleItemGuid,
                            })

            evt['relationships'] = newRel

            #--- Assign "scene" events to the "Narrative" arc.
            if self.scenes[scId].isNotesScene:
                if narrativeArc in evt['relationships']:
                    evt['relationships'].remove(narrativeArc)
            else:
                if narrativeArc not in evt['relationships']:
                    evt['relationships'].append(narrativeArc)

                #--- Assign events to arcs.
                if self.scenes[scId].kwVar['Field_SceneArcs']:
                    sceneArcs = self.scenes[scId].kwVar['Field_SceneArcs'].split(';')
                else:
                    sceneArcs = []
                for arcName in arcs:
                    if arcName in sceneArcs:
                        if arcs[arcName] not in evt['relationships']:
                            evt['relationships'].append(arcs[arcName])
                    else:
                        try:
                            evt['relationships'].remove(arcs[arcName])
                        except:
                            pass

        #--- Delete "Trash" scenes.
        events = []
        for i, evt in enumerate(self._jsonData['events']):
            if not i in self._trashEvents:
                events.append(evt)
        self._jsonData['events'] = events
        return save_timeline(self._jsonData, self.filePath)
from html import unescape
import xml.etree.ElementTree as ET


class Splitter:
    """Helper class for scene and chapter splitting.
    
    When importing scenes to yWriter, they may contain manuallyinserted scene and chapter dividers.
    The Splitter class updates a Novel instance by splitting such scenes and creating new chapters and scenes. 
    
    Public methods:
        split_scenes(novel) -- Split scenes by inserted chapter and scene dividers.
        
    Public class constants:
        PART_SEPARATOR -- marker indicating the beginning of a new part, splitting a scene.
        CHAPTER_SEPARATOR -- marker indicating the beginning of a new chapter, splitting a scene.
        DESC_SEPARATOR -- marker separating title and description of a chapter or scene.
    """
    PART_SEPARATOR = '#'
    CHAPTER_SEPARATOR = '##'
    SCENE_SEPARATOR = '###'
    DESC_SEPARATOR = '|'
    _CLIP_TITLE = 20
    # Maximum length of newly generated scene titles.

    def split_scenes(self, novel):
        """Split scenes by inserted chapter and scene dividers.
        
        Update a Novel instance by generating new chapters and scenes 
        if there are dividers within the scene content.
        
        Positional argument: 
            novel -- Novel instance to update.
        
        Return True if the sructure has changed, 
        otherwise return False.        
        """

        def create_chapter(chapterId, title, desc, level):
            """Create a new chapter and add it to the novel.
            
            Positional arguments:
                chapterId -- str: ID of the chapter to create.
                title -- str: title of the chapter to create.
                desc -- str: description of the chapter to create.
                level -- int: chapter level (part/chapter).           
            """
            newChapter = novel.CHAPTER_CLASS()
            newChapter.title = title
            newChapter.desc = desc
            newChapter.chLevel = level
            newChapter.chType = 0
            novel.chapters[chapterId] = newChapter

        def create_scene(sceneId, parent, splitCount, title, desc):
            """Create a new scene and add it to the novel.
            
            Positional arguments:
                sceneId -- str: ID of the scene to create.
                parent -- Scene instance: parent scene.
                splitCount -- int: number of parent's splittings.
                title -- str: title of the scene to create.
                desc -- str: description of the scene to create.
            """
            WARNING = '(!)'

            # Mark metadata of split scenes.
            newScene = novel.SCENE_CLASS()
            if title:
                newScene.title = title
            elif parent.title:
                if len(parent.title) > self._CLIP_TITLE:
                    title = f'{parent.title[:self._CLIP_TITLE]}...'
                else:
                    title = parent.title
                newScene.title = f'{title} Split: {splitCount}'
            else:
                newScene.title = f'_("New Scene") Split: {splitCount}'
            if desc:
                newScene.desc = desc
            if parent.desc and not parent.desc.startswith(WARNING):
                parent.desc = f'{WARNING}{parent.desc}'
            if parent.goal and not parent.goal.startswith(WARNING):
                parent.goal = f'{WARNING}{parent.goal}'
            if parent.conflict and not parent.conflict.startswith(WARNING):
                parent.conflict = f'{WARNING}{parent.conflict}'
            if parent.outcome and not parent.outcome.startswith(WARNING):
                parent.outcome = f'{WARNING}{parent.outcome}'

            # Reset the parent's status to Draft, if not Outline.
            if parent.status > 2:
                parent.status = 2
            newScene.status = parent.status
            newScene.isNotesScene = parent.isNotesScene
            newScene.isUnused = parent.isUnused
            newScene.isTodoScene = parent.isTodoScene
            newScene.date = parent.date
            newScene.time = parent.time
            newScene.day = parent.day
            newScene.hour = parent.hour
            newScene.minute = parent.minute
            newScene.lastsDays = parent.lastsDays
            newScene.lastsHours = parent.lastsHours
            newScene.lastsMinutes = parent.lastsMinutes
            novel.scenes[sceneId] = newScene

        # Get the maximum chapter ID and scene ID.
        chIdMax = 0
        scIdMax = 0
        for chId in novel.srtChapters:
            if int(chId) > chIdMax:
                chIdMax = int(chId)
        for scId in novel.scenes:
            if int(scId) > scIdMax:
                scIdMax = int(scId)

        # Process chapters and scenes.
        scenesSplit = False
        srtChapters = []
        for chId in novel.srtChapters:
            srtChapters.append(chId)
            chapterId = chId
            srtScenes = []
            for scId in novel.chapters[chId].srtScenes:
                srtScenes.append(scId)
                if not novel.scenes[scId].sceneContent:
                    continue

                sceneId = scId
                lines = novel.scenes[scId].sceneContent.split('\n')
                newLines = []
                inScene = True
                sceneSplitCount = 0

                # Search scene content for dividers.
                for line in lines:
                    heading = line.strip('# ').split(self.DESC_SEPARATOR)
                    title = heading[0]
                    try:
                        desc = heading[1]
                    except:
                        desc = ''
                    if line.startswith(self.SCENE_SEPARATOR):
                        # Split the scene.
                        novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
                        newLines = []
                        sceneSplitCount += 1
                        scIdMax += 1
                        sceneId = str(scIdMax)
                        create_scene(sceneId, novel.scenes[scId], sceneSplitCount, title, desc)
                        srtScenes.append(sceneId)
                        scenesSplit = True
                        inScene = True
                    elif line.startswith(self.CHAPTER_SEPARATOR):
                        # Start a new chapter.
                        if inScene:
                            novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
                            newLines = []
                            sceneSplitCount = 0
                            inScene = False
                        novel.chapters[chapterId].srtScenes = srtScenes
                        srtScenes = []
                        chIdMax += 1
                        chapterId = str(chIdMax)
                        if not title:
                            title = _('New Chapter')
                        create_chapter(chapterId, title, desc, 0)
                        srtChapters.append(chapterId)
                        scenesSplit = True
                    elif line.startswith(self.PART_SEPARATOR):
                        # start a new part.
                        if inScene:
                            novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
                            newLines = []
                            sceneSplitCount = 0
                            inScene = False
                        novel.chapters[chapterId].srtScenes = srtScenes
                        srtScenes = []
                        chIdMax += 1
                        chapterId = str(chIdMax)
                        if not title:
                            title = _('New Part')
                        create_chapter(chapterId, title, desc, 1)
                        srtChapters.append(chapterId)
                    elif not inScene:
                        # Append a scene without heading to a new chapter or part.
                        newLines.append(line)
                        sceneSplitCount += 1
                        scIdMax += 1
                        sceneId = str(scIdMax)
                        create_scene(sceneId, novel.scenes[scId], sceneSplitCount, '', '')
                        srtScenes.append(sceneId)
                        scenesSplit = True
                        inScene = True
                    else:
                        newLines.append(line)
                novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
            novel.chapters[chapterId].srtScenes = srtScenes
        novel.srtChapters = srtChapters
        return scenesSplit


def indent(elem, level=0):
    """xml pretty printer

    Kudos to to Fredrik Lundh. 
    Source: http://effbot.org/zone/element-lib.htm#prettyprint
    """
    i = f'\n{level * "  "}'
    if elem:
        if not elem.text or not elem.text.strip():
            elem.text = f'{i}  '
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class Yw7File(Novel):
    """yWriter 7 project file representation.

    Public methods: 
        read() -- parse the yWriter xml file and get the instance variables.
        merge(source) -- update instance variables from a source instance.
        write() -- write instance variables to the yWriter xml file.
        is_locked() -- check whether the yw7 file is locked by yWriter.
        remove_custom_fields() -- Remove custom fields from the yWriter file.

    Public instance variables:
        tree -- xml element tree of the yWriter project
        scenesSplit -- bool: True, if a scene or chapter is split during merging.
    """
    DESCRIPTION = _('yWriter 7 project')
    EXTENSION = '.yw7'
    _CDATA_TAGS = ['Title', 'AuthorName', 'Bio', 'Desc',
                   'FieldTitle1', 'FieldTitle2', 'FieldTitle3',
                   'FieldTitle4', 'LaTeXHeaderFile', 'Tags',
                   'AKA', 'ImageFile', 'FullName', 'Goals',
                   'Notes', 'RTFFile', 'SceneContent',
                   'Outcome', 'Goal', 'Conflict']
    # Names of xml elements containing CDATA.
    # ElementTree.write omits CDATA tags, so they have to be inserted afterwards.

    _PRJ_KWVAR = ()
    _CHP_KWVAR = ()
    _SCN_KWVAR = ()
    _CRT_KWVAR = ()
    _LOC_KWVAR = ()
    _ITM_KWVAR = ()
    # Keyword variables for custom fields in the .yw7 XML file.

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.
        
        Positional arguments:
            filePath -- str: path to the yw7 file.
            
        Optional arguments:
            kwargs -- keyword arguments (not used here).            
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self.tree = None
        self.scenesSplit = False

        #--- Initialize custom keyword variables.
        for field in self._PRJ_KWVAR:
            self.kwVar[field] = None

    def read(self):
        """Parse the yWriter xml file and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
        if self.is_locked():
            return f'{ERROR}{_("yWriter seems to be open. Please close first")}.'
        try:
            self.tree = ET.parse(self.filePath)
        except:
            return f'{ERROR}{_("Can not process file")}: "{os.path.normpath(self.filePath)}".'

        root = self.tree.getroot()

        #--- Read locations from the xml element tree.
        self.srtLocations = []
        # This is necessary for re-reading.
        for loc in root.iter('LOCATION'):
            lcId = loc.find('ID').text
            self.srtLocations.append(lcId)
            self.locations[lcId] = self.WE_CLASS()

            if loc.find('Title') is not None:
                self.locations[lcId].title = loc.find('Title').text

            if loc.find('ImageFile') is not None:
                self.locations[lcId].image = loc.find('ImageFile').text

            if loc.find('Desc') is not None:
                self.locations[lcId].desc = loc.find('Desc').text

            if loc.find('AKA') is not None:
                self.locations[lcId].aka = loc.find('AKA').text

            if loc.find('Tags') is not None:
                if loc.find('Tags').text is not None:
                    tags = loc.find('Tags').text.split(';')
                    self.locations[lcId].tags = self._strip_spaces(tags)

            #--- Initialize custom keyword variables.
            for fieldName in self._LOC_KWVAR:
                self.locations[lcId].kwVar[fieldName] = None

            #--- Read location custom fields.
            for lcFields in loc.findall('Fields'):
                for fieldName in self._LOC_KWVAR:
                    field = lcFields.find(fieldName)
                    if field is not None:
                        self.locations[lcId].kwVar[fieldName] = field.text

        #--- Read items from the xml element tree.
        self.srtItems = []
        # This is necessary for re-reading.
        for itm in root.iter('ITEM'):
            itId = itm.find('ID').text
            self.srtItems.append(itId)
            self.items[itId] = self.WE_CLASS()

            if itm.find('Title') is not None:
                self.items[itId].title = itm.find('Title').text

            if itm.find('ImageFile') is not None:
                self.items[itId].image = itm.find('ImageFile').text

            if itm.find('Desc') is not None:
                self.items[itId].desc = itm.find('Desc').text

            if itm.find('AKA') is not None:
                self.items[itId].aka = itm.find('AKA').text

            if itm.find('Tags') is not None:
                if itm.find('Tags').text is not None:
                    tags = itm.find('Tags').text.split(';')
                    self.items[itId].tags = self._strip_spaces(tags)

            #--- Initialize custom keyword variables.
            for fieldName in self._ITM_KWVAR:
                self.items[itId].kwVar[fieldName] = None

            #--- Read item custom fields.
            for itFields in itm.findall('Fields'):
                for fieldName in self._ITM_KWVAR:
                    field = itFields.find(fieldName)
                    if field is not None:
                        self.items[itId].kwVar[fieldName] = field.text

        #--- Read characters from the xml element tree.
        self.srtCharacters = []
        # This is necessary for re-reading.
        for crt in root.iter('CHARACTER'):
            crId = crt.find('ID').text
            self.srtCharacters.append(crId)
            self.characters[crId] = self.CHARACTER_CLASS()

            if crt.find('Title') is not None:
                self.characters[crId].title = crt.find('Title').text

            if crt.find('ImageFile') is not None:
                self.characters[crId].image = crt.find('ImageFile').text

            if crt.find('Desc') is not None:
                self.characters[crId].desc = crt.find('Desc').text

            if crt.find('AKA') is not None:
                self.characters[crId].aka = crt.find('AKA').text

            if crt.find('Tags') is not None:
                if crt.find('Tags').text is not None:
                    tags = crt.find('Tags').text.split(';')
                    self.characters[crId].tags = self._strip_spaces(tags)

            if crt.find('Notes') is not None:
                self.characters[crId].notes = crt.find('Notes').text

            if crt.find('Bio') is not None:
                self.characters[crId].bio = crt.find('Bio').text

            if crt.find('Goals') is not None:
                self.characters[crId].goals = crt.find('Goals').text

            if crt.find('FullName') is not None:
                self.characters[crId].fullName = crt.find('FullName').text

            if crt.find('Major') is not None:
                self.characters[crId].isMajor = True
            else:
                self.characters[crId].isMajor = False

            #--- Initialize custom keyword variables.
            for fieldName in self._CRT_KWVAR:
                self.characters[crId].kwVar[fieldName] = None

            #--- Read character custom fields.
            for crFields in crt.findall('Fields'):
                for fieldName in self._CRT_KWVAR:
                    field = crFields.find(fieldName)
                    if field is not None:
                        self.characters[crId].kwVar[fieldName] = field.text

        #--- Read attributes at novel level from the xml element tree.
        prj = root.find('PROJECT')

        if prj.find('Title') is not None:
            self.title = prj.find('Title').text

        if prj.find('AuthorName') is not None:
            self.authorName = prj.find('AuthorName').text

        if prj.find('Bio') is not None:
            self.authorBio = prj.find('Bio').text

        if prj.find('Desc') is not None:
            self.desc = prj.find('Desc').text

        if prj.find('FieldTitle1') is not None:
            self.fieldTitle1 = prj.find('FieldTitle1').text

        if prj.find('FieldTitle2') is not None:
            self.fieldTitle2 = prj.find('FieldTitle2').text

        if prj.find('FieldTitle3') is not None:
            self.fieldTitle3 = prj.find('FieldTitle3').text

        if prj.find('FieldTitle4') is not None:
            self.fieldTitle4 = prj.find('FieldTitle4').text

        #--- Initialize custom keyword variables.
        for fieldName in self._PRJ_KWVAR:
            self.kwVar[fieldName] = None

        #--- Read project custom fields.
        for prjFields in prj.findall('Fields'):
            for fieldName in self._PRJ_KWVAR:
                field = prjFields.find(fieldName)
                if field is not None:
                    self.kwVar[fieldName] = field.text

        #--- Read attributes at chapter level from the xml element tree.
        self.srtChapters = []
        # This is necessary for re-reading.
        for chp in root.iter('CHAPTER'):
            chId = chp.find('ID').text
            self.chapters[chId] = self.CHAPTER_CLASS()
            self.srtChapters.append(chId)

            if chp.find('Title') is not None:
                self.chapters[chId].title = chp.find('Title').text

            if chp.find('Desc') is not None:
                self.chapters[chId].desc = chp.find('Desc').text

            if chp.find('SectionStart') is not None:
                self.chapters[chId].chLevel = 1
            else:
                self.chapters[chId].chLevel = 0

            if chp.find('ChapterType') is not None:
                self.chapters[chId].chType = int(chp.find('ChapterType').text)
            elif chp.find('Type') is not None:
                self.chapters[chId].chType = int(chp.find('Type').text)
            else:
                self.chapters[chId].chType = 0

            if chp.find('Unused') is not None:
                self.chapters[chId].isUnused = True
            else:
                self.chapters[chId].isUnused = False
            self.chapters[chId].suppressChapterTitle = False
            if self.chapters[chId].title is not None:
                if self.chapters[chId].title.startswith('@'):
                    self.chapters[chId].suppressChapterTitle = True

            #--- Initialize custom keyword variables.
            for fieldName in self._CHP_KWVAR:
                self.chapters[chId].kwVar[fieldName] = None

            #--- Read chapter fields.
            for chFields in chp.findall('Fields'):
                if chFields.find('Field_SuppressChapterTitle') is not None:
                    if chFields.find('Field_SuppressChapterTitle').text == '1':
                        self.chapters[chId].suppressChapterTitle = True
                self.chapters[chId].isTrash = False
                if chFields.find('Field_IsTrash') is not None:
                    if chFields.find('Field_IsTrash').text == '1':
                        self.chapters[chId].isTrash = True
                self.chapters[chId].suppressChapterBreak = False
                if chFields.find('Field_SuppressChapterBreak') is not None:
                    if chFields.find('Field_SuppressChapterBreak').text == '1':
                        self.chapters[chId].suppressChapterBreak = True

                #--- Read chapter custom fields.
                for fieldName in self._CHP_KWVAR:
                    field = chFields.find(fieldName)
                    if field is not None:
                        self.chapters[chId].kwVar[fieldName] = field.text

            self.chapters[chId].srtScenes = []
            if chp.find('Scenes') is not None:
                for scn in chp.find('Scenes').findall('ScID'):
                    scId = scn.text
                    self.chapters[chId].srtScenes.append(scId)

        #--- Read attributes at scene level from the xml element tree.
        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text
            self.scenes[scId] = self.SCENE_CLASS()

            if scn.find('Title') is not None:
                self.scenes[scId].title = scn.find('Title').text

            if scn.find('Desc') is not None:
                self.scenes[scId].desc = scn.find('Desc').text

            if scn.find('RTFFile') is not None:
                self.scenes[scId].rtfFile = scn.find('RTFFile').text

            # This is relevant for yW5 files with no SceneContent:
            if scn.find('WordCount') is not None:
                self.scenes[scId].wordCount = int(
                    scn.find('WordCount').text)

            if scn.find('LetterCount') is not None:
                self.scenes[scId].letterCount = int(
                    scn.find('LetterCount').text)

            if scn.find('SceneContent') is not None:
                sceneContent = scn.find('SceneContent').text
                if sceneContent is not None:
                    self.scenes[scId].sceneContent = sceneContent

            if scn.find('Unused') is not None:
                self.scenes[scId].isUnused = True
            else:
                self.scenes[scId].isUnused = False
            self.scenes[scId].isNotesScene = False
            self.scenes[scId].isTodoScene = False

            #--- Initialize custom keyword variables.
            for fieldName in self._SCN_KWVAR:
                self.scenes[scId].kwVar[fieldName] = None

            #--- Read scene fields.
            for scFields in scn.findall('Fields'):
                self.scenes[scId].isTodoScene = False
                if scFields.find('Field_SceneType') is not None:
                    if scFields.find('Field_SceneType').text == '1':
                        self.scenes[scId].isNotesScene = True
                    if scFields.find('Field_SceneType').text == '2':
                        self.scenes[scId].isTodoScene = True

                #--- Read scene custom fields.
                for fieldName in self._SCN_KWVAR:
                    field = scFields.find(fieldName)
                    if field is not None:
                        self.scenes[scId].kwVar[fieldName] = field.text

            if scn.find('ExportCondSpecific') is None:
                self.scenes[scId].doNotExport = False
            elif scn.find('ExportWhenRTF') is not None:
                self.scenes[scId].doNotExport = False
            else:
                self.scenes[scId].doNotExport = True

            if scn.find('Status') is not None:
                self.scenes[scId].status = int(scn.find('Status').text)

            if scn.find('Notes') is not None:
                self.scenes[scId].sceneNotes = scn.find('Notes').text

            if scn.find('Tags') is not None:
                if scn.find('Tags').text is not None:
                    tags = scn.find('Tags').text.split(';')
                    self.scenes[scId].tags = self._strip_spaces(tags)

            if scn.find('Field1') is not None:
                self.scenes[scId].field1 = scn.find('Field1').text

            if scn.find('Field2') is not None:
                self.scenes[scId].field2 = scn.find('Field2').text

            if scn.find('Field3') is not None:
                self.scenes[scId].field3 = scn.find('Field3').text

            if scn.find('Field4') is not None:
                self.scenes[scId].field4 = scn.find('Field4').text

            if scn.find('AppendToPrev') is not None:
                self.scenes[scId].appendToPrev = True
            else:
                self.scenes[scId].appendToPrev = False

            if scn.find('SpecificDateTime') is not None:
                dateTime = scn.find('SpecificDateTime').text.split(' ')
                for dt in dateTime:
                    if '-' in dt:
                        self.scenes[scId].date = dt
                    elif ':' in dt:
                        self.scenes[scId].time = dt
            else:
                if scn.find('Day') is not None:
                    self.scenes[scId].day = scn.find('Day').text

                if scn.find('Hour') is not None:
                    self.scenes[scId].hour = scn.find('Hour').text

                if scn.find('Minute') is not None:
                    self.scenes[scId].minute = scn.find('Minute').text

            if scn.find('LastsDays') is not None:
                self.scenes[scId].lastsDays = scn.find('LastsDays').text

            if scn.find('LastsHours') is not None:
                self.scenes[scId].lastsHours = scn.find('LastsHours').text

            if scn.find('LastsMinutes') is not None:
                self.scenes[scId].lastsMinutes = scn.find('LastsMinutes').text

            if scn.find('ReactionScene') is not None:
                self.scenes[scId].isReactionScene = True
            else:
                self.scenes[scId].isReactionScene = False

            if scn.find('SubPlot') is not None:
                self.scenes[scId].isSubPlot = True
            else:
                self.scenes[scId].isSubPlot = False

            if scn.find('Goal') is not None:
                self.scenes[scId].goal = scn.find('Goal').text

            if scn.find('Conflict') is not None:
                self.scenes[scId].conflict = scn.find('Conflict').text

            if scn.find('Outcome') is not None:
                self.scenes[scId].outcome = scn.find('Outcome').text

            if scn.find('ImageFile') is not None:
                self.scenes[scId].image = scn.find('ImageFile').text

            if scn.find('Characters') is not None:
                for crId in scn.find('Characters').iter('CharID'):
                    if self.scenes[scId].characters is None:
                        self.scenes[scId].characters = []
                    self.scenes[scId].characters.append(crId.text)

            if scn.find('Locations') is not None:
                for lcId in scn.find('Locations').iter('LocID'):
                    if self.scenes[scId].locations is None:
                        self.scenes[scId].locations = []
                    self.scenes[scId].locations.append(lcId.text)

            if scn.find('Items') is not None:
                for itId in scn.find('Items').iter('ItemID'):
                    if self.scenes[scId].items is None:
                        self.scenes[scId].items = []
                    self.scenes[scId].items.append(itId.text)

        # Make sure that ToDo, Notes, and Unused type is inherited from the chapter.
        for chId in self.chapters:
            if self.chapters[chId].chType == 2:
                # Chapter is "ToDo" type.
                for scId in self.chapters[chId].srtScenes:
                    self.scenes[scId].isTodoScene = True
                    self.scenes[scId].isUnused = True
            elif self.chapters[chId].chType == 1:
                # Chapter is "Notes" type.
                for scId in self.chapters[chId].srtScenes:
                    self.scenes[scId].isNotesScene = True
                    self.scenes[scId].isUnused = True
            elif self.chapters[chId].isUnused:
                for scId in self.chapters[chId].srtScenes:
                    self.scenes[scId].isUnused = True
        return 'yWriter project data read in.'

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Novel subclass instance to merge.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

        def merge_lists(srcLst, tgtLst):
            """Insert srcLst items to tgtLst, if missing.
            """
            j = 0
            for i in range(len(srcLst)):
                if not srcLst[i] in tgtLst:
                    tgtLst.insert(j, srcLst[i])
                    j += 1
                else:
                    j = tgtLst.index(srcLst[i]) + 1

        if os.path.isfile(self.filePath):
            message = self.read()
            # initialize data
            if message.startswith(ERROR):
                return message

        #--- Merge and re-order locations.
        if source.srtLocations:
            self.srtLocations = source.srtLocations
            temploc = self.locations
            self.locations = {}
            for lcId in source.srtLocations:

                # Build a new self.locations dictionary sorted like the source.
                self.locations[lcId] = self.WE_CLASS()
                if not lcId in temploc:
                    # A new location has been added
                    temploc[lcId] = self.WE_CLASS()
                if source.locations[lcId].title:
                    # avoids deleting the title, if it is empty by accident
                    self.locations[lcId].title = source.locations[lcId].title
                else:
                    self.locations[lcId].title = temploc[lcId].title
                if source.locations[lcId].image is not None:
                    self.locations[lcId].image = source.locations[lcId].image
                else:
                    self.locations[lcId].desc = temploc[lcId].desc
                if source.locations[lcId].desc is not None:
                    self.locations[lcId].desc = source.locations[lcId].desc
                else:
                    self.locations[lcId].desc = temploc[lcId].desc
                if source.locations[lcId].aka is not None:
                    self.locations[lcId].aka = source.locations[lcId].aka
                else:
                    self.locations[lcId].aka = temploc[lcId].aka
                if source.locations[lcId].tags is not None:
                    self.locations[lcId].tags = source.locations[lcId].tags
                else:
                    self.locations[lcId].tags = temploc[lcId].tags
                for fieldName in self._LOC_KWVAR:
                    try:
                        self.locations[lcId].kwVar[fieldName] = source.locations[lcId].kwVar[fieldName]
                    except:
                        self.locations[lcId].kwVar[fieldName] = temploc[lcId].kwVar[fieldName]

        #--- Merge and re-order items.
        if source.srtItems:
            self.srtItems = source.srtItems
            tempitm = self.items
            self.items = {}
            for itId in source.srtItems:

                # Build a new self.items dictionary sorted like the source.
                self.items[itId] = self.WE_CLASS()
                if not itId in tempitm:
                    # A new item has been added
                    tempitm[itId] = self.WE_CLASS()
                if source.items[itId].title:
                    # avoids deleting the title, if it is empty by accident
                    self.items[itId].title = source.items[itId].title
                else:
                    self.items[itId].title = tempitm[itId].title
                if source.items[itId].image is not None:
                    self.items[itId].image = source.items[itId].image
                else:
                    self.items[itId].image = tempitm[itId].image
                if source.items[itId].desc is not None:
                    self.items[itId].desc = source.items[itId].desc
                else:
                    self.items[itId].desc = tempitm[itId].desc
                if source.items[itId].aka is not None:
                    self.items[itId].aka = source.items[itId].aka
                else:
                    self.items[itId].aka = tempitm[itId].aka
                if source.items[itId].tags is not None:
                    self.items[itId].tags = source.items[itId].tags
                else:
                    self.items[itId].tags = tempitm[itId].tags
                for fieldName in self._ITM_KWVAR:
                    try:
                        self.items[itId].kwVar[fieldName] = source.items[itId].kwVar[fieldName]
                    except:
                        self.items[itId].kwVar[fieldName] = tempitm[itId].kwVar[fieldName]

        #--- Merge and re-order characters.
        if source.srtCharacters:
            self.srtCharacters = source.srtCharacters
            tempchr = self.characters
            self.characters = {}
            for crId in source.srtCharacters:

                # Build a new self.characters dictionary sorted like the source.
                self.characters[crId] = self.CHARACTER_CLASS()
                if not crId in tempchr:
                    # A new character has been added
                    tempchr[crId] = self.CHARACTER_CLASS()
                if source.characters[crId].title:
                    # avoids deleting the title, if it is empty by accident
                    self.characters[crId].title = source.characters[crId].title
                else:
                    self.characters[crId].title = tempchr[crId].title
                if source.characters[crId].image is not None:
                    self.characters[crId].image = source.characters[crId].image
                else:
                    self.characters[crId].image = tempchr[crId].image
                if source.characters[crId].desc is not None:
                    self.characters[crId].desc = source.characters[crId].desc
                else:
                    self.characters[crId].desc = tempchr[crId].desc
                if source.characters[crId].aka is not None:
                    self.characters[crId].aka = source.characters[crId].aka
                else:
                    self.characters[crId].aka = tempchr[crId].aka
                if source.characters[crId].tags is not None:
                    self.characters[crId].tags = source.characters[crId].tags
                else:
                    self.characters[crId].tags = tempchr[crId].tags
                if source.characters[crId].notes is not None:
                    self.characters[crId].notes = source.characters[crId].notes
                else:
                    self.characters[crId].notes = tempchr[crId].notes
                if source.characters[crId].bio is not None:
                    self.characters[crId].bio = source.characters[crId].bio
                else:
                    self.characters[crId].bio = tempchr[crId].bio
                if source.characters[crId].goals is not None:
                    self.characters[crId].goals = source.characters[crId].goals
                else:
                    self.characters[crId].goals = tempchr[crId].goals
                if source.characters[crId].fullName is not None:
                    self.characters[crId].fullName = source.characters[crId].fullName
                else:
                    self.characters[crId].fullName = tempchr[crId].fullName
                if source.characters[crId].isMajor is not None:
                    self.characters[crId].isMajor = source.characters[crId].isMajor
                else:
                    self.characters[crId].isMajor = tempchr[crId].isMajor
                for fieldName in self._CRT_KWVAR:
                    try:
                        self.characters[crId].kwVar[fieldName] = source.characters[crId].kwVar[fieldName]
                    except:
                        self.characters[crId].kwVar[fieldName] = tempchr[crId].kwVar[fieldName]

        #--- Merge scenes.
        sourceHasSceneContent = False
        for scId in source.scenes:
            if not scId in self.scenes:
                self.scenes[scId] = self.SCENE_CLASS()
            if source.scenes[scId].title:
                # avoids deleting the title, if it is empty by accident
                self.scenes[scId].title = source.scenes[scId].title
            if source.scenes[scId].desc is not None:
                self.scenes[scId].desc = source.scenes[scId].desc
            if source.scenes[scId].sceneContent is not None:
                self.scenes[scId].sceneContent = source.scenes[scId].sceneContent
                sourceHasSceneContent = True
            if source.scenes[scId].isUnused is not None:
                self.scenes[scId].isUnused = source.scenes[scId].isUnused
            if source.scenes[scId].isNotesScene is not None:
                self.scenes[scId].isNotesScene = source.scenes[scId].isNotesScene
            if source.scenes[scId].isTodoScene is not None:
                self.scenes[scId].isTodoScene = source.scenes[scId].isTodoScene
            if source.scenes[scId].status is not None:
                self.scenes[scId].status = source.scenes[scId].status
            if source.scenes[scId].sceneNotes is not None:
                self.scenes[scId].sceneNotes = source.scenes[scId].sceneNotes
            if source.scenes[scId].tags is not None:
                self.scenes[scId].tags = source.scenes[scId].tags
            if source.scenes[scId].field1 is not None:
                self.scenes[scId].field1 = source.scenes[scId].field1
            if source.scenes[scId].field2 is not None:
                self.scenes[scId].field2 = source.scenes[scId].field2
            if source.scenes[scId].field3 is not None:
                self.scenes[scId].field3 = source.scenes[scId].field3
            if source.scenes[scId].field4 is not None:
                self.scenes[scId].field4 = source.scenes[scId].field4
            if source.scenes[scId].appendToPrev is not None:
                self.scenes[scId].appendToPrev = source.scenes[scId].appendToPrev
            if source.scenes[scId].date or source.scenes[scId].time:
                if source.scenes[scId].date is not None:
                    self.scenes[scId].date = source.scenes[scId].date
                if source.scenes[scId].time is not None:
                    self.scenes[scId].time = source.scenes[scId].time
            elif source.scenes[scId].minute or source.scenes[scId].hour or source.scenes[scId].day:
                self.scenes[scId].date = None
                self.scenes[scId].time = None
            if source.scenes[scId].minute is not None:
                self.scenes[scId].minute = source.scenes[scId].minute
            if source.scenes[scId].hour is not None:
                self.scenes[scId].hour = source.scenes[scId].hour
            if source.scenes[scId].day is not None:
                self.scenes[scId].day = source.scenes[scId].day
            if source.scenes[scId].lastsMinutes is not None:
                self.scenes[scId].lastsMinutes = source.scenes[scId].lastsMinutes
            if source.scenes[scId].lastsHours is not None:
                self.scenes[scId].lastsHours = source.scenes[scId].lastsHours
            if source.scenes[scId].lastsDays is not None:
                self.scenes[scId].lastsDays = source.scenes[scId].lastsDays
            if source.scenes[scId].isReactionScene is not None:
                self.scenes[scId].isReactionScene = source.scenes[scId].isReactionScene
            if source.scenes[scId].isSubPlot is not None:
                self.scenes[scId].isSubPlot = source.scenes[scId].isSubPlot
            if source.scenes[scId].goal is not None:
                self.scenes[scId].goal = source.scenes[scId].goal
            if source.scenes[scId].conflict is not None:
                self.scenes[scId].conflict = source.scenes[scId].conflict
            if source.scenes[scId].outcome is not None:
                self.scenes[scId].outcome = source.scenes[scId].outcome
            if source.scenes[scId].characters is not None:
                self.scenes[scId].characters = []
                for crId in source.scenes[scId].characters:
                    if crId in self.characters:
                        self.scenes[scId].characters.append(crId)
            if source.scenes[scId].locations is not None:
                self.scenes[scId].locations = []
                for lcId in source.scenes[scId].locations:
                    if lcId in self.locations:
                        self.scenes[scId].locations.append(lcId)
            if source.scenes[scId].items is not None:
                self.scenes[scId].items = []
                for itId in source.scenes[scId].items:
                    if itId in self.items:
                        self.scenes[scId].items.append(itId)
            for fieldName in self._SCN_KWVAR:
                try:
                    self.scenes[scId].kwVar[fieldName] = source.scenes[scId].kwVar[fieldName]
                except:
                    pass

        #--- Merge chapters.
        for chId in source.chapters:
            if not chId in self.chapters:
                self.chapters[chId] = self.CHAPTER_CLASS()
            if source.chapters[chId].title:
                # avoids deleting the title, if it is empty by accident
                self.chapters[chId].title = source.chapters[chId].title
            if source.chapters[chId].desc is not None:
                self.chapters[chId].desc = source.chapters[chId].desc
            if source.chapters[chId].chLevel is not None:
                self.chapters[chId].chLevel = source.chapters[chId].chLevel
            if source.chapters[chId].chType is not None:
                self.chapters[chId].chType = source.chapters[chId].chType
            if source.chapters[chId].isUnused is not None:
                self.chapters[chId].isUnused = source.chapters[chId].isUnused
            if source.chapters[chId].suppressChapterTitle is not None:
                self.chapters[chId].suppressChapterTitle = source.chapters[chId].suppressChapterTitle
            if source.chapters[chId].suppressChapterBreak is not None:
                self.chapters[chId].suppressChapterBreak = source.chapters[chId].suppressChapterBreak
            if source.chapters[chId].isTrash is not None:
                self.chapters[chId].isTrash = source.chapters[chId].isTrash
            for fieldName in self._CHP_KWVAR:
                try:
                    self.chapters[chId].kwVar[fieldName] = source.chapters[chId].kwVar[fieldName]
                except:
                    pass

            #--- Merge the chapter's scene list.
            # New scenes may be added.
            # Existing scenes may be moved to another chapter.
            # Deletion of scenes is not considered.
            # The scene's sort order may not change.

            # Remove scenes that have been moved to another chapter from the scene list.
            srtScenes = []
            for scId in self.chapters[chId].srtScenes:
                if scId in source.chapters[chId].srtScenes or not scId in source.scenes:
                    # The scene has not moved to another chapter or isn't imported
                    srtScenes.append(scId)
            self.chapters[chId].srtScenes = srtScenes

            # Add new or moved scenes to the scene list.
            merge_lists(source.chapters[chId].srtScenes, self.chapters[chId].srtScenes)

        #--- Merge project attributes.
        if source.title:
            # avoids deleting the title, if it is empty by accident
            self.title = source.title
        if source.desc is not None:
            self.desc = source.desc
        if source.authorName is not None:
            self.authorName = source.authorName
        if source.authorBio is not None:
            self.authorBio = source.authorBio
        if source.fieldTitle1 is not None:
            self.fieldTitle1 = source.fieldTitle1
        if source.fieldTitle2 is not None:
            self.fieldTitle2 = source.fieldTitle2
        if source.fieldTitle3 is not None:
            self.fieldTitle3 = source.fieldTitle3
        if source.fieldTitle4 is not None:
            self.fieldTitle4 = source.fieldTitle4
        for fieldName in self._PRJ_KWVAR:
            try:
                self.kwVar[fieldName] = source.kwVar[fieldName]
            except:
                pass

        # Add new chapters to the chapter list.
        # Deletion of chapters is not considered.
        # The sort order of chapters may not change.
        merge_lists(source.srtChapters, self.srtChapters)

        # Split scenes by inserted part/chapter/scene dividers.
        # This must be done after regular merging
        # in order to avoid creating duplicate IDs.
        if sourceHasSceneContent:
            sceneSplitter = Splitter()
            self.scenesSplit = sceneSplitter.split_scenes(self)
        return 'yWriter project data updated or created.'

    def write(self):
        """Write instance variables to the yWriter xml file.
        
        Open the yWriter xml file located at filePath and replace the instance variables 
        not being None. Create new XML elements if necessary.
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
        if self.is_locked():
            return f'{ERROR}{_("yWriter seems to be open. Please close first")}.'

        self._build_element_tree()
        message = self._write_element_tree(self)
        if message.startswith(ERROR):
            return message

        return self._postprocess_xml_file(self.filePath)

    def is_locked(self):
        """Check whether the yw7 file is locked by yWriter.
        
        Return True if a .lock file placed by yWriter exists.
        Otherwise, return False. 
        """
        return os.path.isfile(f'{self.filePath}.lock')

    def _build_element_tree(self):
        """Modify the yWriter project attributes of an existing xml element tree."""

        def build_scene_subtree(xmlScn, prjScn):
            if prjScn.title is not None:
                try:
                    xmlScn.find('Title').text = prjScn.title
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Title').text = prjScn.title
            if xmlScn.find('BelongsToChID') is None:
                for chId in self.chapters:
                    if scId in self.chapters[chId].srtScenes:
                        ET.SubElement(xmlScn, 'BelongsToChID').text = chId
                        break

            if prjScn.desc is not None:
                try:
                    xmlScn.find('Desc').text = prjScn.desc
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Desc').text = prjScn.desc

            if xmlScn.find('SceneContent') is None:
                ET.SubElement(xmlScn, 'SceneContent').text = prjScn.sceneContent

            if xmlScn.find('WordCount') is None:
                ET.SubElement(xmlScn, 'WordCount').text = str(prjScn.wordCount)

            if xmlScn.find('LetterCount') is None:
                ET.SubElement(xmlScn, 'LetterCount').text = str(prjScn.letterCount)

            if prjScn.isUnused:
                if xmlScn.find('Unused') is None:
                    ET.SubElement(xmlScn, 'Unused').text = '-1'
            elif xmlScn.find('Unused') is not None:
                xmlScn.remove(xmlScn.find('Unused'))

            #--- Write scene fields.
            scFields = xmlScn.find('Fields')
            if prjScn.isNotesScene:
                if scFields is None:
                    scFields = ET.SubElement(xmlScn, 'Fields')
                try:
                    scFields.find('Field_SceneType').text = '1'
                except(AttributeError):
                    ET.SubElement(scFields, 'Field_SceneType').text = '1'
            elif scFields is not None:
                if scFields.find('Field_SceneType') is not None:
                    if scFields.find('Field_SceneType').text == '1':
                        scFields.remove(scFields.find('Field_SceneType'))

            if prjScn.isTodoScene:
                if scFields is None:
                    scFields = ET.SubElement(xmlScn, 'Fields')
                try:
                    scFields.find('Field_SceneType').text = '2'
                except(AttributeError):
                    ET.SubElement(scFields, 'Field_SceneType').text = '2'
            elif scFields is not None:
                if scFields.find('Field_SceneType') is not None:
                    if scFields.find('Field_SceneType').text == '2':
                        scFields.remove(scFields.find('Field_SceneType'))

            #--- Write scene custom fields.
            for field in self._SCN_KWVAR:
                if field in self.scenes[scId].kwVar and self.scenes[scId].kwVar[field]:
                    if scFields is None:
                        scFields = ET.SubElement(xmlScn, 'Fields')
                    try:
                        scFields.find(field).text = self.scenes[scId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(scFields, field).text = self.scenes[scId].kwVar[field]
                elif scFields is not None:
                    try:
                        scFields.remove(scFields.find(field))
                    except:
                        pass

            if prjScn.status is not None:
                try:
                    xmlScn.find('Status').text = str(prjScn.status)
                except:
                    ET.SubElement(xmlScn, 'Status').text = str(prjScn.status)

            if prjScn.sceneNotes is not None:
                try:
                    xmlScn.find('Notes').text = prjScn.sceneNotes
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Notes').text = prjScn.sceneNotes

            if prjScn.tags is not None:
                try:
                    xmlScn.find('Tags').text = ';'.join(prjScn.tags)
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Tags').text = ';'.join(prjScn.tags)

            if prjScn.field1 is not None:
                try:
                    xmlScn.find('Field1').text = prjScn.field1
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Field1').text = prjScn.field1

            if prjScn.field2 is not None:
                try:
                    xmlScn.find('Field2').text = prjScn.field2
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Field2').text = prjScn.field2

            if prjScn.field3 is not None:
                try:
                    xmlScn.find('Field3').text = prjScn.field3
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Field3').text = prjScn.field3

            if prjScn.field4 is not None:
                try:
                    xmlScn.find('Field4').text = prjScn.field4
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Field4').text = prjScn.field4

            if prjScn.appendToPrev:
                if xmlScn.find('AppendToPrev') is None:
                    ET.SubElement(xmlScn, 'AppendToPrev').text = '-1'
            elif xmlScn.find('AppendToPrev') is not None:
                xmlScn.remove(xmlScn.find('AppendToPrev'))

            # Date/time information
            if (prjScn.date is not None) and (prjScn.time is not None):
                dateTime = f'{prjScn.date} {prjScn.time}'
                if xmlScn.find('SpecificDateTime') is not None:
                    xmlScn.find('SpecificDateTime').text = dateTime
                else:
                    ET.SubElement(xmlScn, 'SpecificDateTime').text = dateTime
                    ET.SubElement(xmlScn, 'SpecificDateMode').text = '-1'

                    if xmlScn.find('Day') is not None:
                        xmlScn.remove(xmlScn.find('Day'))

                    if xmlScn.find('Hour') is not None:
                        xmlScn.remove(xmlScn.find('Hour'))

                    if xmlScn.find('Minute') is not None:
                        xmlScn.remove(xmlScn.find('Minute'))

            elif (prjScn.day is not None) or (prjScn.hour is not None) or (prjScn.minute is not None):

                if xmlScn.find('SpecificDateTime') is not None:
                    xmlScn.remove(xmlScn.find('SpecificDateTime'))

                if xmlScn.find('SpecificDateMode') is not None:
                    xmlScn.remove(xmlScn.find('SpecificDateMode'))
                if prjScn.day is not None:
                    try:
                        xmlScn.find('Day').text = prjScn.day
                    except(AttributeError):
                        ET.SubElement(xmlScn, 'Day').text = prjScn.day
                if prjScn.hour is not None:
                    try:
                        xmlScn.find('Hour').text = prjScn.hour
                    except(AttributeError):
                        ET.SubElement(xmlScn, 'Hour').text = prjScn.hour
                if prjScn.minute is not None:
                    try:
                        xmlScn.find('Minute').text = prjScn.minute
                    except(AttributeError):
                        ET.SubElement(xmlScn, 'Minute').text = prjScn.minute

            if prjScn.lastsDays is not None:
                try:
                    xmlScn.find('LastsDays').text = prjScn.lastsDays
                except(AttributeError):
                    ET.SubElement(xmlScn, 'LastsDays').text = prjScn.lastsDays

            if prjScn.lastsHours is not None:
                try:
                    xmlScn.find('LastsHours').text = prjScn.lastsHours
                except(AttributeError):
                    ET.SubElement(xmlScn, 'LastsHours').text = prjScn.lastsHours

            if prjScn.lastsMinutes is not None:
                try:
                    xmlScn.find('LastsMinutes').text = prjScn.lastsMinutes
                except(AttributeError):
                    ET.SubElement(xmlScn, 'LastsMinutes').text = prjScn.lastsMinutes

            # Plot related information
            if prjScn.isReactionScene:
                if xmlScn.find('ReactionScene') is None:
                    ET.SubElement(xmlScn, 'ReactionScene').text = '-1'
            elif xmlScn.find('ReactionScene') is not None:
                xmlScn.remove(xmlScn.find('ReactionScene'))

            if prjScn.isSubPlot:
                if xmlScn.find('SubPlot') is None:
                    ET.SubElement(xmlScn, 'SubPlot').text = '-1'
            elif xmlScn.find('SubPlot') is not None:
                xmlScn.remove(xmlScn.find('SubPlot'))

            if prjScn.goal is not None:
                try:
                    xmlScn.find('Goal').text = prjScn.goal
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Goal').text = prjScn.goal

            if prjScn.conflict is not None:
                try:
                    xmlScn.find('Conflict').text = prjScn.conflict
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Conflict').text = prjScn.conflict

            if prjScn.outcome is not None:
                try:
                    xmlScn.find('Outcome').text = prjScn.outcome
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Outcome').text = prjScn.outcome

            if prjScn.image is not None:
                try:
                    xmlScn.find('ImageFile').text = prjScn.image
                except(AttributeError):
                    ET.SubElement(xmlScn, 'ImageFile').text = prjScn.image

            # Characters/locations/items
            if prjScn.characters is not None:
                characters = xmlScn.find('Characters')
                try:
                    for oldCrId in characters.findall('CharID'):
                        characters.remove(oldCrId)
                except(AttributeError):
                    characters = ET.SubElement(xmlScn, 'Characters')
                for crId in prjScn.characters:
                    ET.SubElement(characters, 'CharID').text = crId

            if prjScn.locations is not None:
                locations = xmlScn.find('Locations')
                try:
                    for oldLcId in locations.findall('LocID'):
                        locations.remove(oldLcId)
                except(AttributeError):
                    locations = ET.SubElement(xmlScn, 'Locations')
                for lcId in prjScn.locations:
                    ET.SubElement(locations, 'LocID').text = lcId

            if prjScn.items is not None:
                items = xmlScn.find('Items')
                try:
                    for oldItId in items.findall('ItemID'):
                        items.remove(oldItId)
                except(AttributeError):
                    items = ET.SubElement(xmlScn, 'Items')
                for itId in prjScn.items:
                    ET.SubElement(items, 'ItemID').text = itId

        def build_chapter_subtree(xmlChp, prjChp, sortOrder):
            try:
                xmlChp.find('SortOrder').text = str(sortOrder)
            except(AttributeError):
                ET.SubElement(xmlChp, 'SortOrder').text = str(sortOrder)
            try:
                xmlChp.find('Title').text = prjChp.title
            except(AttributeError):
                ET.SubElement(xmlChp, 'Title').text = prjChp.title

            if prjChp.desc is not None:
                try:
                    xmlChp.find('Desc').text = prjChp.desc
                except(AttributeError):
                    ET.SubElement(xmlChp, 'Desc').text = prjChp.desc

            if xmlChp.find('SectionStart') is not None:
                if prjChp.chLevel == 0:
                    xmlChp.remove(xmlChp.find('SectionStart'))
            elif prjChp.chLevel == 1:
                ET.SubElement(xmlChp, 'SectionStart').text = '-1'

            if prjChp.chType is None:
                prjChp.chType = 0
            try:
                xmlChp.find('ChapterType').text = str(prjChp.chType)
            except(AttributeError):
                ET.SubElement(xmlChp, 'ChapterType').text = str(prjChp.chType)
            if prjChp.chType == 0:
                oldType = '0'
            else:
                oldType = '1'
            try:
                xmlChp.find('Type').text = oldType
            except(AttributeError):
                ET.SubElement(xmlChp, 'Type').text = oldType

            if prjChp.isUnused:
                if xmlChp.find('Unused') is None:
                    ET.SubElement(xmlChp, 'Unused').text = '-1'
            elif xmlChp.find('Unused') is not None:
                xmlChp.remove(xmlChp.find('Unused'))

            #--- Write chapter fields.
            chFields = xmlChp.find('Fields')
            if prjChp.suppressChapterTitle:
                if chFields is None:
                    chFields = ET.SubElement(xmlChp, 'Fields')
                try:
                    chFields.find('Field_SuppressChapterTitle').text = '1'
                except(AttributeError):
                    ET.SubElement(chFields, 'Field_SuppressChapterTitle').text = '1'
            elif chFields is not None:
                if chFields.find('Field_SuppressChapterTitle') is not None:
                    chFields.find('Field_SuppressChapterTitle').text = '0'

            if prjChp.suppressChapterBreak:
                if chFields is None:
                    chFields = ET.SubElement(xmlChp, 'Fields')
                try:
                    chFields.find('Field_SuppressChapterBreak').text = '1'
                except(AttributeError):
                    ET.SubElement(chFields, 'Field_SuppressChapterBreak').text = '1'
            elif chFields is not None:
                if chFields.find('Field_SuppressChapterBreak') is not None:
                    chFields.find('Field_SuppressChapterBreak').text = '0'

            if prjChp.isTrash:
                if chFields is None:
                    chFields = ET.SubElement(xmlChp, 'Fields')
                try:
                    chFields.find('Field_IsTrash').text = '1'
                except(AttributeError):
                    ET.SubElement(chFields, 'Field_IsTrash').text = '1'
            elif chFields is not None:
                if chFields.find('Field_IsTrash') is not None:
                    chFields.remove(chFields.find('Field_IsTrash'))

            #--- Write chapter custom fields.
            for field in self._CHP_KWVAR:
                if field in self.chapters[chId].kwVar and self.chapters[chId].kwVar[field]:
                    if chFields is None:
                        chFields = ET.SubElement(xmlChp, 'Fields')
                    try:
                        chFields.find(field).text = self.chapters[chId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(chFields, field).text = self.chapters[chId].kwVar[field]
                elif chFields is not None:
                    try:
                        chFields.remove(chFields.find(field))
                    except:
                        pass

            #--- Rebuild the chapter's scene list.
            try:
                xScnList = xmlChp.find('Scenes')
                xmlChp.remove(xScnList)
            except:
                pass
            if prjChp.srtScenes:
                sortSc = ET.SubElement(xmlChp, 'Scenes')
                for scId in prjChp.srtScenes:
                    ET.SubElement(sortSc, 'ScID').text = scId

        def build_location_subtree(xmlLoc, prjLoc, sortOrder):
            ET.SubElement(xmlLoc, 'ID').text = lcId
            if prjLoc.title is not None:
                ET.SubElement(xmlLoc, 'Title').text = prjLoc.title

            if prjLoc.image is not None:
                ET.SubElement(xmlLoc, 'ImageFile').text = prjLoc.image

            if prjLoc.desc is not None:
                ET.SubElement(xmlLoc, 'Desc').text = prjLoc.desc

            if prjLoc.aka is not None:
                ET.SubElement(xmlLoc, 'AKA').text = prjLoc.aka

            if prjLoc.tags is not None:
                ET.SubElement(xmlLoc, 'Tags').text = ';'.join(prjLoc.tags)

            ET.SubElement(xmlLoc, 'SortOrder').text = str(sortOrder)

            #--- Write location custom fields.
            lcFields = xmlLoc.find('Fields')
            for field in self._LOC_KWVAR:
                if field in self.locations[lcId].kwVar and self.locations[lcId].kwVar[field]:
                    if lcFields is None:
                        lcFields = ET.SubElement(xmlLoc, 'Fields')
                    try:
                        lcFields.find(field).text = self.locations[lcId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(lcFields, field).text = self.locations[lcId].kwVar[field]
                elif lcFields is not None:
                    try:
                        lcFields.remove(lcFields.find(field))
                    except:
                        pass

        def build_item_subtree(xmlItm, prjItm, sortOrder):
            ET.SubElement(xmlItm, 'ID').text = itId

            if prjItm.title is not None:
                ET.SubElement(xmlItm, 'Title').text = prjItm.title

            if prjItm.image is not None:
                ET.SubElement(xmlItm, 'ImageFile').text = prjItm.image

            if prjItm.desc is not None:
                ET.SubElement(xmlItm, 'Desc').text = prjItm.desc

            if prjItm.aka is not None:
                ET.SubElement(xmlItm, 'AKA').text = prjItm.aka

            if prjItm.tags is not None:
                ET.SubElement(xmlItm, 'Tags').text = ';'.join(prjItm.tags)

            ET.SubElement(xmlItm, 'SortOrder').text = str(sortOrder)

            #--- Write item custom fields.
            itFields = xmlItm.find('Fields')
            for field in self._ITM_KWVAR:
                if field in self.items[itId].kwVar and self.items[itId].kwVar[field]:
                    if itFields is None:
                        itFields = ET.SubElement(xmlItm, 'Fields')
                    try:
                        itFields.find(field).text = self.items[itId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(itFields, field).text = self.items[itId].kwVar[field]
                elif itFields is not None:
                    try:
                        itFields.remove(itFields.find(field))
                    except:
                        pass

        def build_character_subtree(xmlCrt, prjCrt, sortOrder):
            ET.SubElement(xmlCrt, 'ID').text = crId

            if prjCrt.title is not None:
                ET.SubElement(xmlCrt, 'Title').text = prjCrt.title

            if prjCrt.desc is not None:
                ET.SubElement(xmlCrt, 'Desc').text = prjCrt.desc

            if prjCrt.image is not None:
                ET.SubElement(xmlCrt, 'ImageFile').text = prjCrt.image

            ET.SubElement(xmlCrt, 'SortOrder').text = str(sortOrder)

            if prjCrt.notes is not None:
                ET.SubElement(xmlCrt, 'Notes').text = prjCrt.notes

            if prjCrt.aka is not None:
                ET.SubElement(xmlCrt, 'AKA').text = prjCrt.aka

            if prjCrt.tags is not None:
                ET.SubElement(xmlCrt, 'Tags').text = ';'.join(prjCrt.tags)

            if prjCrt.bio is not None:
                ET.SubElement(xmlCrt, 'Bio').text = prjCrt.bio

            if prjCrt.goals is not None:
                ET.SubElement(xmlCrt, 'Goals').text = prjCrt.goals

            if prjCrt.fullName is not None:
                ET.SubElement(xmlCrt, 'FullName').text = prjCrt.fullName

            if prjCrt.isMajor:
                ET.SubElement(xmlCrt, 'Major').text = '-1'

            #--- Write character custom fields.
            crFields = xmlCrt.find('Fields')
            for field in self._CRT_KWVAR:
                if field in self.characters[crId].kwVar and self.characters[crId].kwVar[field]:
                    if crFields is None:
                        crFields = ET.SubElement(xmlCrt, 'Fields')
                    try:
                        crFields.find(field).text = self.characters[crId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(crFields, field).text = self.characters[crId].kwVar[field]
                elif crFields is not None:
                    try:
                        crFields.remove(crFields.find(field))
                    except:
                        pass

        def build_project_subtree(xmlPrj):
            VER = '7'
            try:
                xmlPrj.find('Ver').text = VER
            except(AttributeError):
                ET.SubElement(xmlPrj, 'Ver').text = VER

            if self.title is not None:
                try:
                    xmlPrj.find('Title').text = self.title
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Title').text = self.title

            if self.desc is not None:
                try:
                    xmlPrj.find('Desc').text = self.desc
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Desc').text = self.desc

            if self.authorName is not None:
                try:
                    xmlPrj.find('AuthorName').text = self.authorName
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'AuthorName').text = self.authorName

            if self.authorBio is not None:
                try:
                    xmlPrj.find('Bio').text = self.authorBio
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Bio').text = self.authorBio

            if self.fieldTitle1 is not None:
                try:
                    xmlPrj.find('FieldTitle1').text = self.fieldTitle1
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle1').text = self.fieldTitle1

            if self.fieldTitle2 is not None:
                try:
                    xmlPrj.find('FieldTitle2').text = self.fieldTitle2
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle2').text = self.fieldTitle2

            if self.fieldTitle3 is not None:
                try:
                    xmlPrj.find('FieldTitle3').text = self.fieldTitle3
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle3').text = self.fieldTitle3

            if self.fieldTitle4 is not None:
                try:
                    xmlPrj.find('FieldTitle4').text = self.fieldTitle4
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle4').text = self.fieldTitle4

            #--- Write project custom fields.
            prjFields = xmlPrj.find('Fields')
            for field in self._PRJ_KWVAR:
                setting = self.kwVar[field]
                if setting:
                    if prjFields is None:
                        prjFields = ET.SubElement(xmlPrj, 'Fields')
                    try:
                        prjFields.find(field).text = setting
                    except(AttributeError):
                        ET.SubElement(prjFields, field).text = setting
                else:
                    try:
                        prjFields.remove(prjFields.find(field))
                    except:
                        pass

        TAG = 'YWRITER7'
        xmlScenes = {}
        xmlChapters = {}
        try:
            # Try processing an existing tree.
            root = self.tree.getroot()
            xmlPrj = root.find('PROJECT')
            locations = root.find('LOCATIONS')
            items = root.find('ITEMS')
            characters = root.find('CHARACTERS')
            scenes = root.find('SCENES')
            chapters = root.find('CHAPTERS')
        except(AttributeError):
            # Build a new tree.
            root = ET.Element(TAG)
            xmlPrj = ET.SubElement(root, 'PROJECT')
            locations = ET.SubElement(root, 'LOCATIONS')
            items = ET.SubElement(root, 'ITEMS')
            characters = ET.SubElement(root, 'CHARACTERS')
            scenes = ET.SubElement(root, 'SCENES')
            chapters = ET.SubElement(root, 'CHAPTERS')

        #--- Process project attributes.

        build_project_subtree(xmlPrj)

        #--- Process locations.

        # Remove LOCATION entries in order to rewrite
        # the LOCATIONS section in a modified sort order.
        for xmlLoc in locations.findall('LOCATION'):
            locations.remove(xmlLoc)

        # Add the new XML location subtrees to the project tree.
        sortOrder = 0
        for lcId in self.srtLocations:
            sortOrder += 1
            xmlLoc = ET.SubElement(locations, 'LOCATION')
            build_location_subtree(xmlLoc, self.locations[lcId], sortOrder)

        #--- Process items.

        # Remove ITEM entries in order to rewrite
        # the ITEMS section in a modified sort order.
        for xmlItm in items.findall('ITEM'):
            items.remove(xmlItm)

        # Add the new XML item subtrees to the project tree.
        sortOrder = 0
        for itId in self.srtItems:
            sortOrder += 1
            xmlItm = ET.SubElement(items, 'ITEM')
            build_item_subtree(xmlItm, self.items[itId], sortOrder)

        #--- Process characters.

        # Remove CHARACTER entries in order to rewrite
        # the CHARACTERS section in a modified sort order.
        for xmlCrt in characters.findall('CHARACTER'):
            characters.remove(xmlCrt)

        # Add the new XML character subtrees to the project tree.
        sortOrder = 0
        for crId in self.srtCharacters:
            sortOrder += 1
            xmlCrt = ET.SubElement(characters, 'CHARACTER')
            build_character_subtree(xmlCrt, self.characters[crId], sortOrder)

        #--- Process scenes.

        # Save the original XML scene subtrees
        # and remove them from the project tree.
        for xmlScn in scenes.findall('SCENE'):
            scId = xmlScn.find('ID').text
            xmlScenes[scId] = xmlScn
            scenes.remove(xmlScn)

        # Add the new XML scene subtrees to the project tree.
        for scId in self.scenes:
            if not scId in xmlScenes:
                xmlScenes[scId] = ET.Element('SCENE')
                ET.SubElement(xmlScenes[scId], 'ID').text = scId
            build_scene_subtree(xmlScenes[scId], self.scenes[scId])
            scenes.append(xmlScenes[scId])

        #--- Process chapters.

        # Save the original XML chapter subtree
        # and remove it from the project tree.
        for xmlChp in chapters.findall('CHAPTER'):
            chId = xmlChp.find('ID').text
            xmlChapters[chId] = xmlChp
            chapters.remove(xmlChp)

        # Add the new XML chapter subtrees to the project tree.
        sortOrder = 0
        for chId in self.srtChapters:
            sortOrder += 1
            if not chId in xmlChapters:
                xmlChapters[chId] = ET.Element('CHAPTER')
                ET.SubElement(xmlChapters[chId], 'ID').text = chId
            build_chapter_subtree(xmlChapters[chId], self.chapters[chId], sortOrder)
            chapters.append(xmlChapters[chId])

        # Modify the scene contents of an existing xml element tree.
        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text
            if self.scenes[scId].sceneContent is not None:
                scn.find('SceneContent').text = self.scenes[scId].sceneContent
                scn.find('WordCount').text = str(self.scenes[scId].wordCount)
                scn.find('LetterCount').text = str(self.scenes[scId].letterCount)
            try:
                scn.remove(scn.find('RTFFile'))
            except:
                pass
        indent(root)
        self.tree = ET.ElementTree(root)

    def _write_element_tree(self, ywProject):
        """Write back the xml element tree to a .yw7 xml file located at filePath.
        
        Return a message beginning with the ERROR constant in case of error.
        """
        if os.path.isfile(ywProject.filePath):
            os.replace(ywProject.filePath, f'{ywProject.filePath}.bak')
            backedUp = True
        else:
            backedUp = False
        try:
            ywProject.tree.write(ywProject.filePath, xml_declaration=False, encoding='utf-8')
        except:
            if backedUp:
                os.replace(f'{ywProject.filePath}.bak', ywProject.filePath)
            return f'{ERROR}{_("Cannot write file")}: "{os.path.normpath(ywProject.filePath)}".'

        return 'yWriter XML tree written.'

    def _postprocess_xml_file(self, filePath):
        '''Postprocess an xml file created by ElementTree.
        
        Positional argument:
            filePath -- str: path to xml file.
        
        Read the xml file, put a header on top, insert the missing CDATA tags,
        and replace xml entities by plain text (unescape). Overwrite the .yw7 xml file.
        Return a message beginning with the ERROR constant in case of error.
        
        Note: The path is given as an argument rather than using self.filePath. 
        So this routine can be used for yWriter-generated xml files other than .yw7 as well. 
        '''
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        lines = text.split('\n')
        newlines = ['<?xml version="1.0" encoding="utf-8"?>']
        for line in lines:
            for tag in self._CDATA_TAGS:
                line = re.sub(f'\<{tag}\>', f'<{tag}><![CDATA[', line)
                line = re.sub(f'\<\/{tag}\>', f']]></{tag}>', line)
            newlines.append(line)
        text = '\n'.join(newlines)
        text = text.replace('[CDATA[ \n', '[CDATA[')
        text = text.replace('\n]]', ']]')
        text = unescape(text)
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            return f'{ERROR}{_("Cannot write file")}: "{os.path.normpath(filePath)}".'

        return f'{_("File written")}: "{os.path.normpath(filePath)}".'

    def _strip_spaces(self, lines):
        """Local helper method.

        Positional argument:
            lines -- list of strings

        Return lines with leading and trailing spaces removed.
        """
        stripped = []
        for line in lines:
            stripped.append(line.strip())
        return stripped

    def reset_custom_variables(self):
        """Set custom keyword variables to an empty string.
        
        Thus the write() method will remove the associated custom fields
        from the .yw7 XML file. 
        Return True, if a keyword variable has changed (i.e information is lost).
        """
        hasChanged = False
        for field in self._PRJ_KWVAR:
            if self.kwVar[field]:
                self.kwVar[field] = ''
                hasChanged = True
        for chId in self.chapters:
            for field in self._CHP_KWVAR:
                if self.chapters[chId].kwVar[field]:
                    self.chapters[chId].kwVar[field] = ''
                    hasChanged = True
        for scId in self.scenes:
            for field in self._SCN_KWVAR:
                if self.scenes[scId].kwVar[field]:
                    self.scenes[scId].kwVar[field] = ''
                    hasChanged = True
        return hasChanged



class Yw7Target(Yw7File):
    """yWriter 7 project file representation.
    Extend the superclass
    """
    _SCN_KWVAR = (
        'Field_SceneArcs',
        )

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Required keyword arguments:
            scenes_only -- bool: synchronize only "Normal" scenes.
            
        If scenes_only is True: synchronize only "Normal" scenes.
        If scenes_only is False: synchronize "Notes" scenes as well.            
        """
        super().__init__(filePath, **kwargs)
        self._scenesOnly = kwargs['scenes_only']

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Novel subclass instance to merge.
        
        Return a message beginning with the ERROR constant in case of error.
        Update date/time/duration from the source, if the scene title matches.
        Overrides the superclass mehod.
        """
        message = self.read()
        if message.startswith(ERROR):
            return message

        linkedCharacters = []
        linkedLocations = []
        linkedItems = []

        #--- Check the source for ambiguous titles.
        # Check scenes.
        srcScnTitles = []
        for scId in source.scenes:
            if source.scenes[scId].title in srcScnTitles:
                return f'{ERROR}Ambiguous Aeon event title "{source.scenes[scId].title}".'

            srcScnTitles.append(source.scenes[scId].title)

            # Collect characters, locations, and items assigned to normal scenes.
            if not source.scenes[scId].isNotesScene:
                if source.scenes[scId].characters:
                    linkedCharacters = list(set(linkedCharacters + source.scenes[scId].characters))
                if source.scenes[scId].locations:
                    linkedLocations = list(set(linkedLocations + source.scenes[scId].locations))
                if source.scenes[scId].items:
                    linkedItems = list(set(linkedItems + source.scenes[scId].items))

        # Check characters.
        srcChrNames = []
        for crId in source.characters:
            if not crId in linkedCharacters:
                continue

            if source.characters[crId].title in srcChrNames:
                return f'{ERROR}Ambiguous yWriter character "{source.characters[crId].title}".'

            srcChrNames.append(source.characters[crId].title)

        # Check locations.
        srcLocTitles = []
        for lcId in source.locations:
            if not lcId in linkedLocations:
                continue

            if source.locations[lcId].title in srcLocTitles:
                return f'{ERROR}Ambiguous yWriter location "{source.locations[lcId].title}".'

            srcLocTitles.append(source.locations[lcId].title)

        # Check items.
        srcItmTitles = []
        for itId in source.items:
            if not itId in linkedItems:
                continue

            if source.items[itId].title in srcItmTitles:
                return f'{ERROR}Ambiguous yWriter item "{source.items[itId].title}".'

            srcItmTitles.append(source.items[itId].title)

        #--- Analyze the target.
        # Check scenes.
        scIdMax = 0
        for scId in self.scenes:
            if int(scId) > scIdMax:
                scIdMax = int(scId)

            #--- Mark scenes associated with deleted events "Unused".
            if not self.scenes[scId].title in srcScnTitles:
                if not self.scenes[scId].isNotesScene:
                    self.scenes[scId].isUnused = True

        # Create a chapter for new scenes.
        chIdMax = 0
        for chId in self.chapters:
            if int(chId) > chIdMax:
                chIdMax = int(chId)
        newChapterId = str(chIdMax + 1)
        newChapter = self.CHAPTER_CLASS()
        newChapter.title = 'New scenes'
        newChapterExists = False

        #--- Check the target for ambiguous titles.
        # Check scenes.
        scIdsByTitle = {}
        for chId in self.chapters:
            for scId in self.chapters[chId].srtScenes:
                if self.scenes[scId].isUnused and not self.scenes[scId].isNotesScene:
                    continue

                if self.scenes[scId].title in scIdsByTitle:
                    return f'{ERROR}Ambiguous yWriter scene title "{self.scenes[scId].title}".'

                scIdsByTitle[self.scenes[scId].title] = scId

        # Check characters.
        crIdsByName = {}
        crIdMax = 0
        for crId in self.characters:
            if int(crId) > crIdMax:
                crIdMax = int(crId)
            if self.characters[crId].title in crIdsByName:
                return f'{ERROR}Ambiguous yWriter character "{self.characters[crId].title}".'

            crIdsByName[self.characters[crId].title] = crId

        # Check locations.
        lcIdsByTitle = {}
        lcIdMax = 0
        for lcId in self.locations:
            if int(lcId) > lcIdMax:
                lcIdMax = int(lcId)
            if self.locations[lcId].title in lcIdsByTitle:
                return f'{ERROR}Ambiguous yWriter location "{self.locations[lcId].title}".'

            lcIdsByTitle[self.locations[lcId].title] = lcId

        # Check items.
        itIdsByTitle = {}
        itIdMax = 0
        for itId in self.items:
            if int(itId) > itIdMax:
                itIdMax = int(itId)
            if self.items[itId].title in itIdsByTitle:
                return f'{ERROR}Ambiguous yWriter item "{self.items[itId].title}".'

            itIdsByTitle[self.items[itId].title] = itId

        #--- Update characters from the source.
        crIdsBySrcId = {}
        for srcCrId in source.characters:
            if source.characters[srcCrId].title in crIdsByName:
                crIdsBySrcId[srcCrId] = crIdsByName[source.characters[srcCrId].title]
            elif srcCrId in linkedCharacters:
                #--- Create a new character if it is assigned to at least one scene.
                crIdMax += 1
                crId = str(crIdMax)
                crIdsBySrcId[srcCrId] = crId
                self.characters[crId] = source.characters[srcCrId]
                self.srtCharacters.append(crId)

        #--- Update locations from the source.
        lcIdsBySrcId = {}
        for srcLcId in source.locations:
            if source.locations[srcLcId].title in lcIdsByTitle:
                lcIdsBySrcId[srcLcId] = lcIdsByTitle[source.locations[srcLcId].title]
            elif srcLcId in linkedLocations:
                #--- Create a new location if it is assigned to at least one scene.
                lcIdMax += 1
                lcId = str(lcIdMax)
                lcIdsBySrcId[srcLcId] = lcId
                self.locations[lcId] = source.locations[srcLcId]
                self.srtLocations.append(lcId)

        #--- Update Items from the source.
        itIdsBySrcId = {}
        for srcItId in source.items:
            if source.items[srcItId].title in itIdsByTitle:
                itIdsBySrcId[srcItId] = itIdsByTitle[source.items[srcItId].title]
            elif srcItId in linkedItems:
                #--- Create a new Item if it is assigned to at least one scene.
                itIdMax += 1
                itId = str(itIdMax)
                itIdsBySrcId[srcItId] = itId
                self.items[itId] = source.items[srcItId]
                self.srtItems.append(itId)

        #--- Update scenes from the source.
        for chId in source.chapters:
            if source.chapters[chId].isTrash:
                continue

            for srcId in source.chapters[chId].srtScenes:
                if source.scenes[srcId].isNotesScene and self._scenesOnly:
                    # Make "non-Narative" event a "Notes" scene.
                    if source.scenes[srcId].title in scIdsByTitle:
                        scId = scIdsByTitle[source.scenes[srcId].title]
                        self.scenes[scId].isNotesScene = True
                        self.scenes[scId].isUnused = True
                    continue

                if source.scenes[srcId].title in scIdsByTitle:
                    scId = scIdsByTitle[source.scenes[srcId].title]
                else:
                    #--- Create a new scene.
                    scIdMax += 1
                    scId = str(scIdMax)
                    self.scenes[scId] = self.SCENE_CLASS()
                    self.scenes[scId].title = source.scenes[srcId].title
                    self.scenes[scId].status = 1
                    if not newChapterExists:
                        self.chapters[newChapterId] = newChapter
                        self.srtChapters.append(newChapterId)
                        newChapterExists = True
                    self.chapters[newChapterId].srtScenes.append(scId)

                #--- Update scene type.
                self.scenes[scId].isNotesScene = source.scenes[srcId].isNotesScene
                self.scenes[scId].isUnused = source.scenes[srcId].isUnused

                #--- Update scene start date/time.
                self.scenes[scId].date = source.scenes[srcId].date
                self.scenes[scId].time = source.scenes[srcId].time

                #--- Update scene duration.
                self.scenes[scId].lastsMinutes = source.scenes[srcId].lastsMinutes
                self.scenes[scId].lastsHours = source.scenes[srcId].lastsHours
                self.scenes[scId].lastsDays = source.scenes[srcId].lastsDays

                #--- Update scene tags.
                if source.scenes[srcId].tags is not None:
                    self.scenes[scId].tags = source.scenes[srcId].tags

                #--- Update scene description.
                if source.scenes[srcId].desc is not None:
                    self.scenes[scId].desc = source.scenes[srcId].desc

                #--- Append event notes to scene notes.
                if source.scenes[srcId].sceneNotes is not None:
                    if self.scenes[scId].sceneNotes is not None:
                        if not source.scenes[srcId].sceneNotes in self.scenes[scId].sceneNotes:
                            self.scenes[scId].sceneNotes = f'{self.scenes[scId].sceneNotes}\n{source.scenes[srcId].sceneNotes}'
                    else:
                        self.scenes[scId].sceneNotes = source.scenes[srcId].sceneNotes

                #--- Update scene characters.
                if source.scenes[srcId].characters is not None:
                    try:
                        viewpoint = self.scenes[scId].characters[0]
                    except IndexError:
                        viewpoint = ''
                    if viewpoint in crIdsBySrcId.values():
                        self.scenes[scId].characters = [viewpoint]
                    else:
                        self.scenes[scId].characters = []
                    for crId in source.scenes[srcId].characters:
                        try:
                            if not crIdsBySrcId[crId] in self.scenes[scId].characters:
                                self.scenes[scId].characters.append(crIdsBySrcId[crId])
                        except IndexError:
                            pass

                #--- Update scene locations.
                if source.scenes[srcId].locations is not None:
                    self.scenes[scId].locations = []
                    for lcId in source.scenes[srcId].locations:
                        if lcId in lcIdsBySrcId:
                            self.scenes[scId].locations.append(lcIdsBySrcId[lcId])

                #--- Update scene items.
                if source.scenes[srcId].items is not None:
                    self.scenes[scId].items = []
                    for itId in source.scenes[srcId].items:
                        if itId in itIdsBySrcId:
                            self.scenes[scId].items.append(itIdsBySrcId[itId])

                #--- Update scene keyword variables.
                for fieldName in self._SCN_KWVAR:
                    try:
                        self.scenes[scId].kwVar[fieldName] = source.scenes[srcId].kwVar[fieldName]
                    except:
                        pass

        return 'Novel updated from timeline data.'


class Yw7Source(Yw7File):
    """yWriter 7 project file representation.
    Extend the superclass
    """
    _SCN_KWVAR = (
        'Field_SceneArcs',
        )



class Aeon2Converter(YwCnvUi):
    """A converter class for yWriter and Aeon Timeline 2.
    
    Public methods:
        run(sourcePath, **kwargs) -- Create source and target objects and run conversion.
    """

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath -- str: the source file path.
        
        The direction of the conversion is determined by the source file type.
        Only yWriter project files and Aeon Timeline 2 files are accepted.
        """
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'{ERROR}{_("File not found")}: "{os.path.normpath(sourcePath)}".')
            return

        fileName, fileExtension = os.path.splitext(sourcePath)
        if fileExtension == JsonTimeline2.EXTENSION:
            # Source is a timeline
            sourceFile = JsonTimeline2(sourcePath, **kwargs)
            if os.path.isfile(f'{fileName}{Yw7Source.EXTENSION}'):
                # Update existing yWriter project from timeline
                targetFile = Yw7Target(f'{fileName}{Yw7Target.EXTENSION}', **kwargs)
                sourceFile.ywProject = targetFile
                self.import_to_yw(sourceFile, targetFile)
            else:
                # Create new yWriter project from timeline
                targetFile = Yw7Source(f'{fileName}{Yw7Source.EXTENSION}', **kwargs)
                self.create_yw7(sourceFile, targetFile)
        elif fileExtension == Yw7Source.EXTENSION:
            # Update existing timeline from yWriter project
            sourceFile = Yw7Source(sourcePath, **kwargs)
            targetFile = JsonTimeline2(f'{fileName}{JsonTimeline2.EXTENSION}', **kwargs)
            self.export_from_yw(sourceFile, targetFile)
        else:
            # Source file format is not supported
            self.ui.set_info_how(f'{ERROR}{_("File type is not supported")}: "{os.path.normpath(sourcePath)}".')
            return

SUFFIX = ''
APPNAME = 'aeon2yw'
SETTINGS = dict(
    narrative_arc='Narrative',
    property_description='Description',
    property_notes='Notes',
    role_location='Location',
    role_item='Item',
    role_character='Participant',
    type_character='Character',
    type_location='Location',
    type_item='Item',
    color_scene='Red',
    color_event='Yellow',
)
OPTIONS = dict(
    scenes_only=True,
    add_moonphase=False,
)


def run(sourcePath, silentMode=True, installDir='.'):
    if silentMode:
        ui = Ui('')
    else:
        ui = UiTk('Synchronize Aeon Timeline 2 and yWriter @release')

    #--- Try to get persistent configuration data
    sourceDir = os.path.dirname(sourcePath)
    if not sourceDir:
        sourceDir = '.'
    iniFileName = f'{APPNAME}.ini'
    iniFiles = [f'{installDir}/{iniFileName}', f'{sourceDir}/{iniFileName}']
    configuration = Configuration(SETTINGS, OPTIONS)
    for iniFile in iniFiles:
        configuration.read(iniFile)
    kwargs = {'suffix': SUFFIX}
    kwargs.update(configuration.settings)
    kwargs.update(configuration.options)
    converter = Aeon2Converter()
    converter.ui = ui
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Synchronize Aeon Timeline 2 and yWriter',
        epilog='')
    parser.add_argument('sourcePath',
                        metavar='Sourcefile',
                        help='The path of the aeonzip or yw7 file.')

    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    args = parser.parse_args()
    try:
        homeDir = str(Path.home()).replace('\\', '/')
        installDir = f'{homeDir}/.pywriter/{APPNAME}/config'
    except:
        installDir = '.'
    run(args.sourcePath, args.silent, installDir)