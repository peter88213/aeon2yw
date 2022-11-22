"""Provide a class for a yWriter7 project to get updates from Aeon Timeline 2.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.pywriter_globals import *
from pywriter.model.novel import Novel
from pywriter.model.chapter import Chapter
from pywriter.model.scene import Scene
from pywriter.yw.yw7_file import Yw7File


class Yw7Target(Yw7File):
    """yWriter 7 project file representation.
    Extend the superclass
    """
    _SCN_KWVAR = [
        'Field_SceneArcs',
        ]
    _CRT_KWVAR = [
        'Field_BirthDate',
        'Field_DeathDate',
        ]

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

    def write(self):
        """Update instance variables from a source instance.
        
        Update date/time/duration from the source, if the scene title matches.
        Raise the "Error" exception in case of error. 
        Overrides the superclass mehod.
        """
        #--- Merge first.
        source = self.novel
        self.novel = Novel()
        self.read()
        linkedCharacters = []
        linkedLocations = []
        linkedItems = []

        #--- Check the source for ambiguous titles.
        # Check scenes.
        srcScnTitles = []
        for scId in source.scenes:
            if source.scenes[scId].title in srcScnTitles:
                raise Error(_('Ambiguous Aeon event title "{}".').format(source.scenes[scId].title))

            srcScnTitles.append(source.scenes[scId].title)

            # Collect characters, locations, and items assigned to normal scenes.
            if not source.scenes[scId].scType == 1:
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
                raise Error(_('Ambiguous Aeon character "{}".').format(source.characters[crId].title))

            srcChrNames.append(source.characters[crId].title)

        # Check locations.
        srcLocTitles = []
        for lcId in source.locations:
            if not lcId in linkedLocations:
                continue

            if source.locations[lcId].title in srcLocTitles:
                raise Error(_('Ambiguous Aeon location "{}".').format(source.locations[lcId].title))

            srcLocTitles.append(source.locations[lcId].title)

        # Check items.
        srcItmTitles = []
        for itId in source.items:
            if not itId in linkedItems:
                continue

            if source.items[itId].title in srcItmTitles:
                raise Error(_('Ambiguous Aeon item "{}".').format(source.items[itId].title))

            srcItmTitles.append(source.items[itId].title)

        #--- Analyze the target.
        # Check scenes.
        scIdMax = 0
        for scId in self.novel.scenes:
            if int(scId) > scIdMax:
                scIdMax = int(scId)

            #--- Mark scenes associated with deleted events "Unused".
            if not self.novel.scenes[scId].title in srcScnTitles:
                if not self.novel.scenes[scId].scType == 1:
                    self.novel.scenes[scId].scType = 3

        # Create a chapter for new scenes.
        chIdMax = 0
        for chId in self.novel.chapters:
            if int(chId) > chIdMax:
                chIdMax = int(chId)
        newChapterId = str(chIdMax + 1)
        newChapter = Chapter()
        newChapter.title = 'New scenes'
        newChapterExists = False

        #--- Check the target for ambiguous titles.
        # Check scenes.
        scIdsByTitle = {}
        for chId in self.novel.chapters:
            for scId in self.novel.chapters[chId].srtScenes:
                if self.novel.scenes[scId].scType == 3:
                    continue

                if self.novel.scenes[scId].title in scIdsByTitle:
                    raise Error(_('Ambiguous yWriter scene title "{}".').format(self.novel.scenes[scId].title))

                scIdsByTitle[self.novel.scenes[scId].title] = scId

        # Check characters.
        crIdsByName = {}
        crIdMax = 0
        for crId in self.novel.characters:
            if int(crId) > crIdMax:
                crIdMax = int(crId)
            if self.novel.characters[crId].title in crIdsByName:
                raise Error(_('Ambiguous yWriter character "{}".').format(self.novel.characters[crId].title))

            crIdsByName[self.novel.characters[crId].title] = crId

        # Check locations.
        lcIdsByTitle = {}
        lcIdMax = 0
        for lcId in self.novel.locations:
            if int(lcId) > lcIdMax:
                lcIdMax = int(lcId)
            if self.novel.locations[lcId].title in lcIdsByTitle:
                raise Error(_('Ambiguous yWriter location "{}".').format(self.novel.locations[lcId].title))

            lcIdsByTitle[self.novel.locations[lcId].title] = lcId

        # Check items.
        itIdsByTitle = {}
        itIdMax = 0
        for itId in self.novel.items:
            if int(itId) > itIdMax:
                itIdMax = int(itId)
            if self.novel.items[itId].title in itIdsByTitle:
                raise Error(_('Ambiguous yWriter item "{}".').format(self.novel.items[itId].title))

            itIdsByTitle[self.novel.items[itId].title] = itId

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
                self.novel.characters[crId] = source.characters[srcCrId]
                self.novel.srtCharacters.append(crId)

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
                self.novel.locations[lcId] = source.locations[srcLcId]
                self.novel.srtLocations.append(lcId)

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
                self.novel.items[itId] = source.items[srcItId]
                self.novel.srtItems.append(itId)

        #--- Update scenes from the source.
        for chId in source.chapters:
            if source.chapters[chId].isTrash:
                continue

            for srcId in source.chapters[chId].srtScenes:
                if source.scenes[srcId].scType == 1 and self._scenesOnly:
                    # Make "non-Narative" event a "Notes" scene.
                    if source.scenes[srcId].title in scIdsByTitle:
                        scId = scIdsByTitle[source.scenes[srcId].title]
                        self.novel.scenes[scId].scType = 1
                    continue

                if source.scenes[srcId].title in scIdsByTitle:
                    scId = scIdsByTitle[source.scenes[srcId].title]
                else:
                    #--- Create a new scene.
                    scIdMax += 1
                    scId = str(scIdMax)
                    self.novel.scenes[scId] = Scene()
                    self.novel.scenes[scId].title = source.scenes[srcId].title
                    self.novel.scenes[scId].status = 1
                    if not newChapterExists:
                        self.novel.chapters[newChapterId] = newChapter
                        self.novel.srtChapters.append(newChapterId)
                        newChapterExists = True
                    self.novel.chapters[newChapterId].srtScenes.append(scId)

                #--- Update scene type.
                self.novel.scenes[scId].scType = source.scenes[srcId].scType

                #--- Update scene start date/time.
                self.novel.scenes[scId].date = source.scenes[srcId].date
                self.novel.scenes[scId].time = source.scenes[srcId].time

                #--- Update scene duration.
                self.novel.scenes[scId].lastsMinutes = source.scenes[srcId].lastsMinutes
                self.novel.scenes[scId].lastsHours = source.scenes[srcId].lastsHours
                self.novel.scenes[scId].lastsDays = source.scenes[srcId].lastsDays

                #--- Update scene tags.
                if source.scenes[srcId].tags is not None:
                    self.novel.scenes[scId].tags = source.scenes[srcId].tags

                #--- Update scene description.
                if source.scenes[srcId].desc is not None:
                    self.novel.scenes[scId].desc = source.scenes[srcId].desc

                #--- Append event notes to scene notes.
                if source.scenes[srcId].notes is not None:
                    if self.novel.scenes[scId].notes is not None:
                        if not source.scenes[srcId].notes in self.novel.scenes[scId].notes:
                            self.novel.scenes[scId].notes = f'{self.novel.scenes[scId].notes}\n{source.scenes[srcId].notes}'
                    else:
                        self.novel.scenes[scId].notes = source.scenes[srcId].notes

                #--- Update scene characters.
                if source.scenes[srcId].characters is not None:
                    try:
                        viewpoint = self.novel.scenes[scId].characters[0]
                    except:
                        viewpoint = ''
                    if viewpoint in crIdsBySrcId.values():
                        self.novel.scenes[scId].characters = [viewpoint]
                    else:
                        self.novel.scenes[scId].characters = []
                    for crId in source.scenes[srcId].characters:
                        try:
                            if not crIdsBySrcId[crId] in self.novel.scenes[scId].characters:
                                self.novel.scenes[scId].characters.append(crIdsBySrcId[crId])
                        except:
                            pass

                #--- Update scene locations.
                if source.scenes[srcId].locations is not None:
                    self.novel.scenes[scId].locations = []
                    for lcId in source.scenes[srcId].locations:
                        if lcId in lcIdsBySrcId:
                            self.novel.scenes[scId].locations.append(lcIdsBySrcId[lcId])

                #--- Update scene items.
                if source.scenes[srcId].items is not None:
                    self.novel.scenes[scId].items = []
                    for itId in source.scenes[srcId].items:
                        if itId in itIdsBySrcId:
                            self.novel.scenes[scId].items.append(itIdsBySrcId[itId])

                #--- Update scene keyword variables.
                for fieldName in self._SCN_KWVAR:
                    try:
                        self.novel.scenes[scId].kwVar[fieldName] = source.scenes[srcId].kwVar[fieldName]
                    except:
                        pass

        super().write()

