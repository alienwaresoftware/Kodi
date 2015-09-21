try:
    import xbmc
    import xbmcaddon
    import os
    import json
    import AlphaUIUtils
     
    __programlauncheraddon__ = xbmcaddon.Addon(id='plugin.program.aw.programlauncher')
    __programlauncheraddonprofile__ = xbmc.translatePath(__programlauncheraddon__.getAddonInfo('profile')).decode('utf-8')
    PROGRAMS_DB_PATH = os.path.join(__programlauncheraddonprofile__, "programs.db")

    CATEGORY_ALL = 4294967295
    CATEGORY_ADD = 1
    CATEGORY_PROGRAM = 2
    CATEGORY_VIDEO = 4
    CATEGORY_MUSIC = 8
    CATEGORY_IMAGE = 16

    TYPE_WIN32 = 1
    TYPE_WIN8 = 2
    TYPE_WEBSITE = 4
    TYPE_ADDON = 8

    class Program(object):
        def __init__(self, programId, name, category, type, path, parameter, thumbImage, fanartImage, isNameChanged,
                     isPathChanged, isIconChanged, isFanartChanged, addedToMainMenu=False, addedToSubMenu=False,
                     mouseKeyboardOnLoad=True, elevatePermission=False, startAtBoot=False):
            self.id = programId
            self.name = name
            self.category = category
            self.type = type
            self.path = path
            self.parameter = parameter
            self.thumbImage = thumbImage
            self.fanartImage = fanartImage
            self.isNameChanged = isNameChanged
            self.isPathChanged = isPathChanged
            self.isIconChanged = isIconChanged
            self.isFanartChanged = isFanartChanged
            self.addedToMainMenu = addedToMainMenu
            self.addedToSubMenu = addedToSubMenu
            self.mouseKeyboardOnLoad = mouseKeyboardOnLoad
            self.elevatePermission = elevatePermission
            self.startAtBoot = startAtBoot

    def getPrograms(programCategory):
        programs = []

        if (os.path.isfile(PROGRAMS_DB_PATH)):
            programsDBfile = open(PROGRAMS_DB_PATH, 'r')
            programsJson = json.loads(programsDBfile.read())
            programsDBfile.close()

            for program in programsJson:
                category = int(programsJson[program]['category'])
                if ((programCategory & category) == category):
                    programs.append(Program(program, programsJson[program]['name'], programsJson[program]['category'],
                                            programsJson[program]['type'], programsJson[program]['path'],
                                            programsJson[program]['parameter'], programsJson[program]['thumbImage'],
                                            programsJson[program]['fanartImage'], programsJson[program]['isNameChanged'],
                                            programsJson[program]['isPathChanged'], programsJson[program]['isIconChanged'],
                                            programsJson[program]['isFanartChanged'], mouseKeyboardOnLoad = programsJson[program]['mouseKeyboardOnLoad'] ,
                                            elevatePermission = programsJson[program]['elevatePermission'], startAtBoot = programsJson[program]['startAtBoot']))

        return programs

    if __name__ == '__main__':
        monitor = xbmc.Monitor()

        if not monitor.waitForAbort(3):
        
            programs = getPrograms(CATEGORY_ALL)

            if (programs):
                for program in programs:

                    if (program.type == TYPE_ADDON):
                        if(program.startAtBoot):

                            if(program.mouseKeyboardOnLoad):
                                AlphaUIUtils.EnableDisableControllerMouse(True)

                            xbmc.executebuiltin(program.path)

                    elif(program.type == TYPE_WIN32):
                        if(program.startAtBoot):
                            print(program.name + " : startAtBoot -> " + str(program.startAtBoot))
                            AlphaUIUtils.LaunchApplication(unicode(program.path), unicode(os.path.dirname(program.path)),unicode(""), program.elevatePermission, program.mouseKeyboardOnLoad, program.mouseKeyboardOnLoad)        

except:
    pass