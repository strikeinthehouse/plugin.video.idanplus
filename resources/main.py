# -*- coding: utf-8 -*-
import sys, os, datetime, json
import xbmc, xbmcplugin, xbmcaddon
import resources.lib.common as common
import resources.lib.epg as epg
import resources.lib.iptv as iptv
import resources.lib.baseChannels as baseChannels

if common.py2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

Addon = xbmcaddon.Addon(common.AddonID)
AddonName = Addon.getAddonInfo("name")
icon = Addon.getAddonInfo('icon')
imagesDir = common.imagesDir
profileDir = common.profileDir
favoritesFile = os.path.join(profileDir, 'favorites.json')
if not os.path.isfile(favoritesFile):
    common.WriteList(favoritesFile, [])


def GetCategoriesList():
    name = common.GetLabelColor("Favoritos do Iday Plus", bold=True, color="none")
    common.addDir(name, '', 10, icon, infos={"Title": name}, addFav=False)
    name = common.GetLabelColor("Buscar Programas", bold=True, color="none")
    common.addDir(name, '', 4, icon, infos={"Title": name}, addFav=False)
    name = common.GetLabelColor("Televisão", bold=True, color="none")
    common.addDir(name, '', 1, icon, infos={"Title": name})
    name = common.GetLabelColor("VOD", bold=True, color="none")
    common.addDir(name, '', 2, icon, infos={"Title": name})
    name = common.GetLabelColor("Rádio", bold=True, color="none")
    common.addDir(name, '', 3, icon, infos={"Title": name})
    name = common.GetLabelColor("Programas de Rádio", bold=True, color="none")
    common.addDir(name, '', 12, icon, infos={"Title": name})
    name = common.GetLabelColor("Podcasts", bold=True, color="none")
    common.addDir(name, '', 13, icon, infos={"Title": name})
    name = common.GetLabelColor("Música", bold=True, color="none")
    common.addDir(name, '', 14, icon, infos={"Title": name})
    name = common.GetLabelColor("Configurações", bold=True, color="none")
    common.addDir(name, 'Addon.OpenSettings', 6, icon, infos={"Title": name}, moreData=common.AddonID, isFolder=False)

def GetUserChannels(type='tv'):
    userChannels = []
    if type == 'tv':
        channels = baseChannels.TvChannels
    elif type == 'radio':
        channels = baseChannels.RadioChannels
    for channel in channels:
        channel['index'] = common.GetIntSetting(channel['ch'], channel['index'])
    channels = sorted(channels, key=lambda k: k['index']) 
    for channel in channels:
        if channel['index'] != 0:
            userChannels.append(channel)
    userChannels = sorted(userChannels, key=lambda k: k['index'])
    return userChannels

def LiveChannels():
    if common.GetAddonSetting("tvShortcut") == 'true':
        name = common.GetLabelColor(common.GetLocaleString(30652), bold=True, color="none")
        common.addDir(name, 'ActivateWindow', 6, icon, infos={"Title": name}, moreData='tvchannels', isFolder=False)
    nowEPG = epg.GetNowEPG()
    channels = GetUserChannels(type='tv')
    for channel in channels:
        programs = [] if channel['tvgID'] == '' else nowEPG.get(channel['tvgID'], [])
        LiveChannel(common.GetLocaleString(channel['nameID']), channel['channelID'], channel['mode'], channel['image'], channel['module'], contextMenu=[], resKey=channel['resKey'], programs=programs, tvgID=channel['tvgID'])

def LiveChannel(name, url, mode, iconimage, module, contextMenu=[], choose=True, resKey='', bitrate='', programs=[], tvgID='', addFav=True):
    displayName = common.GetLabelColor(name, keyColor="chColor", bold=True)
    description = ''
    iconimage = common.GetIconFullPath(iconimage)
    
    if len(programs) > 0:
        contextMenu.insert(0, (common.GetLocaleString(30030), 'Container.Update({0}?url={1}&name={2}&mode=2&iconimage={3}&module=epg)'.format(sys.argv[0], tvgID, common.quote_plus(name), common.quote_plus(iconimage))))
        programTime = common.GetLabelColor("[{0}-{1}]".format(datetime.datetime.fromtimestamp(programs[0]["start"]).strftime('%H:%M'), datetime.datetime.fromtimestamp(programs[0]["end"]).strftime('%H:%M')), keyColor="timesColor")
        programName = common.GetLabelColor(common.encode(programs[0]["name"], 'utf-8'), keyColor="prColor", bold=True)
        displayName = GetChannelName(programName, programTime, displayName, channelNameFormat)
        description = '{0}[CR]{1}'.format(programName, common.encode(programs[0]["description"], 'utf-8'))
        if len(programs) > 1:
            nextProgramName = common.GetLabelColor(common.encode(programs[1]["name"], 'utf-8'), keyColor="prColor", bold=True)
            nextProgramTime = common.GetLabelColor("[{0}-{1}]".format(datetime.datetime.fromtimestamp(programs[1]["start"]).strftime('%H:%M'), datetime.datetime.fromtimestamp(programs[1]["end"]).strftime('%H:%M')), keyColor="timesColor")
            description = GetDescription(description, nextProgramTime, nextProgramName, channelNameFormat)
    if resKey == '' and bitrate == '':
        bitrate = 'best'
    else:
        if bitrate == '':
            bitrate = common.GetAddonSetting(resKey)
            if bitrate == '':
                bitrate = 'best'
        if addFav:
            contextMenu.insert(0, (common.GetLocaleString(30023), 'RunPlugin({0}?url={1}&name={2}&mode={3}&iconimage={4}&moredata=set_{5}&module={6})'.format(sys.argv[0], url, common.quote_plus(displayName), mode, common.quote_plus(iconimage), resKey, module)))
    if choose:
        contextMenu.insert(0, (common.GetLocaleString(30005), 'RunPlugin({0}?url={1}&name={2}&mode={3}&iconimage={4}&moredata=choose&module={5})'.format(sys.argv[0], url, common.quote_plus(displayName), mode, common.quote_plus(iconimage), module)))
    if contextMenu == []:
        contextMenu = None
    urlParamsData = {'name': common.GetLabelColor(name, keyColor="chColor", bold=True), 'tvgID': tvgID} if addFav else {}
    common.addDir(displayName, url, mode, iconimage, infos={"Title": displayName, "Plot": description,'mediatype': 'movie'}, contextMenu=contextMenu, moreData=bitrate, module=module, isFolder=False, isPlayable=True, addFav=addFav, urlParamsData=urlParamsData)

def GetChannelName(programName, programTime, displayName, channelNameFormat):
    if channelNameFormat == 0:
        chName = " {0} - {1} {2} ".format(displayName, programName, programTime)
    elif channelNameFormat == 1:
        chName = " {0}  {1}  {2} ".format(displayName, programTime, programName)
    elif channelNameFormat == 2:
        chName = " {0} {1} - {2} ".format(programTime, programName, displayName)
    elif channelNameFormat == 3:
        chName = "  {0}  {1}  {2} ".format(programName, programTime, displayName)
    return chName
    
def GetDescription(description, nextProgramTime, nextProgramName, channelNameFormat):
    if channelNameFormat == 0 or channelNameFormat == 1:
        description = ' {0}[CR][CR]{1} {2} '.format(description, nextProgramTime, nextProgramName)
    elif channelNameFormat == 2 or channelNameFormat == 3:
        description = ' {0}[CR][CR]{1} {2} '.format(description, nextProgramName, nextProgramTime)
    return description

def VODs():
    name = common.GetLabelColor(common.GetLocaleString(30602), bold=True, color="none")
    common.addDir(name, '', 0, common.GetIconFullPath("kan.jpg"), infos={"Title": name}, module='kan')
    name = common.GetLabelColor(common.GetLocaleString(30603), bold=True, color="none")
    common.addDir(name, '', 0, common.GetIconFullPath("mako.png"), infos={"Title": name}, module='keshet')
    name = common.GetLabelColor(common.GetLocaleString(30604), bold=True, color="none")
    common.addDir(name, '', -1, common.GetIconFullPath("13.jpg"), infos={"Title": name}, module='reshet')
    name = common.GetLabelColor(common.GetLocaleString(30606), bold=True, color="none")
    common.addDir(name, '', -1, common.GetIconFullPath("channel.png"), infos={"Title": name}, module='id')
    name = common.GetLabelColor(common.GetLocaleString(30607), bold=True, color="none")
    common.addDir(name, '', -1, common.GetIconFullPath("trump.jpg"), infos={"Title": name}, module='mako')

def RadioChannels():
    name = common.GetLabelColor(common.GetLocaleString(30608), bold=True, color="none")
    common.addDir(name, '', 0, common.GetIconFullPath("98fm.jpg"), infos={"Title": name}, module='98fm')
    name = common.GetLabelColor(common.GetLocaleString(30609), bold=True, color="none")
    common.addDir(name, '', 0, common.GetIconFullPath("radio7.jpg"), infos={"Title": name}, module='radio7')
    name = common.GetLabelColor(common.GetLocaleString(30610), bold=True, color="none")
    common.addDir(name, '', 0, common.GetIconFullPath("galei.jpg"), infos={"Title": name}, module='galei')
    name = common.GetLabelColor(common.GetLocaleString(30611), bold=True, color="none")
    common.addDir(name, '', 0, common.GetIconFullPath("radio1.jpg"), infos={"Title": name}, module='radio1')
    name = common.GetLabelColor(common.GetLocaleString(30612), bold=True, color="none")
    common.addDir(name, '', 0, common.GetIconFullPath("kan.jpg"), infos={"Title": name}, module='kan')

def EPGs():
    if common.GetAddonSetting("epgChannelFormat") == '1':
        name = common.GetLabelColor(common.GetLocaleString(30613), bold=True, color="none")
        common.addDir(name, '', 0, common.GetIconFullPath("kan.jpg"), infos={"Title": name}, module='kan')
    if common.GetAddonSetting("epgChannelFormat") == '2':
        name = common.GetLabelColor(common.GetLocaleString(30614), bold=True, color="none")
        common.addDir(name, '', 0, common.GetIconFullPath("mako.png"), infos={"Title": name}, module='keshet')
    if common.GetAddonSetting("epgChannelFormat") == '3':
        name = common.GetLabelColor(common.GetLocaleString(30615), bold=True, color="none")
        common.addDir(name, '', -1, common.GetIconFullPath("13.jpg"), infos={"Title": name}, module='reshet')
    if common.GetAddonSetting("epgChannelFormat") == '4':
        name = common.GetLabelColor(common.GetLocaleString(30616), bold=True, color="none")
        common.addDir(name, '', -1, common.GetIconFullPath("channel.png"), infos={"Title": name}, module='id')
    if common.GetAddonSetting("epgChannelFormat") == '5':
        name = common.GetLabelColor(common.GetLocaleString(30617), bold=True, color="none")
        common.addDir(name, '', -1, common.GetIconFullPath("trump.jpg"), infos={"Title": name}, module='mako')

def main():
    params = common.get_params()
    url = params.get("url", None)
    name = params.get("name", None)
    mode = int(params.get("mode", -1))
    iconimage = params.get("iconimage", None)
    module = params.get("module", None)
    
    if mode == 10:
        GetCategoriesList()
    elif mode == 1:
        LiveChannels()
    elif mode == 2:
        VODs()
    elif mode == 3:
        RadioChannels()
    elif mode == 4:
        common.Search()
    elif mode == 6:
        common.OpenSettings()
    elif mode == 12:
        common.ShowRadioPrograms()
    elif mode == 13:
        common.ShowPodcasts()
    elif mode == 14:
        common.ShowMusic()
    else:
        xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

if __name__ == '__main__':
    main()
