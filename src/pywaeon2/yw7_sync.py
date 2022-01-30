"""Provide a class for a yWriter7 project to get updates from Aeon Timeline 2.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.pywriter_globals import ERROR
from pywriter.yw.yw7_file import Yw7File
from pywriter.model.chapter import Chapter
from pywriter.model.scene import Scene


class Yw7Sync(Yw7File):
    """yWriter 7 project file representation.
    Extend the superclass
    """

    def __init__(self, filePath, **kwargs):
        """Extend the superclass constructor,
        defining instance variables.
        """
        super().__init__(filePath, **kwargs)
        self.scenesOnly = kwargs['scenes_only']

    def merge(self, source):
        """Update date/time/duration from the source,
        if the scene title matches.
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

            else:
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

            if source.characters[crId].fullName in srcChrNames:
                return f'{ERROR}Ambiguous yWriter character "{source.characters[crId].fullName}".'

            else:
                srcChrNames.append(source.characters[crId].fullName)

        # Check locations.

        srcLocTitles = []

        for lcId in source.locations:

            if not lcId in linkedLocations:
                continue

            if source.locations[lcId].title in srcLocTitles:
                return f'{ERROR}Ambiguous yWriter location "{source.locations[lcId].title}".'

            else:
                srcLocTitles.append(source.locations[lcId].title)

        # Check items.

        srcItmTitles = []

        for itId in source.items:

            if not itId in linkedItems:
                continue

            if source.items[itId].title in srcItmTitles:
                return f'{ERROR}Ambiguous yWriter item "{source.items[itId].title}".'

            else:
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
        newChapter = Chapter()
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

                else:
                    scIdsByTitle[self.scenes[scId].title] = scId

        # Check characters.

        crIdsByName = {}
        crIdMax = 0

        for crId in self.characters:

            if int(crId) > crIdMax:
                crIdMax = int(crId)

            if self.characters[crId].fullName in crIdsByName:
                return f'{ERROR}Ambiguous yWriter character "{self.characters[crId].fullName}".'

            else:
                crIdsByName[self.characters[crId].fullName] = crId

        # Check locations.

        lcIdsByTitle = {}
        lcIdMax = 0

        for lcId in self.locations:

            if int(lcId) > lcIdMax:
                lcIdMax = int(lcId)

            if self.locations[lcId].title in lcIdsByTitle:
                return f'{ERROR}Ambiguous yWriter location "{self.locations[lcId].title}".'

            else:
                lcIdsByTitle[self.locations[lcId].title] = lcId

        # Check items.

        itIdsByTitle = {}
        itIdMax = 0

        for itId in self.items:

            if int(itId) > itIdMax:
                itIdMax = int(itId)

            if self.items[itId].title in itIdsByTitle:
                return f'{ERROR}Ambiguous yWriter item "{self.items[itId].title}".'

            else:
                itIdsByTitle[self.items[itId].title] = itId

        #--- Update characters from the source.

        crIdsBySrcId = {}

        for srcCrId in source.characters:

            if source.characters[srcCrId].fullName in crIdsByName:
                crIdsBySrcId[srcCrId] = crIdsByName[source.characters[srcCrId].fullName]

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

                if source.scenes[srcId].isNotesScene and self.scenesOnly:

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
                    self.scenes[scId] = Scene()
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

        return 'Novel updated from timeline data.'
