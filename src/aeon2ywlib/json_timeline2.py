"""Provide a class for Aeon Timeline 2 JSON representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from datetime import datetime
from datetime import timedelta
from pywriter.pywriter_globals import ERROR
from pywriter.model.novel import Novel
from aeon2ywlib.aeon2_fop import open_timeline
from aeon2ywlib.aeon2_fop import save_timeline
from aeon2ywlib.uid_helper import get_uid
from aeon2ywlib.moonphase import get_moon_phase_plus


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
