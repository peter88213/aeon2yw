"""Provide a class for Aeon Timeline 2 JSON representation.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from datetime import datetime
from datetime import timedelta

from pywriter.model.novel import Novel
from pywriter.model.scene import Scene
from pywriter.model.chapter import Chapter
from pywriter.model.world_element import WorldElement
from pywriter.model.character import Character

from pywaeon2.aeon2_fop import open_timeline
from pywaeon2.aeon2_fop import save_timeline
from pywaeon2.uid_helper import get_uid


class JsonTimeline2(Novel):
    """File representation of an Aeon Timeline 2 project. 
    Represents the .aeonzip file containing 'timeline.json'.
    """

    EXTENSION = '.aeonzip'
    DESCRIPTION = 'Aeon Timeline 2 project'
    SUFFIX = ''

    VALUE_YES = '1'
    # JSON representation of "yes" in Aeon2 "yes/no" properties

    DATE_LIMIT = (datetime(100, 1, 1) - datetime.min).total_seconds()
    # Dates before 100-01-01 can not be displayed properly in yWriter

    DEFAULT_TIMESTAMP = (datetime.now() - datetime.min).total_seconds()

    def __init__(self, filePath, **kwargs):
        """Extend the superclass constructor,
        defining instance variables.
        """
        Novel.__init__(self, filePath, **kwargs)

        self.jsonData = None

        # JSON[entities][name]

        self.entityNarrative = kwargs['narrative_arc']

        # JSON[template][properties][name]

        self.propertyDesc = kwargs['property_description']
        self.propertyNotes = kwargs['property_notes']

        # JSON[template][types][name][roles]

        self.roleLocation = kwargs['role_location']
        self.roleItem = kwargs['role_item']
        self.roleCharacter = kwargs['role_character']

        # JSON[template][types][name]

        self.typeCharacter = kwargs['type_character']
        self.typeLocation = kwargs['type_location']
        self.typeItem = kwargs['type_item']

        # GUIDs

        self.tplDateGuid = None
        self.typeArcGuid = None
        self.typeCharacterGuid = None
        self.typeLocationGuid = None
        self.typeItemGuid = None
        self.roleArcGuid = None
        self.roleCharacterGuid = None
        self.roleLocationGuid = None
        self.roleItemGuid = None
        self.entityNarrativeGuid = None
        self.propertyDescGuid = None
        self.propertyNotesGuid = None

        # Miscellaneous

        self.scenesOnly = kwargs['scenes_only']
        self.sceneColor = kwargs['color_scene']
        self.eventColor = kwargs['color_event']
        self.majorCharactersOnly = kwargs['major_characters_only']
        self.timestampMax = 0
        self.displayIdMax = 0.0
        self.colors = {}
        self.arcCount = 0
        self.characterGuidById = {}
        self.locationGuidById = {}
        self.itemGuidById = {}

    def read(self):
        """Read the JSON part of the Aeon Timeline 2 file located at filePath, 
        and build a yWriter novel structure.
        - Events marked as scenes are converted to scenes in one single chapter.
        - Other events are converted to “Notes” scenes in another chapter.
        Return a message beginning with SUCCESS or ERROR.
        Override the superclass method.
        """

        message, self.jsonData = open_timeline(self.filePath)

        if message.startswith('ERROR'):
            return message

        #--- Get the color definitions.

        for tplCol in self.jsonData['template']['colors']:
            self.colors[tplCol['name']] = tplCol['guid']

        #--- Get the date definition.

        for tplRgp in self.jsonData['template']['rangeProperties']:

            if tplRgp['type'] == 'date':

                for tplRgpCalEra in tplRgp['calendar']['eras']:

                    if tplRgpCalEra['name'] == 'AD':
                        self.tplDateGuid = tplRgp['guid']
                        break

        if self.tplDateGuid is None:
            return 'ERROR: "AD" era is missing in the calendar.'

        #--- Get GUID of user defined types and roles.

        for tplTyp in self.jsonData['template']['types']:

            if tplTyp['name'] == 'Arc':
                self.typeArcGuid = tplTyp['guid']

                for tplTypRol in tplTyp['roles']:

                    if tplTypRol['name'] == 'Arc':
                        self.roleArcGuid = tplTypRol['guid']

            elif tplTyp['name'] == self.typeCharacter:
                self.typeCharacterGuid = tplTyp['guid']

                for tplTypRol in tplTyp['roles']:

                    if tplTypRol['name'] == self.roleCharacter:
                        self.roleCharacterGuid = tplTypRol['guid']

            elif tplTyp['name'] == self.typeLocation:
                self.typeLocationGuid = tplTyp['guid']

                for tplTypRol in tplTyp['roles']:

                    if tplTypRol['name'] == self.roleLocation:
                        self.roleLocationGuid = tplTypRol['guid']
                        break

            elif tplTyp['name'] == self.typeItem:
                self.typeItemGuid = tplTyp['guid']

                for tplTypRol in tplTyp['roles']:

                    if tplTypRol['name'] == self.roleItem:
                        self.roleItemGuid = tplTypRol['guid']
                        break

        #--- Add "Arc" type, if missing.

        if self.typeArcGuid is None:
            self.typeArcGuid = get_uid()
            self.roleArcGuid = get_uid()
            typeCount = len(self.jsonData['template']['types'])
            self.jsonData['template']['types'].append(
                {
                    'color': 'iconYellow',
                    'guid': self.typeArcGuid,
                    'icon': 'book',
                    'name': 'Arc',
                    'persistent': True,
                    'roles': [
                        {
                            'allowsMultipleForEntity': True,
                            'allowsMultipleForEvent': True,
                            'allowsPercentAllocated': False,
                            'guid': self.roleArcGuid,
                            'icon': 'circle text',
                            'mandatoryForEntity': False,
                            'mandatoryForEvent': False,
                            'name': 'Arc',
                            'sortOrder': 0
                        }
                    ],
                    'sortOrder': typeCount
                })

        #--- Add "Character" type, if missing.

        if self.typeCharacterGuid is None:
            self.typeCharacterGuid = get_uid()
            self.roleCharacterGuid = get_uid()
            typeCount = len(self.jsonData['template']['types'])
            self.jsonData['template']['types'].append(
                {
                    'color': 'iconRed',
                    'guid': self.typeCharacterGuid,
                    'icon': 'person',
                    'name': self.typeCharacter,
                    'persistent': False,
                    'roles': [
                        {
                            'allowsMultipleForEntity': True,
                            'allowsMultipleForEvent': True,
                            'allowsPercentAllocated': False,
                            'guid': self.roleCharacterGuid,
                            'icon': 'circle text',
                            'mandatoryForEntity': False,
                            'mandatoryForEvent': False,
                            'name': self.roleCharacter,
                            'sortOrder': 0
                        }
                    ],
                    'sortOrder': typeCount
                })

        #--- Add "Location" type, if missing.

        if self.typeLocationGuid is None:
            self.typeLocationGuid = get_uid()
            self.roleLocationGuid = get_uid()
            typeCount = len(self.jsonData['template']['types'])
            self.jsonData['template']['types'].append(
                {
                    'color': 'iconOrange',
                    'guid': self.typeLocationGuid,
                    'icon': 'map',
                    'name': self.typeLocation,
                    'persistent': True,
                    'roles': [
                        {
                            'allowsMultipleForEntity': True,
                            'allowsMultipleForEvent': True,
                            'allowsPercentAllocated': False,
                            'guid': self.roleLocationGuid,
                            'icon': 'circle text',
                            'mandatoryForEntity': False,
                            'mandatoryForEvent': False,
                            'name': self.roleLocation,
                            'sortOrder': 0
                        }
                    ],
                    'sortOrder': typeCount
                })

        #--- Add "Item" type, if missing.

        if self.typeItemGuid is None:
            self.typeItemGuid = get_uid()
            self.roleItemGuid = get_uid()
            typeCount = len(self.jsonData['template']['types'])
            self.jsonData['template']['types'].append(
                {
                    'color': 'iconPurple',
                    'guid': self.typeItemGuid,
                    'icon': 'cube',
                    'name': self.typeItem,
                    'persistent': True,
                    'roles': [
                        {
                            'allowsMultipleForEntity': True,
                            'allowsMultipleForEvent': True,
                            'allowsPercentAllocated': False,
                            'guid': self.roleItemGuid,
                            'icon': 'circle text',
                            'mandatoryForEntity': False,
                            'mandatoryForEvent': False,
                            'name': self.roleItem,
                            'sortOrder': 0
                        }
                    ],
                    'sortOrder': typeCount
                })

        #--- Get characters, locations, and items.

        crIdsByGuid = {}
        lcIdsByGuid = {}
        itIdsByGuid = {}
        characterCount = 0
        locationCount = 0
        itemCount = 0

        for ent in self.jsonData['entities']:

            if ent['entityType'] == self.typeArcGuid:
                self.arcCount += 1

                if ent['name'] == self.entityNarrative:
                    self.entityNarrativeGuid = ent['guid']

            elif ent['entityType'] == self.typeCharacterGuid:
                characterCount += 1
                crId = str(characterCount)
                crIdsByGuid[ent['guid']] = crId
                self.characters[crId] = Character()
                self.characters[crId].title = ent['name']
                self.characters[crId].fullName = ent['name']
                self.characterGuidById[crId] = ent['guid']

                if ent['notes']:
                    self.characters[crId].notes = ent['notes']

                else:
                    ent['notes'] = ''

                self.srtCharacters.append(crId)

            elif ent['entityType'] == self.typeLocationGuid:
                locationCount += 1
                lcId = str(locationCount)
                lcIdsByGuid[ent['guid']] = lcId
                self.locations[lcId] = WorldElement()
                self.locations[lcId].title = ent['name']
                self.srtLocations.append(lcId)
                self.locationGuidById[lcId] = ent['guid']

            elif ent['entityType'] == self.typeItemGuid:
                itemCount += 1
                itId = str(itemCount)
                itIdsByGuid[ent['guid']] = itId
                self.items[itId] = WorldElement()
                self.items[itId].title = ent['name']
                self.srtItems.append(itId)
                self.itemGuidById[itId] = ent['guid']

        #--- Get GUID of user defined properties.

        hasPropertyNotes = False
        hasPropertyDesc = False

        for tplPrp in self.jsonData['template']['properties']:

            if tplPrp['name'] == self.propertyDesc:
                self.propertyDescGuid = tplPrp['guid']
                hasPropertyDesc = True

            elif tplPrp['name'] == self.propertyNotes:
                self.propertyNotesGuid = tplPrp['guid']
                hasPropertyNotes = True

        #--- Create user defined properties, if missing.

        if not hasPropertyNotes:
            self.propertyNotesGuid = get_uid()
            self.jsonData['template']['properties'].insert(0, {
                'calcMode': 'default',
                'calculate': False,
                'fadeEvents': False,
                'guid': self.propertyNotesGuid,
                'icon': 'tag',
                'isMandatory': False,
                'name': 'Notes',
                'sortOrder': 0,
                'type': 'multitext'
            })

            i = 0

            for tplPrp in self.jsonData['template']['properties']:
                tplPrp['sortOrder'] = i
                i += 1

        if not hasPropertyDesc:
            self.propertyDescGuid = get_uid()
            self.jsonData['template']['properties'].append({
                'calcMode': 'default',
                'calculate': False,
                'fadeEvents': False,
                'guid': self.propertyDescGuid,
                'icon': 'tag',
                'isMandatory': False,
                'name': 'Description',
                'sortOrder': 1,
                'type': 'multitext'
            })

            i = 0

            for tplPrp in self.jsonData['template']['properties']:
                tplPrp['sortOrder'] = i
                i += 1

        #--- Get scenes.

        eventCount = 0
        scIdsByDate = {}

        for evt in self.jsonData['events']:
            eventCount += 1
            scId = str(eventCount)
            self.scenes[scId] = Scene()
            self.scenes[scId].title = evt['title']

            displayId = float(evt['displayId'])

            if displayId > self.displayIdMax:
                self.displayIdMax = displayId

            # Set scene status = "Outline".

            self.scenes[scId].status = 1

            #--- Evaluate properties.

            hasDescription = False
            hasNotes = False

            for evtVal in evt['values']:

                # Get scene description.

                if evtVal['property'] == self.propertyDescGuid:
                    hasDescription = True

                    if evtVal['value']:
                        self.scenes[scId].desc = evtVal['value']

                # Get scene notes.

                elif evtVal['property'] == self.propertyNotesGuid:
                    hasNotes = True

                    if evtVal['value']:
                        self.scenes[scId].sceneNotes = evtVal['value']

            #--- Add description and scene notes, if missing.

            if not hasDescription:
                evt['values'].append({'property': self.propertyDescGuid, 'value': ''})

            if not hasNotes:
                evt['values'].append({'property': self.propertyNotesGuid, 'value': ''})

            #--- Get scene tags.

            if evt['tags']:

                if self.scenes[scId].tags is None:
                    self.scenes[scId].tags = []

                for evtTag in evt['tags']:
                    self.scenes[scId].tags.append(evtTag)

            #--- Get date/time/duration

            timestamp = 0

            for evtRgv in evt['rangeValues']:

                if evtRgv['rangeProperty'] == self.tplDateGuid:
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
                                endYear += evtRgv['span']['months'] // 12
                                endMonth += evtRgv['span']['months']

                                while endMonth > 12:
                                    endMonth -= 12

                            sceneEnd = datetime(endYear, endMonth, sceneStart.day)
                            sceneDuration = sceneEnd - sceneStart
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

                if evtRel['role'] == self.roleArcGuid:

                    # Make scene event "Normal" type scene.

                    if self.entityNarrativeGuid and evtRel['entity'] == self.entityNarrativeGuid:
                        self.scenes[scId].isNotesScene = False
                        self.scenes[scId].isUnused = False

                        if timestamp > self.timestampMax:
                            self.timestampMax = timestamp

                elif evtRel['role'] == self.roleCharacterGuid:

                    if self.scenes[scId].characters is None:
                        self.scenes[scId].characters = []

                    crId = crIdsByGuid[evtRel['entity']]
                    self.scenes[scId].characters.append(crId)

                elif evtRel['role'] == self.roleLocationGuid:

                    if self.scenes[scId].locations is None:
                        self.scenes[scId].locations = []

                    lcId = lcIdsByGuid[evtRel['entity']]
                    self.scenes[scId].locations.append(lcId)

                elif evtRel['role'] == self.roleItemGuid:

                    if self.scenes[scId].items is None:
                        self.scenes[scId].items = []

                    itId = itIdsByGuid[evtRel['entity']]
                    self.scenes[scId].items.append(itId)

        #--- Sort scenes by date/time and place them in chapters.

        chIdNarrative = '1'
        chIdBackground = '2'

        self.chapters[chIdNarrative] = Chapter()
        self.chapters[chIdNarrative].title = 'Chapter 1'
        self.chapters[chIdNarrative].chType = 0
        self.srtChapters.append(chIdNarrative)

        self.chapters[chIdBackground] = Chapter()
        self.chapters[chIdBackground].title = 'Background'
        self.chapters[chIdBackground].chType = 1
        self.srtChapters.append(chIdBackground)

        srtScenes = sorted(scIdsByDate.items())

        for date, scList in srtScenes:

            for scId in scList:

                if self.scenes[scId].isNotesScene:
                    self.chapters[chIdBackground].srtScenes.append(scId)

                else:
                    self.chapters[chIdNarrative].srtScenes.append(scId)

        if self.timestampMax == 0:
            self.timestampMax = self.DEFAULT_TIMESTAMP

        return 'SUCCESS: Data read from "' + os.path.normpath(self.filePath) + '".'

    def merge(self, source):
        """Update date/time/duration from the source,
        if the scene title matches.
        """

        def get_display_id():
            self.displayIdMax += 1
            return str(int(self.displayIdMax))

        def build_event(scene):
            """Create a new event from a scene.
            """
            event = {
                'attachments': [],
                'color': '',
                'displayId': get_display_id(),
                'guid': get_uid(),
                'links': [],
                'locked': False,
                'priority': 500,
                'rangeValues': [{
                    'minimumZoom': -1,
                    'position': {
                        'precision': 'minute',
                        'timestamp': self.DATE_LIMIT
                    },
                    'rangeProperty': self.tplDateGuid,
                    'span': {},
                }],
                'relationships': [],
                'tags': [],
                'title': scene.title,
                'values': [{
                    'property': self.propertyNotesGuid,
                    'value': ''
                },
                    {
                    'property': self.propertyDescGuid,
                    'value': ''
                }],
            }

            if scene.isNotesScene:
                event['color'] = self.colors[self.eventColor]

            else:
                event['color'] = self.colors[self.sceneColor]

            return event

        message = self.read()

        if message.startswith('ERROR'):
            return message

        #--- Check the source for ambiguous titles.

        srcTitles = []

        for chId in source.chapters:

            if source.chapters[chId].isTrash:
                continue

            for scId in source.chapters[chId].srtScenes:

                if source.scenes[scId].isUnused and not source.scenes[scId].isNotesScene:
                    continue

                if source.scenes[scId].title in srcTitles:
                    return 'ERROR: Ambiguous yWriter scene title "' + source.scenes[scId].title + '".'

                else:
                    srcTitles.append(source.scenes[scId].title)

        srcNames = []

        for crId in source.characters:

            if self.majorCharactersOnly and not source.characters[crId].isMajor:
                continue

            if not source.characters[crId].fullName:
                return 'ERROR: Character "' + source.characters[crId].title + '" has no full name.'

            if source.characters[crId].fullName in srcNames:
                return 'ERROR: Ambiguous yWriter character "' + source.characters[crId].fullName + '".'

            else:
                srcNames.append(source.characters[crId].fullName)

        #--- Check the target for ambiguous titles.

        scIdsByTitle = {}

        for scId in self.scenes:

            if self.scenes[scId].title in scIdsByTitle:
                return 'ERROR: Ambiguous Aeon event title "' + self.scenes[scId].title + '".'

            else:
                scIdsByTitle[self.scenes[scId].title] = scId

        crIdsByName = {}

        for crId in self.characters:

            if self.characters[crId].fullName in crIdsByName:
                return 'ERROR: Ambiguous Aeon character "' + self.characters[crId].fullName + '".'

            else:
                crIdsByName[self.characters[crId].fullName] = crId

        #--- Update characters from the source.

        totalCharacters = len(self.characters)
        crIdsBySrcId = {}

        for srcCrId in source.characters:

            if source.characters[srcCrId].fullName in crIdsByName:
                crIdsBySrcId[srcCrId] = crIdsByName[source.characters[srcCrId].fullName]

            elif not self.majorCharactersOnly or source.characters[srcCrId].isMajor:
                #--- Create a new character.

                totalCharacters += 1
                crId = str(totalCharacters)
                crIdsBySrcId[srcCrId] = crId
                self.characters[crId] = source.characters[srcCrId]
                newGuid = get_uid()
                self.characterGuidById[crId] = newGuid
                self.jsonData['entities'].append(
                    {
                        'entityType': self.typeCharacterGuid,
                        'guid': newGuid,
                        'icon': 'person',
                        'name': self.characters[crId].fullName,
                        'notes': '',
                        'sortOrder': totalCharacters - 1,
                        'swatchColor': 'darkPink'
                    })

        #--- Update scenes from the source.

        totalEvents = len(self.jsonData['events'])

        for chId in source.chapters:

            if source.chapters[chId].isTrash:
                continue

            for srcId in source.chapters[chId].srtScenes:

                if source.scenes[srcId].isUnused and not source.scenes[srcId].isNotesScene:
                    continue

                if source.scenes[srcId].isNotesScene and self.scenesOnly:
                    continue

                if source.scenes[srcId].title in scIdsByTitle:
                    scId = scIdsByTitle[source.scenes[srcId].title]

                else:
                    #--- Create a new scene.

                    totalEvents += 1
                    scId = str(totalEvents)
                    self.scenes[scId] = Scene()
                    self.scenes[scId].title = source.scenes[srcId].title
                    newEvent = build_event(self.scenes[scId])
                    self.jsonData['events'].append(newEvent)

                self.scenes[scId].status = source.scenes[srcId].status

                #--- Update scene type.

                if source.scenes[srcId].isNotesScene is not None:
                    self.scenes[scId].isNotesScene = source.scenes[srcId].isNotesScene

                if source.scenes[srcId].isUnused is not None:
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

        return 'SUCCESS'

    def write(self):
        """Write selected properties to the file.
        """
        def get_timestamp(scene):
            """Return a timestamp integer from the scene date.
            """
            timestamp = int(self.timestampMax)

            try:

                if scene.date:
                    isoDt = scene.date

                    if scene.time:
                        isoDt += (' ' + scene.time)

                timestamp = int((datetime.fromisoformat(isoDt) - datetime.min).total_seconds())

            except:
                pass

            return timestamp

        def get_span(scene):
            """Return a time span dictionary from the scene duration.
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

        if self.entityNarrativeGuid is None:
            self.entityNarrativeGuid = get_uid()
            self.jsonData['entities'].append(
                {
                    'entityType': self.typeArcGuid,
                    'guid': self.entityNarrativeGuid,
                    'icon': 'book',
                    'name': self.entityNarrative,
                    'notes': '',
                    'sortOrder': self.arcCount,
                    'swatchColor': 'orange'
                })

        narrativeArc = {
            'entity': self.entityNarrativeGuid,
            'percentAllocated': 1,
            'role': self.roleArcGuid,
        }

        #--- Update events from scenes.

        eventCount = 0

        for evt in self.jsonData['events']:
            eventCount += 1
            scId = str(eventCount)

            #--- Set event date/time/span.

            if evt['rangeValues'][0]['position']['timestamp'] >= self.DATE_LIMIT:
                evt['rangeValues'][0]['span'] = get_span(self.scenes[scId])
                evt['rangeValues'][0]['position']['timestamp'] = get_timestamp(self.scenes[scId])

            #--- Set scene description and notes.

            for evtVal in evt['values']:

                # Set scene description.

                if evtVal['property'] == self.propertyDescGuid:

                    if self.scenes[scId].desc:
                        evtVal['value'] = self.scenes[scId].desc

                # Set scene notes.

                elif evtVal['property'] == self.propertyNotesGuid:

                    if self.scenes[scId].sceneNotes:
                        evtVal['value'] = self.scenes[scId].sceneNotes

            #--- Set scene tags.

            if self.scenes[scId].tags:
                evt['tags'] = self.scenes[scId].tags

            #--- Update characters, locations, and items.

            newRel = []

            for evtRel in evt['relationships']:

                if evtRel['role'] == self.roleCharacterGuid:
                    continue

                elif evtRel['role'] == self.roleLocationGuid:
                    continue

                elif evtRel['role'] == self.roleItemGuid:
                    continue

                else:
                    newRel.append(evtRel)

            if self.scenes[scId].characters:

                for chId in self.scenes[scId].characters:

                    if self.scenes[scId].characters:
                        newRel.append(
                            {
                                'entity': self.characterGuidById[chId],
                                'percentAllocated': 1,
                                'role': self.roleCharacterGuid,
                            })

            evt['relationships'] = newRel

            #--- Assign "scene" events to the "Narrative" arc.

            if self.scenes[scId].isNotesScene:

                if narrativeArc in evt['relationships']:
                    evt['relationships'].remove(narrativeArc)

            elif narrativeArc not in evt['relationships']:
                evt['relationships'].append(narrativeArc)

        return save_timeline(self.jsonData, self.filePath)
