"""Provide a class for a yWriter7 project to get 
scene date/time updates from Aeon Timeline 2.

yWriter version-specific file representations inherit from this class.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""

from pywriter.yw.yw7_file import Yw7File


class Yw7Sync(Yw7File):
    """yWriter 7 project file representation.
    Extend the superclass
    """

    def merge(self, source):
        """Update date/time/duration from the source,
        if the scene title matches.
        """
        message = self.read()

        if message.startswith('ERROR'):
            return message

        # Check the source for ambiguous titles.

        scIdsByTitles = {}

        for scId in source.scenes:

            if source.scenes[scId].title in scIdsByTitles:
                return 'ERROR: Ambiguous Aeon event title "' + source.scenes[scId].title + '".'

            else:
                scIdsByTitles[source.scenes[scId].title] = scId

        # Get scene titles.

        scIdsByTitles = {}

        for chId in self.chapters:

            if self.chapters[chId].isTrash:
                continue

            for scId in self.chapters[chId].srtScenes:

                if self.scenes[scId].isUnused and not self.scenes[scId].isNotesScene:
                    continue

                if self.scenes[scId].title in scIdsByTitles:
                    return 'ERROR: Ambiguous yWriter scene title "' + self.scenes[scId].title + '".'

                else:
                    scIdsByTitles[self.scenes[scId].title] = scId

        # Get date/time/duration from the source, if the scene title matches.

        for srcId in source.scenes:

            if source.scenes[srcId].title in scIdsByTitles:
                scId = scIdsByTitles[source.scenes[srcId].title]

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

                if source.scenes[srcId].lastsMinutes is not None:
                    self.scenes[scId].lastsMinutes = source.scenes[srcId].lastsMinutes

                if source.scenes[srcId].lastsHours is not None:
                    self.scenes[scId].lastsHours = source.scenes[srcId].lastsHours

                if source.scenes[srcId].lastsDays is not None:
                    self.scenes[scId].lastsDays = source.scenes[srcId].lastsDays

        return 'SUCCESS'
