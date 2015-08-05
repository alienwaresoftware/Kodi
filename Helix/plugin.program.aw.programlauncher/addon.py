import os
import sys
import urllib
import urlparse
from glob import glob
import json
import subprocess
import traceback
import string
import uuid
import tempfile
import shutil
import webbrowser
import sqlite3
import ntpath
from xml.etree import ElementTree as ET
from xml.dom.minidom import parse
from xml.dom.minidom import Document

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import resources.lib.common as common
from resources.lib.common import log
from resources.lib.common import localize

__addon__ = common.__addon__
__addonid__ = common.__addonid__
__addonversion__ = common.__addonversion__
__addonname__ = common.__addonname__
__addonpath__ = common.__addonpath__
__addonprofile__ = common.__addonprofile__
__icon__ = common.__icon__

MEDIA_PATH = os.path.join(__addonpath__, 'resources', 'skins', 'Default', 'media', 'alienware')
DEFAULT_THUMB_PATH = os.path.join(__addonprofile__, "thumbs")
DEFAULT_FANART_PATH = os.path.join(__addonprofile__, "fanarts")
PROGRAMS_DB_PATH = os.path.join(__addonprofile__, "programs.db")
TEMP_DIR = os.path.join(tempfile.gettempdir(), __addonid__)
DEFAULT_MUSIC_THUMB_PATH = os.path.join(MEDIA_PATH, "icon_music.png")
DEFAULT_PICTURE_THUMB_PATH = os.path.join(MEDIA_PATH, "icon_pictures.png")
DEFAULT_VIDEO_THUMB_PATH = os.path.join(MEDIA_PATH, "icon_video.png")
DEFAULT_PROGRAM_THUMB_PATH = os.path.join(MEDIA_PATH, "icon_programs.png")
ADDONS_PATH = xbmc.translatePath(os.path.join("special://home", "addons"))
FAVOURITES_PATH = xbmc.translatePath('special://profile/favourites.xml')
DATABASE_PATH = xbmc.translatePath('special://profile/Database')
START_MENU_PATH = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs"

base_url = ''
addon_handle = -1
lastaction = ''

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


def getUuid():
    return uuid.uuid4().get_hex()


def build_url(query):    
    return base_url + '?' + urllib.urlencode(query)


def writeToDB(programs):
    programsDBfile = open(PROGRAMS_DB_PATH, 'w')
    programsDBfile.write(json.dumps(programs))
    programsDBfile.close()

def getProgramsJson():
    if os.path.isfile(PROGRAMS_DB_PATH):
        programsDBfile = open(PROGRAMS_DB_PATH, 'r')
        programsJson = json.loads(programsDBfile.read())
        programsDBfile.close()
        return programsJson


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

def removeProgram(program):
   
    programs = getProgramsJson()

    for i in programs:
        if programs[i]['name'] == program.name and programs[i]['path'] == program.path:
            programs.pop(i)
            break

    writeToDB(programs)


def getProgramsFromPath(path):
    if path == 'program':
        programs = getPrograms(common.CATEGORY_PROGRAM)
    elif path == 'music':
        programs = getPrograms(common.CATEGORY_MUSIC)
    elif path == 'video':
        programs = getPrograms(common.CATEGORY_VIDEO)
    elif path == 'image':
        programs = getPrograms(common.CATEGORY_IMAGE)
    else:
        programs = getPrograms(common.CATEGORY_ALL)

    return programs

def getCategoryName(path):
    if path == 'program':
        category = localize(33001)
    elif path == 'music':
        category = localize(33002)
    elif path == 'video':
        category = localize(33003)
    elif path == 'image':
        category = localize(33004)
    else:
        category = localize(33000)

    return category



def extractIcon2(filePath, extractIconPath):
    if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)

    resHackPath = os.path.join(__addonpath__, "resources", "lib", "ResourceHacker.exe")
    subprocess.call(
        [resHackPath, "-extract", filePath, ",", os.path.join(TEMP_DIR, "extractIcon.rc"), ",", "IconGroup,,"])

    iconPath = os.path.join(TEMP_DIR, "Icon_1.ico")
    if os.path.exists(iconPath):
        shutil.copy2(iconPath, extractIconPath)
    shutil.rmtree(TEMP_DIR)


def extractIcon(filePath, extractIconPath):
    return AlphaUIUtils.GetIconFromExecutable(unicode(filePath), unicode(extractIconPath))


def addProgramToDictionary(programs, programId, name, category, type, path, parameter, thumbImage, fanartImage,
                           isNameChanged,
                           isPathChanged, isIconChanged, isFanartChanged, addedToMainMenu=False, addedToSubMenu=False,
                           mouseKeyboardOnLoad=True, elevatePermission=False, startAtBoot=False):
    programs[programId] = {}
    programs[programId]['name'] = name
    programs[programId]['category'] = category
    programs[programId]['type'] = type
    programs[programId]['path'] = path
    programs[programId]['parameter'] = parameter
    programs[programId]['thumbImage'] = thumbImage
    programs[programId]['fanartImage'] = fanartImage
    programs[programId]['isNameChanged'] = isNameChanged
    programs[programId]['isPathChanged'] = isPathChanged
    programs[programId]['isIconChanged'] = isIconChanged
    programs[programId]['isFanartChanged'] = isFanartChanged
    programs[programId]['addedToMainMenu'] = addedToMainMenu
    programs[programId]['addedToSubMenu'] = addedToSubMenu
    programs[programId]['mouseKeyboardOnLoad'] = mouseKeyboardOnLoad
    programs[programId]['elevatePermission'] = elevatePermission
    programs[programId]['startAtBoot'] = startAtBoot


def getProgramsDictionary():
    existingPrograms = getPrograms(common.CATEGORY_ALL)
    programs = {}

    for program in existingPrograms:
        addProgramToDictionary(programs, program.id, program.name, program.category, program.type, program.path,
                               program.parameter, program.thumbImage, program.fanartImage, program.isNameChanged,
                               program.isPathChanged, program.isIconChanged, program.isFanartChanged,
                               program.addedToMainMenu, program.addedToSubMenu, program.mouseKeyboardOnLoad,
                               program.elevatePermission, program.startAtBoot)

    return programs


def getSafeFileName(fileName):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in fileName if c in valid_chars)


def getDefaultThumbImage(launcherCategory):
    if launcherCategory == common.CATEGORY_PROGRAM:
        return DEFAULT_PROGRAM_THUMB_PATH
    elif launcherCategory == common.CATEGORY_VIDEO:
        return DEFAULT_VIDEO_THUMB_PATH
    elif launcherCategory == common.CATEGORY_MUSIC:
        return DEFAULT_MUSIC_THUMB_PATH
    elif launcherCategory == common.CATEGORY_IMAGE:
        return DEFAULT_PICTURE_THUMB_PATH


def getAddons():
    addons = []
    for dir_addon in os.listdir(ADDONS_PATH):
        addon_xml_path = os.path.join(ADDONS_PATH, dir_addon, 'addon.xml')
        if os.path.isfile(addon_xml_path):
            with open(addon_xml_path, 'r') as f:
                tree = ET.parse(f)
                addonNode = tree.find('[@id]')
                provideNode = tree.find('.//extension/provides')
                if provideNode is not None:
                    if addonNode.attrib['id'] != __addonid__:
                        addonType = 1
                        provides = string.split(provideNode.text, ' ')
                        if provides[0] == "executable":
                            addonType = common.CATEGORY_PROGRAM
                        elif provides[0] == "audio":
                            addonType = common.CATEGORY_MUSIC
                        elif provides[0] == "video":
                            addonType = common.CATEGORY_VIDEO
                        elif provides[0] == "image":
                            addonType = common.CATEGORY_IMAGE

                        addons.append((addonNode.attrib['id'], addonNode.attrib['name'], addonType,
                                       os.path.join(ADDONS_PATH, dir_addon, 'icon.png'),
                                       os.path.join(ADDONS_PATH, dir_addon, 'fanart.jpg')))
    return addons

def getProgramUrl(program, path):
    url = ''
    if (common.CATEGORY_ADD & int(program.category)) == common.CATEGORY_ADD:
        url = build_url(
            {'mode': 'folder', 'action': 'addprogram', 'programid': program.id, 'programtype': program.type,
             'programcategory': program.category, 'programpath': program.path, 'path': path,
             'programparam': program.parameter, "mouse" : program.mouseKeyboardOnLoad, "elevatepermission" : program.elevatePermission})
    else:
        url = build_url(
            {'mode': 'folder', 'action': 'launchprogram', 'programid': program.id, 'programtype': program.type,
             'programcategory': program.category, 'programpath': program.path, 'path': path,
             'programparam': program.parameter, "mouse" : program.mouseKeyboardOnLoad, "elevatepermission" : program.elevatePermission})

    return url

def isInFavorites(program):
    if os.path.isfile(FAVOURITES_PATH):
        with open(FAVOURITES_PATH, 'r') as f:
            tree = ET.parse(f)
            favouriteNodes = tree.findall('favourite[@programid]')
            for favouriteNode in favouriteNodes:
                if favouriteNode.attrib["programid"] == program.id:
                    return True
                    break

    else:
        return False


def addToFavorite(program, path):
    if program:
        doc = None
        root = None

        if (not os.path.isfile(FAVOURITES_PATH)):
            doc = Document()
            root = doc.createElement("favourites")
            doc.appendChild(root)
        else:
            doc = parse(FAVOURITES_PATH)
            root = doc.documentElement

        favNode = doc.createElement("favourite")
        root.appendChild(favNode)

        favNode.setAttribute("name", program.name)
        favNode.setAttribute("thumb", program.thumbImage)
        favNode.setAttribute("programid", program.id)

        url = getProgramUrl(program, path)

        textNode = doc.createTextNode(url)
        favNode.appendChild(textNode)

        doc.writexml(open(FAVOURITES_PATH, 'w'))

        doc.unlink()


def removeFromFavorite(program, path):
    if program:
        if os.path.isfile(FAVOURITES_PATH):
            doc = parse(FAVOURITES_PATH)
            fav_doc = doc.documentElement.getElementsByTagName('favourite')
            for count, favourite in enumerate(fav_doc):
                if favourite.attributes.get('programid',None) is not None and favourite.attributes['programid'].nodeValue == program.id and favourite.firstChild.data == getProgramUrl(program, path):
                    doc.documentElement.removeChild(favourite)
                    break

        doc.writexml(open(FAVOURITES_PATH, 'w'))

        doc.unlink()


def getFavoriteMenuItem(program, folderAction, path):
    favoriteMenu = None
    if (isInFavorites(program)):
        favoriteMenu = (xbmc.getLocalizedString(14077),
                     'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={4}&amp;path={5}&amp;action=removefromfavorites&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                         __addonid__, program.id, program.type, program.category, folderAction, path),)
    else:
        favoriteMenu = (xbmc.getLocalizedString(14076),
                     'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={4}&amp;path={5}&amp;action=addtofavorites&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                         __addonid__, program.id, program.type, program.category, folderAction, path),)
    return favoriteMenu


def getHomeMenuItem(program, folderAction, path):
    homeMenu = None

    isProgramAdded = isAddedtoMenu('HomeMenuButton' ,program.id)

    if isProgramAdded:
        homeMenu = (localize(33028),
             'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={4}&amp;path={5}&amp;action=removefromhomemenu&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                 __addonid__, program.id, program.type, program.category, folderAction, path),)
    else:
        homeMenu = (localize(33027),
             'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={4}&amp;path={5}&amp;action=addtohomemenu&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                 __addonid__, program.id, program.type, program.category, folderAction, path),)

    return homeMenu


def isAddedtoMenu(buttonPrefix,programId):
    isSubMenuExist = False
    for i in range(1, 6, 1):
        addonId = ''
        buttonValue = xbmc.getInfoLabel('Skin.String({0}{1})'.format(buttonPrefix, i))
        if not buttonValue:
            addonId = xbmc.getInfoLabel('System.AddonTitle({0})'.format(buttonValue))

        if not addonId:
            if xbmc.getInfoLabel('Skin.String({0}{1}Type)'.format(buttonPrefix, i)) == 'launcher':
                if xbmc.getInfoLabel('Skin.String({0}{1}TypeId)'.format(buttonPrefix, i)) == programId:
                    isSubMenuExist = True
                    break
    return isSubMenuExist

def existsInHomeMenu(program):
    return isAddedtoMenu('HomeMenuButton' ,program.id)

def existsInSubMenu(program):
    return isAddedtoMenu('HomeProgramButton', program.id) or isAddedtoMenu('HomeVideosButton', program.id) or isAddedtoMenu('HomeMusicButton', program.id) or isAddedtoMenu('HomePictureButton', program.id)

def getSubMenuItem(program, folderAction, path):
    subMenu = None
    title = ''
    action = ''
    isSubMenuExist = False

    #print "program.category {0} -> {1}".format(program.name, program.category)

    if program.category == common.CATEGORY_PROGRAM:
        isSubMenuExist = isAddedtoMenu('HomeProgramButton', program.id)
        if isSubMenuExist:
            title = localize(33036)
        else:
            title = localize(33035)
    elif program.category == common.CATEGORY_VIDEO:
        isSubMenuExist = isAddedtoMenu('HomeVideosButton', program.id)
        if isSubMenuExist:
            title = localize(33030)
        else:
            title = localize(33029)
    elif program.category == common.CATEGORY_MUSIC:
        isSubMenuExist = isAddedtoMenu('HomeMusicButton', program.id)
        if isSubMenuExist:
            title = localize(33032)
        else:
            title = localize(33031)
    elif program.category == common.CATEGORY_IMAGE:
        isSubMenuExist = isAddedtoMenu('HomePictureButton', program.id)
        if isSubMenuExist:
            title = localize(33034)
        else:
            title = localize(33033)

    if isSubMenuExist:
        action = 'removefromsubmenu'
    else:
        action = 'addtosubmenu'

    subMenu = (title,
             'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={5}&amp;path={6}&amp;action={4}&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                 __addonid__, program.id, program.type, program.category, action, folderAction, path),)

    return subMenu


    listItem.addContextMenuItems([mouseKeyboardSettingMenu, elevatePermissionSettingMenu, startAtBootSettingMenu,], True)

def createEditDialog(selectedProgram):
    
    heading = localize(33048)
    item1 = localize(33005)
    item2 = localize(33006)
    item3 = localize(33007)
    item4 = localize(33008)
    item5 = localize(33055)

    if selectedProgram.type == common.TYPE_ADDON:
        items = [item1, item3, item4]
    else:
        items = [item1, item2, item3, item4, item5]

    dialog = xbmcgui.Dialog()
    retValue = dialog.select(heading, items)

    if retValue != -1:

        if selectedProgram.type == common.TYPE_ADDON:
            if retValue == 0:
                updateProgramInformation(selectedProgram, 'title')
            elif retValue == 1:
                updateProgramInformation(selectedProgram, 'icon')
            elif retValue == 2:
                updateProgramInformation(selectedProgram, 'fanart')
        else:
            if retValue == 0:
                updateProgramInformation(selectedProgram, 'title')
            elif retValue == 1:
                updateProgramInformation(selectedProgram, 'path')
            elif retValue == 2:
                updateProgramInformation(selectedProgram, 'icon')
            elif retValue == 3:
                updateProgramInformation(selectedProgram, 'fanart')
            elif retValue == 4:
                updateProgramInformation(selectedProgram, 'category')

def addContextMenu(listItem, program, folderAction, path):
    if program.category == common.CATEGORY_ADD:
        listItem.addContextMenuItems([], True)
    else:
        title = ''
        if program.mouseKeyboardOnLoad:
            title = localize(33038)
        else:
            title = localize(33037)

        mouseKeyboardSettingMenu = (title,
                                       'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={4}&amp;path={5}&amp;action=updatesetting&amp;settingname=mousekb&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                                            __addonid__, program.id, program.type, program.category, folderAction, path),)
      
        if program.elevatePermission:
            title = localize(33019)
        else:
            title = localize(33018)

        elevatePermissionSettingMenu = (title,
                                       'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={4}&amp;path={5}&amp;action=updatesetting&amp;settingname=elevatepermission&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                                            __addonid__, program.id, program.type, program.category, folderAction, path),)

        if program.startAtBoot:
            title = localize(33040)
        else:
            title = localize(33039)

        startAtBootSettingMenu = (title,
                                       'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={4}&amp;path={5}&amp;action=updatesetting&amp;settingname=startatboot&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                                            __addonid__, program.id, program.type, program.category, folderAction, path),)


        if program.type == common.TYPE_ADDON:

            editMenu = (localize(33046),
                    'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={4}&amp;path={5}&amp;action=editmenu&amp;settingname=mousekb&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                      __addonid__, program.id, program.type, program.category, folderAction, path),)

            listItem.addContextMenuItems([getFavoriteMenuItem(program, folderAction, path),
                                      editMenu,
                                      getHomeMenuItem(program, folderAction, path),
                                      getSubMenuItem(program, folderAction, path),                                     
                                      ], True)
        elif program.type == common.TYPE_WEBSITE:
            editMenu = (localize(33047),
                    'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={4}&amp;path={5}&amp;action=editmenu&amp;settingname=mousekb&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                      __addonid__, program.id, program.type, program.category, folderAction, path),)
            
            removeFromPrograms = (localize(33049),
                                       'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={4}&amp;path={5}&amp;action=removefromprograms&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                                            __addonid__, program.id, program.type, program.category, folderAction, path),)
            listItem.addContextMenuItems([getFavoriteMenuItem(program, folderAction, path),
                                      editMenu,
                                      getHomeMenuItem(program, folderAction, path),
                                      getSubMenuItem(program, folderAction, path),
                                      mouseKeyboardSettingMenu,
                                      removeFromPrograms,
                                      ], True)            
        else:
            #log("in program branch") 
            editMenu = (localize(33047),
                    'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={4}&amp;path={5}&amp;action=editmenu&amp;settingname=mousekb&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                      __addonid__, program.id, program.type, program.category, folderAction, path),)
            
            removeFromPrograms = (localize(33049),
                                       'XBMC.Container.Refresh(plugin://{0}/?mode=contextmenu&amp;from={4}&amp;path={5}&amp;action=removefromprograms&amp;programid={1}&amp;programtype={2}&amp;programcategory={3})'.format(
                                            __addonid__, program.id, program.type, program.category, folderAction, path),)
            listItem.addContextMenuItems([getFavoriteMenuItem(program, folderAction, path),
                                      editMenu,
                                      getHomeMenuItem(program, folderAction, path),
                                      getSubMenuItem(program, folderAction, path),
                                      mouseKeyboardSettingMenu,
                                      elevatePermissionSettingMenu,
                                      startAtBootSettingMenu,
                                      removeFromPrograms,
                                      ], True)




def get_view_mode():
    view_mode = 50
    for id in range(50, 59 + 1):
        try:
            if xbmc.getCondVisibility("Control.IsVisible(%i)" % id):
                view_mode = repr(id)
                return view_mode
                break
        except:
            pass

    for id in range(500, 600 + 1):
        try:
            if xbmc.getCondVisibility("Control.IsVisible(%i)" % id):
                view_mode = repr(id)
                return view_mode
                break
        except:
            pass

    return view_mode

def getDisabledAddonList():
    disabledAddonList = []
    for fileName in glob(os.path.join(DATABASE_PATH,'Addons*.db')):
        con = sqlite3.connect(fileName)
        cur = con.cursor()

        command = "SELECT addonID from main.disabled;"
        cur.execute(command)
        rows = cur.fetchall()

        for row in rows:
            disabledAddonList.append(row[0])
        con.close()

    return disabledAddonList

def initAddon():
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    try:
        # Create Addon Necessary Path
        if not os.path.exists(DEFAULT_THUMB_PATH): os.makedirs(DEFAULT_THUMB_PATH)
        if not os.path.exists(DEFAULT_FANART_PATH): os.makedirs(DEFAULT_FANART_PATH)

        # Create Database file if not exist

        programs = {}
        if not os.path.isfile(PROGRAMS_DB_PATH):
            addProgramToDictionary(programs, getUuid(), localize(33022), common.CATEGORY_ADD, 0, '', '',
                                   os.path.join(MEDIA_PATH, 'add.png'), '', 0, 0, 0, 0, False, False, False, False,
                                   False)
            addons = getAddons()
            for addon in addons:
                addProgramToDictionary(programs, addon[0], addon[1], addon[2], common.TYPE_ADDON,
                                       'RunAddon(%s)' % addon[0], '',
                                       addon[3], addon[4], 0, 0, 0, 0, False, False, False, False, False)
        else:
            #programs = getProgramsDictionary()
            programs = getProgramsJson()

            programList = getPrograms(common.CATEGORY_ALL)
            addons = getAddons()
            programsToRemove = []
            for programId in programs:
                if programs[programId]['type'] == common.TYPE_ADDON:
                    shouldRemove = True
                    for addon in addons:
                        if programId == addon[0]:
                            shouldRemove = False
                            break
                    if shouldRemove:
                        programsToRemove.append(programId)

            for programId in getDisabledAddonList():
                programsToRemove.append(programId)

            for programId in programsToRemove:
                if programs.get(programId, None):
                    del programs[programId]

            for addon in addons:
                shouldAdd = True
                for program in programList:
                    if (program.id == addon[0]):
                        shouldAdd = False
                        break
                if (shouldAdd):
                    addProgramToDictionary(programs, addon[0], addon[1], addon[2], common.TYPE_ADDON,
                                           'RunAddon(%s)' % addon[0], '',
                                           addon[3], addon[4], 0, 0, 0, 0, False, False, False, False, False)

        writeToDB(programs)
    except Exception, e:
        #log(e.message)
        #log(e.__class__.__name__)
        traceback.print_exc(e)

    programs = getPrograms(common.CATEGORY_ADD)
    for p in programs:
        if p.category == common.CATEGORY_ADD:
            updateProgramInformation(p, 'add_title')
            break

    xbmc.executebuiltin("Dialog.Close(busydialog)")


def createRootFolders():
    noOfItems = 5

    url = build_url({'action': 'show','mode': 'folder','path': 'all'})
    li = xbmcgui.ListItem(localize(33000), iconImage=os.path.join(MEDIA_PATH, 'all.png'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=noOfItems, isFolder=True)

    url = build_url({'mode': 'folder', 'action': 'show', 'path': 'program'})
    li = xbmcgui.ListItem(localize(33001), iconImage=os.path.join(MEDIA_PATH, 'icon_programs.png'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=noOfItems, isFolder=True)

    url = build_url({'mode': 'folder', 'action': 'show', 'path': 'music'})
    li = xbmcgui.ListItem(localize(33002), iconImage=os.path.join(MEDIA_PATH, 'icon_music.png'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=noOfItems, isFolder=True)

    url = build_url({'mode': 'folder', 'action': 'show', 'path': 'video'})
    li = xbmcgui.ListItem(localize(33003), iconImage=os.path.join(MEDIA_PATH, 'icon_video.png'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=noOfItems, isFolder=True)

    url = build_url({'mode': 'folder', 'action': 'show', 'path': 'image'})
    li = xbmcgui.ListItem(localize(33004), iconImage=os.path.join(MEDIA_PATH, 'icon_pictures.png'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=noOfItems, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

def showLaunchers(path):

    viewModeId = xbmc.getInfoLabel('Skin.String(ProgramsDefaultViewMode)')
    if (not viewModeId):
        xbmc.executebuiltin('Skin.SetString(ProgramsDefaultViewMode, %s)' % '500')
        xbmc.executebuiltin('Container.SetViewMode(%s)' % '500')

    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)

    programs = getProgramsFromPath(path)

    if (programs):
        for program in programs:
            url = getProgramUrl(program, path)

            li = xbmcgui.ListItem(program.name, iconImage=program.thumbImage)
            li.setProperty('Fanart_Image', program.fanartImage)

            addContextMenu(li, program, 'show', path)

            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=len(programs),
                                        isFolder=False)

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

    if (not viewModeId):
        xbmc.executebuiltin('Container.SetViewMode(%s)' % '500')

def getProgramTitle(dialog, name):
    if not dialog:
        dialog = xbmcgui.Dialog()

    retValue = dialog.input(localize(33012), name, type=xbmcgui.INPUT_ALPHANUM)

    if retValue:
        return retValue
    else:
        return name


def getProgramPath(dialog, programType, path):
    if not dialog:
        dialog = xbmcgui.Dialog()

    retValue = ''
    if programType == common.TYPE_WEBSITE:
        retValue = dialog.input(localize(33010), path, type=xbmcgui.INPUT_ALPHANUM)
    else:
        retValue = dialog.browse(1, localize(33011), 'files', '.exe', True, False, path)

    if retValue:
        return retValue
    else:
        return path

def getProgramIcon(dialog, thumbImage):
    if not dialog:
        dialog = xbmcgui.Dialog()

    #log(thumbImage)
    retValue = dialog.browse(2, localize(33013), 'files', '.png', True, False, thumbImage)

    if retValue:
        return retValue
    else:
        return thumbImage

def getProgramFanart(dialog, fanartImage):
    if not dialog:
        dialog = xbmcgui.Dialog()
        newFanart = dialog.browse(2, localize(33014), 'files', '.png|.jpg', True, False, fanartImage)

        if newFanart:
            return newFanart
        else:
            return fanartImage

def getProgramCategory(dialog, category):
    if not dialog:
        dialog = xbmcgui.Dialog()        
    
    items = [localize(33001), localize(33003), localize(33002), localize(33004)]     
    dialogCategory = dialog.select(localize(33055),
                                   items)
    if dialogCategory == 0:
        category = common.CATEGORY_PROGRAM
    elif dialogCategory == 1:
        category = common.CATEGORY_VIDEO
    elif dialogCategory == 2:
        category = common.CATEGORY_MUSIC
    elif dialogCategory == 3:
        category = common.CATEGORY_IMAGE

    return category

def getStartMenuPrograms():
    programs = []
    for root, dir, files in os.walk(START_MENU_PATH):
        for file in files:
            if file.endswith(".lnk"):
                if(AlphaUIUtils.IsLnkFileIsExe(unicode(os.path.join(root, file)))):
                    programs.append(os.path.join(root, file))
    return programs
    

def addProgram():
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

    programs = getProgramsDictionary()

    dialog = xbmcgui.Dialog()
    dialogCategory = dialog.select(localize(33056),
                                   [localize(33001), localize(33003), localize(33002), localize(33004)])

    if dialogCategory != -1:
        programCategory = 2 ** (dialogCategory + 1)

        d = dialog.select(localize(33023), [localize(33024), localize(33026)])
        if(d == 1):
            d = 2

        if d != -1 and d != 2: 
            dialogAddInstall = dialog.select(localize(33050), [localize(33051), localize(33052)])

            #install a program
            if dialogAddInstall == 0:
                d = -1
                programType = 2 ** d
                path = getProgramPath(dialog, programType, '')
                #log(path)
                if path != "":
                    #subprocess.Popen(path)
                    result = AlphaUIUtils.LaunchApplication(unicode(path), unicode(os.path.dirname(path)),unicode(""), True, True, True)
                    if not result:
                        customizationAddon = xbmcaddon.Addon(id='service.aw.customizations')
                        customizationAddonLanguage = customizationAddon.getLocalizedString
                        xbmcgui.Dialog().ok(__addonname__, customizationAddonLanguage(33020))
            elif dialogAddInstall != 1:
                d = -1

        #add a program
        if d != -1:
            programType = 2 ** d

            addStartMenu = False
            if(d != 2):
                startMenuPrograms = getStartMenuPrograms()
                startMenuNames = [localize(33011)]
                for s in startMenuPrograms:
                    startMenuNames.append(string.replace(ntpath.basename(s), '.lnk', ''))


                #populate from start menu
                d = dialog.select(localize(33011), startMenuNames)

                if(d == -1):
                    return
                elif(d == 0):
                    path = getProgramPath(dialog, programType, '')
                    #log(path)
                else:
                    path = startMenuPrograms[d-1]
                    addStartMenu = True

                if path == "":
                    return

                allPrograms = getProgramsJson()
                for i in allPrograms:
                    if allPrograms[i]['path'] == path:
                        #program already exists
                        path = None
                        #create dialog
                        heading = localize(33053)
                        line = localize(33054)
                        dialog = xbmcgui.Dialog()
                        ok = dialog.ok(heading, line)

                        return

            if programType == common.TYPE_WEBSITE:
                path = getProgramPath(dialog, common.TYPE_WEBSITE, '')
                nameHelp = path
            else:
                folderPath, fileName = os.path.split(path)
                nameHelp = string.replace(fileName, '.exe', '')
                nameHelp = string.replace(nameHelp, '.lnk', '')
            if path:
                name = getProgramTitle(dialog, nameHelp)
                if name:
                    if programType == common.TYPE_WEBSITE:
                        thumbImage = os.path.join(MEDIA_PATH, "website.png")
                    else:
                        #thumbImage = os.path.join(DEFAULT_THUMB_PATH,"{0}_{1}.ico".format(getSafeFileName(name), getUuid()))
                        thumbImage = os.path.join(DEFAULT_THUMB_PATH,"{0}_{1}.png".format(getSafeFileName(name), getUuid()))
                        if not extractIcon(path, thumbImage):
                            thumbImage = getDefaultThumbImage(programCategory)
                            thumbImage = getProgramIcon(dialog, thumbImage)
                    
                       
                    #thumbImage = getProgramIcon(dialog, thumbImage)

                    fanartImage = getProgramFanart(dialog, '')

                    if programType != common.TYPE_WEBSITE:

                        enableMouseKeyboardOn = True

                        d = dialog.select(localize(33015), [localize(33037), localize(33038)])
                        if d == 0:
                            enableMouseKeyboardOn = True
                        elif d == 1:
                            enableMouseKeyboardOn = False

                        elevatePermission = False

                        d = dialog.select(localize(33016), [localize(33019), localize(33018)])
                        if d == 0:
                            elevatePermission = False
                        elif d == 1:
                            elevatePermission = True

                        startAtBoot = False

                        d = dialog.select(localize(33017), [localize(33040), localize(33039)])
                        if d == 0:
                            startAtBoot = False
                        elif d == 1:
                            startAtBoot = True

                        addProgramToDictionary(programs, getUuid(), name, programCategory, programType, path, '',
                                               thumbImage, fanartImage, 0, 0, 0, 0,
                                               mouseKeyboardOnLoad=enableMouseKeyboardOn,
                                               elevatePermission=elevatePermission, startAtBoot=startAtBoot)
                    else:
                        addProgramToDictionary(programs, getUuid(), name, programCategory, programType, path, '',
                                               thumbImage, fanartImage, 0, 0, 0, 0)

                    dialogConfim = dialog.yesno(localize(33020), '', localize(33021))
                    if dialogConfim:
                        writeToDB(programs)

    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
    url = base_url + "?action=show&mode=folder&path=all"
    xbmc.executebuiltin('Container.Refresh("' + url + '")')

def launchProgram(selectedProgram, path):
    isContainerRefresh = True

    try:
        if selectedProgram.type == common.TYPE_ADDON:
            isContainerRefresh = False
            xbmc.executebuiltin(selectedProgram.path)
        elif selectedProgram.type == common.TYPE_WEBSITE:
            webbrowser.open(selectedProgram.path)
        elif selectedProgram.type == common.TYPE_WIN32 or selectedProgram.type == common.TYPE_WIN8:
            #subprocess.Popen(selectedProgram.path, cwd=os.path.dirname(selectedProgram.path))
            mouseAndKeyboard = selectedProgram.mouseKeyboardOnLoad == "True"
            elevated = selectedProgram.elevatePermission == "True"
            log(selectedProgram.path)
            log(os.path.dirname(selectedProgram.path))
            result = AlphaUIUtils.LaunchApplication(unicode(selectedProgram.path), unicode(os.path.dirname(selectedProgram.path)),unicode(""), elevated, mouseAndKeyboard, mouseAndKeyboard)
            if not result:
                customizationAddon = xbmcaddon.Addon(id='service.aw.customizations')
                customizationAddonLanguage = customizationAddon.getLocalizedString
                xbmcgui.Dialog().ok(__addonname__, customizationAddonLanguage(33020))
    except:
        pass

    if (isContainerRefresh):
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)      
        url = base_url + "?action=show&mode=folder&path=" + path
        xbmc.executebuiltin('Container.Refresh("' + url + '")')


def processFolderUrl(actionName, path, selectedProgram):
    if (actionName == 'show'):
        showLaunchers(path)
    elif actionName == 'addprogram':
        addProgram()
    elif actionName == 'launchprogram':
        launchProgram(selectedProgram, path)


def findSelectedProgram(programs, programId, programType, programCategory):
    for program in programs:
        if program.id == programId and program.type == programType and program.category == programCategory:
            return program

def updateProgramInformation(selectedProgram, property):
    if selectedProgram:
        programJson = getProgramsJson()

        if programJson.get(selectedProgram.id, None):
            if programJson[selectedProgram.id]['type'] == selectedProgram.type:

                databaseChanged = False
                if property == 'title':
                    name = getProgramTitle(None, selectedProgram.name)
                    if name and name != selectedProgram.name:
                        programJson[selectedProgram.id]['name'] = name
                        programJson[selectedProgram.id]['isNameChanged'] = 1
                        selectedProgram.name = name
                        selectedProgram.isNameChanged = 1
                        databaseChanged = True
                elif property == 'add_title':
                    name = localize(33022)
                    if name and name != selectedProgram.name:
                        programJson[selectedProgram.id]['name'] = name
                        programJson[selectedProgram.id]['isNameChanged'] = 1
                        selectedProgram.name = name
                        selectedProgram.isNameChanged = 1
                        databaseChanged = True
                elif property == 'path':
                    newPath = getProgramPath(None, selectedProgram.type, selectedProgram.path)
                    if newPath and newPath != selectedProgram.path:
                        programJson[selectedProgram.id]['path'] = newPath
                        programJson[selectedProgram.id]['isPathChanged'] = 1
                        selectedProgram.path = newPath
                        selectedProgram.isPathChanged = 1
                        databaseChanged = True
                elif property == 'icon':
                    newThumbImage = getProgramIcon(None, selectedProgram.thumbImage)
                    if newThumbImage and newThumbImage != selectedProgram.thumbImage:
                        programJson[selectedProgram.id]['thumbImage'] = newThumbImage
                        programJson[selectedProgram.id]['isIconChanged'] = 1
                        selectedProgram.thumbImage = newThumbImage
                        selectedProgram.isIconChanged = 1
                        databaseChanged = True
                elif property == 'fanart':
                    newFanartImage = getProgramFanart(None, selectedProgram.fanartImage)
                    if newFanartImage and newFanartImage != selectedProgram.fanartImage:
                        programJson[selectedProgram.id]['fanartImage'] = newFanartImage
                        programJson[selectedProgram.id]['isFanartChanged'] = 1
                        selectedProgram.fanartImage = newFanartImage
                        selectedProgram.isFanartChanged = 1
                        databaseChanged = True
                elif property == 'category':
                    newCategory = getProgramCategory(None, selectedProgram.category) 
                    if newCategory and newCategory != selectedProgram.category:
                        programJson[selectedProgram.id]['category'] = newCategory
                        programJson[selectedProgram.id]['isCategoryChanged'] = 1
                        removeFromHomeMenu(selectedProgram, 'sub')
                        selectedProgram.category = newCategory
                        databaseChanged = True          
                elif property == 'mousekb':
                    selectedProgram.mouseKeyboardOnLoad = not selectedProgram.mouseKeyboardOnLoad
                    programJson[selectedProgram.id]['mouseKeyboardOnLoad'] = selectedProgram.mouseKeyboardOnLoad
                    databaseChanged = True
                elif property == 'elevatepermission':
                    selectedProgram.elevatePermission = not selectedProgram.elevatePermission
                    programJson[selectedProgram.id]['elevatePermission'] = selectedProgram.elevatePermission
                    databaseChanged = True
                elif property == 'startatboot':
                    selectedProgram.startAtBoot = not selectedProgram.startAtBoot
                    programJson[selectedProgram.id]['startAtBoot'] = selectedProgram.startAtBoot
                    databaseChanged = True

                if databaseChanged:
                    writeToDB(programJson)


def getMenuInfo(menuType, category):
    title = ''
    buttonPrefix = ''
    if menuType == 'home':
            buttonPrefix = 'HomeMenuButton'
            title = localize(33041)
    elif menuType == 'sub':
        if category == common.CATEGORY_PROGRAM:
            buttonPrefix = 'HomeProgramButton'
            title = localize(33042)
        elif category == common.CATEGORY_VIDEO:
            buttonPrefix = 'HomeVideosButton'
            title = localize(33043)
        elif category == common.CATEGORY_MUSIC:
            buttonPrefix = 'HomeMusicButton'
            title = localize(33044)
        elif category == common.CATEGORY_IMAGE:
            buttonPrefix = 'HomePictureButton'
            title = localize(33045)
    return title, buttonPrefix


def removeFromHomeMenu(selectedProgram, menuType):
    if selectedProgram:

        title, buttonPrefix = getMenuInfo(menuType, selectedProgram.category)

        for i in range(1, 6, 1):
            buttonValue = xbmc.getInfoLabel('Skin.String({0}{1})'.format(buttonPrefix, i))
            if buttonValue:
                addonId = xbmc.getInfoLabel('System.AddonTitle({0})'.format(buttonValue))

                if not addonId:
                    if xbmc.getInfoLabel('Skin.String({0}{1}Type)'.format(buttonPrefix, i)) == 'launcher':
                        if xbmc.getInfoLabel('Skin.String({0}{1}TypeId)'.format(buttonPrefix, i)) == selectedProgram.id:
                            xbmc.executebuiltin('Skin.SetString({0}{1}, '')'.format(buttonPrefix, i))
                            xbmc.executebuiltin('Skin.SetString({0}{1}Title, '')'.format(buttonPrefix, i))
                            xbmc.executebuiltin('Skin.SetString({0}{1}Image, '')'.format(buttonPrefix, i))
                            xbmc.executebuiltin('Skin.SetString({0}{1}Type, '')'.format(buttonPrefix, i))
                            xbmc.executebuiltin('Skin.SetString({0}{1}TypeId, '')'.format(buttonPrefix, i))

                            programJson = getProgramsJson()
                            if menuType == 'home':
                                programJson[selectedProgram.id]['addedToMainMenu'] = False
                            elif menuType == 'sub':
                                programJson[selectedProgram.id]['addedToSubMenu'] = False

                            writeToDB(programJson)

                            break


def addtoHomeMenu(selectedProgram, menuType, path):
    if selectedProgram:
        myurl = getProgramUrl(selectedProgram, path)
        optionToShow = []

        title, buttonPrefix = getMenuInfo(menuType, selectedProgram.category)

        for i in range(1, 6, 1):
            buttonValue = xbmc.getInfoLabel('Skin.String({0}{1})'.format(buttonPrefix, i))
            if buttonValue:
                addonId = xbmc.getInfoLabel('System.AddonTitle({0})'.format(buttonValue))

                if addonId:
                    optionToShow.append(xbmc.getLocalizedString(24000) + ' {0}        {1}'.format(i, addonId))
                else:
                    optionToShow.append(xbmc.getLocalizedString(24000) + ' {0}        {1}'.format(i, xbmc.getInfoLabel('Skin.String({0}{1}Title)'.format(buttonPrefix, i))))
            else:
                optionToShow.append(xbmc.getLocalizedString(24000) + ' {0}'.format(i))

        dialog = xbmcgui.Dialog()
        retVal = dialog.select(title,optionToShow)
        if retVal != -1:
            position = retVal + 1

            xbmc.executebuiltin('Skin.SetString({0}{1}, {2})'.format(buttonPrefix ,position, myurl))
            xbmc.executebuiltin('Skin.SetString({0}{1}Title, {2})'.format(buttonPrefix ,position, selectedProgram.name))
            xbmc.executebuiltin('Skin.SetString({0}{1}Image, {2})'.format(buttonPrefix ,position, selectedProgram.thumbImage))
            xbmc.executebuiltin('Skin.SetString({0}{1}Type, {2})'.format(buttonPrefix ,position, 'launcher'))
            xbmc.executebuiltin('Skin.SetString({0}{1}TypeId, {2})'.format(buttonPrefix ,position, selectedProgram.id))

            programJson = getProgramsJson()

            if menuType == 'home':
                programJson[selectedProgram.id]['addedToMainMenu'] = True
            elif menuType == 'sub':
                programJson[selectedProgram.id]['addedToSubMenu'] = True

            writeToDB(programJson)

def processUrl():
    global base_url
    base_url = sys.argv[0]
    global addon_handle
    addon_handle = int(sys.argv[1])
    args = urlparse.parse_qs(sys.argv[2][1:], True)
    
    mode = args.get('mode', None)

    if mode is None:
        # Create root folders
        createRootFolders()

    elif (mode[0] == 'folder'):
        actionName = args['action'][0]
        programid = args.get('programid', None)
        program = None
        path = args.get('path', None)
        if path is not None:
            path = args['path'][0]

        if programid is not None:
            program = Program(args['programid'][0], '', int(args['programcategory'][0]), int(args['programtype'][0]),
                              args['programpath'][0], args['programparam'][0], '', '', 0, 0, 0, 0, mouseKeyboardOnLoad = args['mouse'][0], elevatePermission = args['elevatepermission'][0])

        processFolderUrl(actionName, path, program)

        # log(actionName)

    elif mode[0] == 'contextmenu':
        actionName = args['action'][0]
        actionFrom = args['from'][0]
        path = args['path'][0]
        programId = args['programid'][0]
        programType = int(args['programtype'][0])
        programCategory = int(args['programcategory'][0])

        programs = getProgramsFromPath(path)

        selectedProgram = findSelectedProgram(programs, programId, programType, programCategory)

        if actionName == 'addtofavorites':
            addToFavorite(selectedProgram, path)
        elif actionName == 'removefromfavorites':
            removeFromFavorite(selectedProgram, path)
        elif actionName == 'editmenu':
            createEditDialog(selectedProgram)
        elif actionName == 'addtohomemenu':
            addtoHomeMenu(selectedProgram, 'home', path)
        elif actionName == 'removefromhomemenu':
            removeFromHomeMenu(selectedProgram, 'home')
        elif actionName == 'addtosubmenu':
            addtoHomeMenu(selectedProgram, 'sub', path)
        elif actionName == 'removefromsubmenu':
            removeFromHomeMenu(selectedProgram, 'sub')
        elif actionName == 'removefromprograms':
            #log("call remove")
            if isInFavorites(selectedProgram):
                removeFromFavorite(selectedProgram, path)
            if existsInHomeMenu(selectedProgram):
                removeFromHomeMenu(selectedProgram, 'home')
            if existsInSubMenu(selectedProgram):
                removeFromHomeMenu(selectedProgram, 'sub')
            removeProgram(selectedProgram)      
        elif actionName == 'advancedsettings':
            createAdvancedSettingsDialog(selectedProgram)
        elif actionName == 'updatesetting':
            settingName = args['settingname'][0]
            updateProgramInformation(selectedProgram, settingName)

        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        
        url = base_url + "?action=show&mode=folder&path=" + path
        xbmc.executebuiltin('Container.Refresh("' + url + '")')

if (__name__ == "__main__"):

    if (xbmcgui.Window(10004).getProperty('service.aw.customizations.isComponentInstalled') == "False"):
        customizationAddon = xbmcaddon.Addon(id='service.aw.customizations')
        customizationAddonLanguage = customizationAddon.getLocalizedString

        xbmcgui.Dialog().ok(__addonname__, customizationAddonLanguage(33011))
    else:
        import AlphaUIUtils

        # Initialize Addon
        initAddon()

        # Process Addon Url
        processUrl()