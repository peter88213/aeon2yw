"""Provide a class for csv timeline representation.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/paeon
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import csv

from pywriter.file.file_export import FileExport
from pywriter.model.scene import Scene
from pywriter.model.chapter import Chapter
from pywriter.model.world_element import WorldElement
from pywriter.model.character import Character


class CsvTimeline(FileExport):
    """File representation of a csv file exported by Aeon Timeline 2. 

    Represents a csv file with a record per scene.
    - Records are separated by line breaks.
    - Data fields are delimited by the _SEPARATOR character.
    """

    EXTENSION = '.csv'
    DESCRIPTION = 'Timeline'
    SUFFIX = ''
    _SEPARATOR = ','

    # Events assigned to the "narrative arc" (case insensitive) become
    # regular scenes, the others become Notes scenes.

    def __init__(self, filePath, **kwargs):
        """Extend the superclass constructor,
        defining instance variables.
        """
        FileExport.__init__(self, filePath, **kwargs)
        self.sceneMarker = kwargs['sceneMarker']
        self.titleLabel = kwargs['titleLabel']
        self.sceneLabel = kwargs['sceneLabel']
        self.dateTimeLabel = kwargs['dateTimeLabel']
        self.descriptionLabel = kwargs['descriptionLabel']
        self.notesLabel = kwargs['notesLabel']
        self.tagLabel = kwargs['tagLabel']
        self.locationLabel = kwargs['locationLabel']
        self.itemLabel = kwargs['itemLabel']
        self.characterLabel = kwargs['characterLabel']

    def read(self):
        """Parse the csv file located at filePath, 
        fetching the Scene attributes contained.

        Create one single chapter containing all scenes.

        Return a message beginning with SUCCESS or ERROR.
        """
        self.locationCount = 0
        self.locIdsByTitle = {}
        # key = location title
        # value = location ID

        self.itemCount = 0
        self.itmIdsByTitle = {}
        # key = item title
        # value = item ID

        def get_lcIds(lcTitles):
            """Return a list of location IDs; Add new location to the project.
            """
            lcIds = []

            for lcTitle in lcTitles:

                if lcTitle in self.locIdsByTitle:
                    lcIds.append(self.locIdsByTitle[lcTitle])

                elif lcTitle:
                    # Add a new location to the project.

                    self.locationCount += 1
                    lcId = str(self.locationCount)
                    self.locIdsByTitle[lcTitle] = lcId
                    self.locations[lcId] = WorldElement()
                    self.locations[lcId].title = lcTitle
                    self.srtLocations.append(lcId)
                    lcIds.append(lcId)

                else:
                    return None

            return lcIds

        def get_itIds(itTitles):
            """Return a list of item IDs; Add new item to the project.
            """
            itIds = []

            for itTitle in itTitles:

                if itTitle in self.itmIdsByTitle:
                    itIds.append(self.itmIdsByTitle[itTitle])

                elif itTitle:
                    # Add a new item to the project.

                    self.itemCount += 1
                    itId = str(self.itemCount)
                    self.itmIdsByTitle[itTitle] = itId
                    self.items[itId] = WorldElement()
                    self.items[itId].title = itTitle
                    self.srtItems.append(itId)
                    itIds.append(itId)

                else:
                    return None

            return itIds

        self.characterCount = 0
        self.chrIdsByTitle = {}
        # key = character title
        # value = character ID

        def get_crIds(crTitles):
            """Return a list of character IDs; Add new characters to the project.
            """
            crIds = []

            for crTitle in crTitles:

                if crTitle in self.chrIdsByTitle:
                    crIds.append(self.chrIdsByTitle[crTitle])

                elif crTitle:
                    # Add a new character to the project.

                    self.characterCount += 1
                    crId = str(self.characterCount)
                    self.chrIdsByTitle[crTitle] = crId
                    self.characters[crId] = Character()
                    self.characters[crId].title = crTitle
                    self.srtCharacters.append(crId)
                    crIds.append(crId)

                else:
                    return None

            return crIds

        self.rows = []

        #--- Read the csv file.

        try:
            with open(self.filePath, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=self._SEPARATOR)

                chId = '1'
                self.chapters[chId] = Chapter()
                self.chapters[chId].title = 'Chapter 1'
                self.srtChapters = [chId]

                scIdsByDate = {}
                sceneCount = 0

                for row in reader:
                    sceneCount += 1
                    scId = str(sceneCount)
                    self.scenes[scId] = Scene()

                    self.scenes[scId].title = row[self.titleLabel]

                    if not row[self.dateTimeLabel] in scIdsByDate:
                        scIdsByDate[row[self.dateTimeLabel]] = []

                    scIdsByDate[row[self.dateTimeLabel]].append(scId)

                    dt = row[self.dateTimeLabel].split(' ')
                    self.scenes[scId].date = dt[0]
                    self.scenes[scId].time = dt[1]

                    if not self.sceneMarker in row[self.sceneLabel]:
                        self.scenes[scId].isNotesScene = True

                    if self.descriptionLabel in row:
                        self.scenes[scId].desc = row[self.descriptionLabel]

                    if self.notesLabel in row:
                        self.scenes[scId].sceneNotes = row[self.notesLabel]

                    if self.tagLabel in row and row[self.tagLabel] != '':
                        self.scenes[scId].tags = row[self.tagLabel].split(
                            '|')

                    if self.locationLabel in row:
                        self.scenes[scId].locations = get_lcIds(
                            row[self.locationLabel].split('|'))

                    if self.characterLabel in row:
                        self.scenes[scId].characters = get_crIds(
                            row[self.characterLabel].split('|'))

                    if self.itemLabel in row:
                        self.scenes[scId].items = get_itIds(
                            row[self.itemLabel].split('|'))

                    # Set scene status = "Outline".

                    self.scenes[scId].status = 1

        except(FileNotFoundError):
            return 'ERROR: "' + os.path.normpath(self.filePath) + '" not found.'

        except(KeyError):
            return 'ERROR: Wrong csv structure.'

        except:
            return 'ERROR: Can not parse "' + os.path.normpath(self.filePath) + '".'

        # Sort scenes by date/time

        srtScenes = sorted(scIdsByDate.items())

        for date, scList in srtScenes:

            for scId in scList:
                self.chapters[chId].srtScenes.append(scId)

        return 'SUCCESS: Data read from "' + os.path.normpath(self.filePath) + '".'
