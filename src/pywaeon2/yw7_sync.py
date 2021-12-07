"""Provide a class for a yWriter7 project to get 
scene date/time updates from Aeon Timeline 2.

yWriter version-specific file representations inherit from this class.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""

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
        Yw7File.__init__(self, filePath, **kwargs)
        self.scenesOnly = kwargs['scenes_only']

    def merge(self, source):
        """Update date/time/duration from the source,
        if the scene title matches.
        """
        message = self.read()

        if message.startswith('ERROR'):
            return message

        # Check the source for ambiguous titles.

        srcScnTitles = []

        for scId in source.scenes:

            if source.scenes[scId].title in srcScnTitles:
                return 'ERROR: Ambiguous Aeon event title "' + source.scenes[scId].title + '".'

            else:
                srcScnTitles.append(source.scenes[scId].title)

        scIdMax = 0

        for scId in self.scenes:

            if int(scId) > scIdMax:
                scIdMax = int(scId)

        chIdMax = 0

        for chId in self.chapters:

            if int(chId) > chIdMax:
                chIdMax = int(chId)

        newChapterId = str(chIdMax + 1)
        newChapter = Chapter()
        newChapter.title = 'New scenes'
        newChapterExists = False

        # Get scene titles.

        scIdsByTitle = {}

        for chId in self.chapters:

            for scId in self.chapters[chId].srtScenes:

                if self.scenes[scId].isUnused and not self.scenes[scId].isNotesScene:
                    continue

                if self.scenes[scId].title in scIdsByTitle:
                    return 'ERROR: Ambiguous yWriter scene title "' + self.scenes[scId].title + '".'

                else:
                    scIdsByTitle[self.scenes[scId].title] = scId

        #--- Update data from the source, if the scene title matches.

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
                            self.scenes[scId].sceneNotes += ('\n' + source.scenes[srcId].sceneNotes)

                    else:
                        self.scenes[scId].sceneNotes = source.scenes[srcId].sceneNotes

        return 'SUCCESS'
