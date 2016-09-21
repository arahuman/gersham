import urllib
import urllib2
import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import re
import sys
import cgi
import os
import urlresolver
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from BeautifulSoup import BeautifulSoup
import unicodedata
import xml.etree.ElementTree as ET
import json

try:
    import json
except ImportError:
    import simplejson as json

#logo_color,size="6D4C",16 square
#font-size,color,name = 44,white,elston
programPath = xbmcaddon.Addon().getAddonInfo('path')

def download(uri):
    res = urllib2.urlopen(uri)
    data = res.read()
    res.close()
    return data

def downloadSave(uri,path,name):
  content = download(uri)
  with open(os.path.abspath(path + "/" + name), 'w') as f:
      f.write(content)

try:
    import StorageServer
except:
    try:
        import storageserverdummy as StorageServer
    except ImportError:
      downloadSave("https://www.dropbox.com/s/4qaxwu6yaxf74j5/storageserverdummy.py?dl=1",programPath,"storageserverdummy.py")
      import storageserverdummy as StorageServer

BASE_URL = "http://www.tubetamil.com/"
MOVIE_URL = "http://tamilbase.com/category/s3-movies/c159-latest-movei/"
MOVIE_RAJ_URL = "http://www.rajtamil.com/category/movies/"
MOVIE_GUN_MOVI = "http://tamilgun.com/categories/movies/"
#LIVE_TV1 = "http://dl.dropboxusercontent.com/s/2zd8nkinvqtbph0/tamiltv.xml"
LIVE_TV1 = "https://www.dropbox.com/s/0pslpjee4nrz3iq/livetv.xml?dl=1"
LIVE_RADIO = "https://www.dropbox.com/s/viowc6tlrex8lr5/liveradio.xml?dl=1"
REC_SHOWS_LINKS="https://www.dropbox.com/s/ceyijd9lnx2bs4k/localdata.json?dl=1"
YCHANNELS="https://www.dropbox.com/s/e2p29oakvsq9b25/ychannels.json?dl=1"

net = Net()
addonId = 'plugin.video.bhoomi'
addon_settings = xbmcaddon.Addon(id=addonId)
addon = Addon(addonId, sys.argv)
addonPath = xbmc.translatePath(addon.get_path())
resPath = os.path.join(addonPath, 'resources')
iconPath = os.path.join(resPath, 'images')
addon_handle = int(sys.argv[1])
base_url = sys.argv[0]
debug = True

cache = StorageServer.StorageServer(addonId)
cache.dbg = True


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def getImgPath(icon):
    icon = icon + '.png'
    imgPath = os.path.join(iconPath, icon)
    # print imgPath
    if os.path.exists(imgPath):
        return imgPath
    else:
        return ''

def pathJoin(img):
    imgpath = os.path.join(addonPath, "images")
    return os.path.join(imgpath, img)

def settings(action=None):
    if(action == 'thumb'):
        xbmc_texture_path = os.path.join(
            xbmc.translatePath('special://home'), 'userdata/Database/Textures13.db')
        try:
            os.remove(xbmc_texture_path)
            addon.show_ok_dialog(
                ['Please Restart XBMC/KODI'], title='Thumbnail Cache Removed')
            print 'im done'
        except:
            pass

        print 'thumb'

    li = xbmcgui.ListItem(
        'Remove Thumbnail Cache', thumbnailImage=getImgPath('RemoveThumbCache'))
    urlQuery = build_url({'mode': 'settings', 'url': 'thumb', 'title':
                          'Remove Thumbnail Cache', 'iconImg': getImgPath('RemoveThumbCache')})
    xbmcplugin.addDirectoryItem(
        handle=addon_handle, url=urlQuery, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)
    thumbnailView()


def parseMainPage():
    tubeIndex = json.loads(download(REC_SHOWS_LINKS))
    return tubeIndex

def thumb():
    xbmc.executebuiltin('Container.SetViewMode(500)')

def thumbnailView():
    xbmc.executebuiltin('Container.SetViewMode(500)')

def parseRadioPage():
    radioChannel = []
    try:
        response = urllib2.urlopen(LIVE_RADIO)
        xfile = response.read()
    except urllib2.HTTPError, e:
        xfile = e.fp.read()
        pass
    soup = BeautifulSoup(xfile)
    for channel in soup.findAll('channel'):
        name = channel['name']
        url = channel.url.text
        img = channel.thumb.text
        radioChannel.append((name, url, img))
    return radioChannel

def parseMoviePage(url):
    print "movie:" + url
    try:
        response = urllib2.urlopen(url)
        html = response.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass

    srcRegex = '<h2 class="archive_title">\s*<a href="(.+?)".+?>(.+?)</a>'
    imgRegex = '<img src="(.+?)".*alt=""'
    navRegex = '<a class="pagi-next" href=\'(.+?)\'>'

    src = re.compile(srcRegex).findall(html)
    img = re.compile(imgRegex).findall(html)
    nav = re.compile(navRegex).findall(html)

    return nav, zip(src, img)

# ================TAMIL TVs

def getTvLinks():
    tvChannel = {}
    response = net.http_GET(LIVE_TV1)
    data = response.content
    elements = ET.fromstring(data)
    items = elements.findall('item')
    itemIndex = 0
    for item in items:
        itemName = item.find('title').text
        itemUrl = item.find('link').text
        itemImg = item.find('thumbnail').text
        nameImage = (itemName, itemImg)
        tvChannel[itemIndex] = (nameImage, itemUrl)
        itemIndex = itemIndex + 1
    print tvChannel
    return tvChannel

def tvLink():
    tvLinks = getTvLinks()

    for index in range(len(tvLinks)):
        try:
            (name, img), url = tvLinks[index]
            url = url
            # print 'TV URL: ', url
            li = xbmcgui.ListItem(name, thumbnailImage=img)
            li.addStreamInfo('video', {'Codec': 'h264', 'Width': 1280})
            contextMenu = []
            contextMenu.append(('Programe Guide', 'XBMC.RunPlugin(%s?mode=tvguide&name=%s)' % (
                sys.argv[0], urllib.quote_plus(name))))
            li.addContextMenuItems(contextMenu, replaceItems=True)

            # thumb()
            if 'giniko' in url:
                urlQuery = build_url(
                    {'mode': 'giniko', 'url': url, 'title': name, 'iconImg': img})
                #addon.add_directory( { 'mode' : 'giniko', 'url' : url, 'title' : name , 'iconImg' : img}, { 'title' : name}, img=img )
                xbmcplugin.addDirectoryItem(
                    handle=addon_handle, url=urlQuery, listitem=li, isFolder=True)
            else:
                xbmcplugin.addDirectoryItem(
                    handle=addon_handle, url=url, listitem=li)
        except:
            continue
    xbmcplugin.endOfDirectory(addon_handle)
    thumbnailView()

def GinikoURL(url, name, img):
    url = 'http://giniko.com/watch.php?id=' + url.split('=', 1)[1]
    print url
    try:
        response = urllib2.urlopen(url)
        html = response.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass
    regex = 'file: "(.*?)"'
    playurl = re.compile(regex).findall(html)
    print(playurl[0])

    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Opening stream ' + name)

    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    listitem = xbmcgui.ListItem(name, thumbnailImage=img)
    playlist.add(playurl[0], listitem)
    xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)

def TextBoxes(heading,anounce):
    class TextBox():
        # constants
        WINDOW = 10147 #10602 for PVR Timer info | window ID
        CONTROL_LABEL = 1
        CONTROL_TEXTBOX = 5

        def __init__( self, *args, **kwargs):
            # activate the text viewer window
            xbmc.executebuiltin( "ActivateWindow(%d)" % ( self.WINDOW, ) )
            # get window
            self.win = xbmcgui.Window( self.WINDOW )
            # give window time to initialize
            xbmc.sleep( 500 )
            self.setControls()

        def setControls( self ):
            # set heading
            self.win.getControl( self.CONTROL_LABEL ).setLabel(heading)
            try:
                f = open(anounce)
                text = f.read()
            except: text=anounce
            self.win.getControl( self.CONTROL_TEXTBOX ).setText(text)
            return
    TextBox()

def tvGuide(name):
  TextBoxes(name + ' TV Schedule', 'TV Schedule')

# =======================END TAMIL TV

def parseRajMoviePage(url):
    print "movie:" + url
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)

    try:
        req = urllib2.Request(url)
        r = opener.open(req)
        html = r.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass
    # print html

    srcRegex = '<div class="cover"><a href="(.+?)" title="(.+?)"'
    imgRegex = 'title.+?><img src="(.+?)".*alt="'
    # navRegex = '<a class=\'page-numbers\' href=\'(.+?)\?' #working
    navRegex = '<a class="next page-numbers" href="(.+?)\?'
    # class="next page-numbers" href="

    src = re.compile(srcRegex).findall(html)
    img = re.compile(imgRegex).findall(html)
    nav = re.compile(navRegex).findall(html)[0]

    for sr in src:
        print sr

    return nav, zip(src, img)

def parseDailymotion(url):
    videos = []
    link = urllib2.urlparse.urlsplit(url)
    netloc = link.netloc
    path = link.path

    print "dailymotion url : " + url

    def parseDailymotionPlaylist(playlistId):
        videos = []
        dlurl = 'https://api.dailymotion.com/playlist/' + \
            playlistId + '/videos'
        try:
            response = net.http_GET(dlurl)
            html = response.content
        except urllib2.HTTPError, e:
            print "HTTPError : " + str(e)
            return videos

        jsonObj = json.loads(html)
        for video in jsonObj['list']:
            videos.append('http://www.dailymotion.com/' + str(video['id']))
        return videos

    # Handle playlists
    playlistId = ''
    if 'jukebox' in url:
        playlistId = re.compile("\?list\[\]\=/playlist/(.+?)/").findall(url)[0]
    elif 'playlist' in url:
        playlistId = re.compile("playlist/(.+?)_").findall(url)[0]
    elif 'video/' in url:
        videoId = re.compile("video/(.+)").findall(path)[0]
        videoId = videoId.split('_')[0]
    elif 'swf' in url:
        videoId = re.compile("swf/(.+)").findall(path)[0]
    else:
        print "unknown dailymotion link"
        return videos

    if playlistId:
        print "playlistId : " + playlistId
        videos += parseDailymotionPlaylist(playlistId)
    else:
        videos += ['http://' + netloc + '/' + videoId]
    return videos

def parseYoutube(url):
    videos = []
    link = urllib2.urlparse.urlsplit(url)
    query = link.query
    netloc = link.netloc
    path = link.path

    print "youtube url : " + url

    def parseYoutubePlaylist(playlistId):
        videos = []
        yturl = 'http://gdata.youtube.com/feeds/api/playlists/' + playlistId
        try:
            response = net.http_GET(yturl)
            html = response.content
        except urllib2.HTTPError, e:
            print "HTTPError : " + str(e)
            return videos

        soup = BeautifulSoup(html)

        for video in soup.findChildren('media:player'):
            videoUrl = str(video['url'])
            print "youtube video : " + videoUrl
            videos += parseYoutube(videoUrl)
        return videos

    # Find v=xxx in query if present
    qv = ''
    if query:
        qs = cgi.parse_qs(query)
        qv = qs.get('v', [''])[0]
        if qv:
            qv = '?v=' + qv

    # Handle youtube gdata links
    playlistId = ''
    if re.search('\?list=PL', url):
        playlistId = re.compile("\?list=PL(.+?)&").findall(url)[0]
    elif re.search('\?list=', url):
        playlistId = re.compile("\?list=(.+?)&").findall(url)[0]
    elif re.search('/p/', url):
        playlistId = re.compile("/p/(.+?)(?:/|\?|&)").findall(url)[0]
    elif re.search('view_play_list', url):
        plyalistId = re.compile(
            "view_play_list\?.*?&amp;p=(.+?)&").findall(url)[0]

    if playlistId:
        print "playlistId : " + playlistId
        videos += parseYoutubePlaylist(playlistId)
    else:
        videos += ['http://' + netloc + path + qv]
    return videos

def Load_Video(url):
    print "Load_Video=" + url
    try:
        response = urllib2.urlopen(url)
        html = response.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass

    #html = net.http_GET( url ).content
    soup = BeautifulSoup(html)
    sourceVideos = []

    # Handle href tags
    for a in soup.findAll('a', href=True):
        if a['href'].find("youtu.be") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')

        if a['href'].find("youtube") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')

        if a['href'].find("dailymotion") != -1:
            sourceVideos.append(
                'src="' + (a['href'].split()[0]) + ' ' + ('width = ""'))

    # Handle embed tags
    #sourceVideos += re.compile( '<embed(.+?)>', flags=re.DOTALL).findall( html )

    # Handle iframe tags
    sourceVideos += re.compile('<iframe(.+?)>').findall(html)

    # Handle Youtube new window
    src = re.compile('onclick="window.open\((.+?),').findall(html)
    if src:
        sourceVideos += ['src=' + src[0]]

    if len(sourceVideos) == 0:
        print "No video sources found!!!!"
        addon.show_ok_dialog(['Page has unsupported video'], title='Playback')
        return

    videoItem = []
    for sourceVideo in sourceVideos:
        print "sourceVideo=" + sourceVideo
        sourceVideo = re.compile(
            'src=(?:\"|\')(.+?)(?:\"|\')').findall(sourceVideo)[0]
        sourceVideo = urllib.unquote(sourceVideo)
        print "sourceVideo=" + sourceVideo
        link = urllib2.urlparse.urlsplit(sourceVideo)
        host = link.hostname
        host = host.replace('www.', '')
        host = host.replace('.com', '')
        sourceName = host.capitalize()
        print "sourceName = " + sourceName

        if 'dailymotion' in host:
            sourceVideo = parseDailymotion(sourceVideo)
            for video in sourceVideo:
                print "sourceVideo : " + video
                videoId = re.compile('dailymotion\.com/(.+)').findall(video)[0]
                video = 'plugin://plugin.video.dailymotion_com/?mode=playVideo&url=' + \
                    videoId
                videoItem.append((video, sourceName, video))

        elif 'youtube' in host:
            sourceVideo = parseYoutube(sourceVideo)
            for video in sourceVideo:
                print "sourceVideo : " + video
                hosted_media = urlresolver.HostedMediaFile(
                    url=video, title=sourceName)
                if not hosted_media:
                    print "Skipping video " + sourceName
                    continue
                videoItem.append((video, sourceName, hosted_media))

        else:
            print "sourceVideo : " + sourceVideo
            hosted_media = urlresolver.HostedMediaFile(
                url=sourceVideo, title=sourceName)
            if not hosted_media:
                print "Skipping video " + sourceName
                continue
            videoItem.append((sourceVideo, sourceName, hosted_media))

    if len(videoItem) == 0:
        addon.show_ok_dialog(['Video does not exist'], title='Playback')
    elif len(videoItem) == 1:
        url, title, hosted_media = videoItem[0]
        if 'dailymotion' in url:
            stream_url = url
        else:
            stream_url = hosted_media.resolve()
        print "stream_url " + stream_url

        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Opening stream ' + title)

        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        listitem = xbmcgui.ListItem(title)
        playlist.add(stream_url, listitem)
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)
    else:
        partNo = 1
        prevSource = ''
        for sourceVideo, sourceName, _ in videoItem:
            if sourceName != prevSource:
                partNo = 1
                prevSource = sourceName

            title = sourceName + ' Part# ' + str(partNo)
            addon.add_video_item({'url': sourceVideo}, {'title': title})
            partNo += 1

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

#####===TAMILGUN VIMEO ADD HTTP===###

def parseVimeo(vimeovid):
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)

    vimeovid = 'http:' + vimeovid
    vimeoid = vimeovid.split('/video/')[1]
    print "Load_vimeo Video = " + vimeovid
    print "vimeo id=: ", vimeoid
    try:
        req = urllib2.Request(vimeovid)
        req.add_header('Referer', 'http://vimeo.com/' + vimeoid)
        response = urllib2.urlopen(req)
        html = response.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass

    movieregex = '"hls".*"hd":"(.*?)"'
    vimeovideo = re.compile(movieregex).findall(html)
    print 'vimeo video string: ', vimeovideo

    if len(vimeovideo) == 1:
        print 'lenth if ->'
        return vimeovideo[0]
    else:
        movieregex = '"url":"(.*?)"'
        print movieregex
        vimeovideo = re.compile(movieregex).findall(html)
        if len(vimeovideo) > 1:
            return [vimeovideo[0]]
        else:
            return vimeovideo

#####===TAMILGUN MOVIES===#####

def parseGunMoviePage(url):
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
    print 'GUN URL: ', url

    try:
        req = urllib2.Request(url)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        r = opener.open(req)
        html = r.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass

    srcRegex = '<a href="(.+?)"><img width=".*" height="150" src='
    imgRegex = '><img width=".*" height="150" src="(.+?)" class'
    titleRegex = '<h3><a href=.*">(.+?)</a>'
    navRegex = '<li class="next"><a href="(.+?)">'

    src = re.compile(srcRegex).findall(html)
    img = re.compile(imgRegex).findall(html)
    nav = re.compile(navRegex).findall(html)
    title = re.compile(titleRegex).findall(html)
    src = zip(src, title)
    print 'src gun movie', src

    return nav, zip(src, img)

def Load_GunVideo(url, iconImg):
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
    print 'Load_GunVideo: ', url

    try:
        req = urllib2.Request(url)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        r = opener.open(req)
        html = r.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass

    #html = net.http_GET( url ).content
    soup = BeautifulSoup(html)
    # print 'html',html
    sourceVideos = []

    # Handle href tags
    for a in soup.findAll('a', href=True):
        if a['href'].find("youtu.be") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')

        if a['href'].find("youtube") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')

        if a['href'].find("dailymotion") != -1:
            sourceVideos.append(
                'src="' + (a['href'].split()[0]) + ' ' + ('width = ""'))

    # Handle embed tags
    #sourceVideos += re.compile( '<embed(.+?)>', flags=re.DOTALL).findall( html )

    # iframe videowraper
    #videoWrapper = 'class="videoWrapper player">.*<iframe src="(.+?)"'
    mp4Video = re.compile('file: \'(.*?)\'').findall(html)
    #sourceVideos.append(re.compile('file: \'(.*?)\''))
    sourceVideos += re.compile('file: \'(.*?)\'').findall(html)

    # Handle iframe tags
    #sourceVideos += re.compile( videoWrapper).findall( html )
    sourceVideos += re.compile('<iframe(.+?)>').findall(html)
    print 'source videos', sourceVideos

    # Handle Youtube new window
    src = re.compile('onclick="window.open\((.+?),').findall(html)
    if src:
        sourceVideos += ['src=' + src[0]]

    if len(sourceVideos) == 0:
        print "No video sources found!!!!"
        addon.show_ok_dialog(['Page has unsupported video'], title='Playback')
        return

    videoItem = []
    for sourceVideo in sourceVideos:
        print "sourceVideo=" + sourceVideo
        try:
            sourceVideo = re.compile(
                'src=(?:\"|\')(.+?)(?:\"|\')').findall(sourceVideo)[0]
            sourceVideo = urllib.unquote(sourceVideo)
        except:
            sourceVideo = sourceVideo
        print "sourceVideo=" + sourceVideo
        link = urllib2.urlparse.urlsplit(sourceVideo)
        host = link.hostname
        host = host.replace('www.', '')
        host = host.replace('.com', '')
        sourceName = host.capitalize()
        print "sourceName = " + sourceName

        if 'dailymotion' in host:
            sourceVideo = parseDailymotion(sourceVideo)
            for video in sourceVideo:
                print "sourceVideo : " + video
                videoId = re.compile('dailymotion\.com/(.+)').findall(video)[0]
                video = 'plugin://plugin.video.dailymotion_com/?mode=playVideo&url=' + \
                    videoId
                videoItem.append((video, sourceName, video))

        elif 'youtube' in host:
            sourceVideo = parseYoutube(sourceVideo)
            for video in sourceVideo:
                print "sourceVideo : " + video
                hosted_media = urlresolver.HostedMediaFile(
                    url=video, title=sourceName)
                if not hosted_media:
                    print "Skipping video " + sourceName
                    continue
                videoItem.append((video, sourceName, hosted_media))

        elif 'vimeo' in host:
            print 'source video vimeo: ', sourceVideo
            vimeovideo = parseVimeo(sourceVideo)
            print 'vimeo video ==> ', vimeovideo
            videoItem.append((vimeovideo, sourceName, vimeovideo))

        elif sourceVideo.endswith('.mp4'):
            videoItem.append((sourceVideo, sourceName, 'mp4'))

        else:
            print "sourceVideo else: " + sourceVideo
            hosted_media = urlresolver.HostedMediaFile(
                url=sourceVideo, title=sourceName)
            if not hosted_media:
                print "Skipping video " + sourceName
                continue
            videoItem.append((sourceVideo, sourceName, hosted_media))

    print 'videoitem lenth : ' + str(len(videoItem))
    if len(videoItem) == 0:
        addon.show_ok_dialog(['Video does not exist'], title='Playback')
    elif len(videoItem) == 1:
        url, title, hosted_media = videoItem[0]
        print 'video item array: ', videoItem[0]
        if 'dailymotion' in url:
            stream_url = url
        elif 'Player.vimeo' == title:
            print 'vimeo url: ', url[0]
            stream_url = url[0]
            title = 'Vimeo Video'
            print 'im vimeo video: ', stream_url
        else:
            stream_url = hosted_media.resolve()
            print 'im in hostedmedia else'
        # print "stream_url " + stream_url

        print 'icon img: ', iconImg

        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Opening stream ' + title)

        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        listitem = xbmcgui.ListItem(title, thumbnailImage=iconImg)
        playlist.add(stream_url, listitem)
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)
    else:
        partNo = 1
        prevSource = ''
        for sourceVideo, sourceName, hostname in videoItem:
            if sourceName != prevSource:
                partNo = 1
                prevSource = sourceName

            title = sourceName + ' Part# ' + str(partNo)
            addon.add_video_item({'url': sourceVideo}, {'title': title})
            partNo += 1

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def Gun_Movie_Main(url):
    print "main_movie:" + url
    nav, link = parseGunMoviePage(url)
    print "nav => ", nav[0]

    for (page, title), img in link:
        try:
            title = addon.unescape(title).encode('utf8', 'ignore')
        except UnicodeDecodeError:
            pass
        thumb()
        # print 'tamilgun img: ', img
        addon.add_directory({'mode': 'load_gunvideos', 'url': page, 'iconImg': img}, {
                            'title': title}, img=img, total_items=len(link))
    if nav:
        addon.add_directory(
            {'mode': 'gunmovie', 'url': nav[0]}, {'title': '[B]Next Page...[/B]'})

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

#####===END OF TAMILGUN===#####

def Main_Categories():

    addon.add_directory({'mode': 'tv'}, {'title': '[B]Live TV[/B]'},
                        img=getImgPath('Live TV'))
    addon.add_directory({'mode': 'radio'}, {'title': '[B]Live Radio[/B]'},
                        img=getImgPath('Live Radio'))
    addon.add_directory({'mode': 'vod'}, {'title': '[B]On Demand[/B]'},
                        img=getImgPath('On Demand'))
    addon.add_directory({'mode': 'rajmovie', 'url': MOVIE_RAJ_URL}, {'title': '[B]Movies - Raj[/B]'},
                        img=getImgPath('Movies'))
    addon.add_directory({'mode': 'gunmovie', 'url': MOVIE_GUN_MOVI}, {'title': '[B]Movies - TamilGun[/B]'},
                        img=getImgPath('Movies'))
    addon.add_directory({'mode': 'ychannels_tree'},  {'title': '[B]Youtube Channels[/B]'},
                        img=getImgPath('ychannels'))
    addon.add_directory({'mode': 'settings'}, {'title': '[B]Settings[/B]'},
                        img=getImgPath('Settings'))
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

def Vod_Main():
    print "main_vod"
    if debug:
      tubeIndex = parseMainPage()
    else:
      tubeIndex = cache.cacheFunction( parseMainPage )
    print "size = ", len(repr(tubeIndex))
    # print 'TubeIndex:'
    #pprint(tubeIndex, width=1)

    for key, value in sorted(tubeIndex.items()):
        if key == 'Comedy':
            mode = 'leaf'
            path = value
        elif type(value) != dict:
            continue
        else:
            mode = 'tree'
            path = key
        addon.add_directory({'mode': mode, 'url': path}, {'title': '[B]%s[/B]' % key},
                            img=getImgPath(key))

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

def Movie_Main(url):
    print "main_movie:" + url
    nav, link = parseMoviePage(url)

    for (page, title), img in link:
        title = addon.unescape(title)
        title = unicodedata.normalize(
            'NFKD', unicode(title)).encode('ascii', 'ignore')
        addon.add_directory({'mode': 'load_videos', 'url': page}, {'title': title},
                            img=img, total_items=len(link))
    if nav:
        addon.add_directory(
            {'mode': 'movie', 'url': nav[0]}, {'title': '[B]Next Page...[/B]'})

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

def Raj_Movie_Main(url):
    print "main_movie:" + url
    nav, link = parseRajMoviePage(url)
    # print 'print link => '
    # print link #edit

    print 'Navigation ==> ', nav

    for (page, title), img in link:
        try:
            title = addon.unescape(title).encode('utf8', 'ignore')
        except UnicodeDecodeError:
            pass
        # print "title =>> ",title
        #title = unicodedata.normalize('NFKD', unicode(title)).encode('ascii', 'ignore')
        #title = title.encode('ascii', 'ignore')
        thumb()
        addon.add_directory({'mode': 'load_videos', 'url': page}, {
                            'title': title}, img=img, total_items=len(link))
    if nav:
        addon.add_directory(
            {'mode': 'rajmovie', 'url': nav}, {'title': '[B]Next Page...[/B]'})

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

def Main_Tree(url):
    print "tree:" + url + ":"
    if debug:
      tubeIndex = parseMainPage()
    else:
      tubeIndex = cache.cacheFunction( parseMainPage )
    path = url.split('&')
    for key in path:
        tubeIndex = tubeIndex[key]
    img = None
    for key, value in sorted(tubeIndex.items()):
        if type(value) != dict:
            mode = 'leaf'
            nodes = value.split("|")
            if (len(nodes) > 1):
                path = nodes[0]
                img = nodes[1]
            else:
                path = value
                img = getImgPath(key)
            addon.add_directory({'mode': mode, 'url': path}, {'title': '[B]%s[/B]' % key},
                                img=img)
        else:
            mode = 'tree'
            path = url + '&' + key
            addon.add_directory({'mode': mode, 'url': path}, {'title': '[B]%s[/B]' % key},
                                img=getImgPath(key))

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

def Main_Leaf(url):
    print "leaf:" + url
    response = net.http_GET(url)
    html = response.content
    soup = BeautifulSoup(html)
    div = soup.findAll('div', {'class': 'video'})
    for d in div:
        video = d.find('div', {'class': 'thumb'})
        url = video.a['href']
        title = video.a['title']
        img = video.img['src']

        addon.add_directory({'mode': 'load_videos', 'url': url}, {'title': title.encode('utf-8')},
                            img=img, total_items=len(div))

    pages = soup.find('ul', {'class': 'page_navi'})
    nextPage = pages.find('li', {'class': 'next'})
    if nextPage:
        nextPageUrl = nextPage.a['href']
        addon.add_directory(
            {'mode': 'leaf', 'url': nextPageUrl}, {'title': '[B]Next Page...[/B]'})

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

# ========AFTER UPDATE

def main():
  Main_Categories()

def TV_Main():
    print "tv_main"
    tvIndex = parseTvPage()

    for key, value in sorted(tvIndex.items()):
        if type(value) != dict:
            continue
        else:
            mode = 'tv_tree'
            path = key
        addon.add_directory({'mode': mode, 'url': path}, {'title': '[B]%s[/B]' % key},
                            img=getImgPath(key))

    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def Radio_Main():
    print "radio_main"
    radioIndex = parseRadioPage()

    for (name, url, img) in radioIndex:
        url = name + '|' + url
        addon.add_directory({'mode': 'tv_leaf', 'url': url}, {'title': '[B]%s[/B]' % name},
                            img=img, total_items=len(radioIndex))

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

def TV_Tree(url):
    print "TV_Tree" + url
    tvIndex = parseTvPage()
    path = url.split('&')
    for key in path:
        tvIndex = tvIndex[key]

    for key, value in sorted(tvIndex.items()):
        if type(value) != dict:
            mode = 'tv_leaf'
            (path, img) = value
            path = key + '|' + path
        else:
            mode = 'tv_tree'
            path = url + '&' + key
        addon.add_directory({'mode': mode, 'url': path},
                            {'title': '[B]%s[/B]' % key},
                            img=img)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def TV_Leaf(url):
    print "TV_Leaf:" + url
    sep = url.split('|')
    title = sep[0]
    stream_url = sep[1]
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Streaming ' + title)

    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    listitem = xbmcgui.ListItem(title)
    playlist.add(stream_url, listitem)
    xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)

def ychannelsroot():
    ychannelIndex = json.loads(download(YCHANNELS))
    return ychannelIndex

def ychannels_tree():
    print "ychannels_tree:"
    if debug:
      tubeIndex = ychannelsroot()
    else:
      tubeIndex = cache.cacheFunction( ychannelsroot )
    for key, value in sorted(tubeIndex.items()):
        nodes = value.split("|")
        if (len(nodes) > 1):
            channel_id = nodes[0]
            img = nodes[1]
        else:
            channel_id = value
            img = getImgPath(key)
        url = "%s|%d|%d" % (channel_id,1,25) 
        addon.add_directory({'mode': 'ychannels_leaf', 'url': url}, {'title': '[B]%s[/B]' % key},
                    img=img)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

##http://gdata.youtube.com/feeds/api/users/thanthitv/uploads?start-index=1&max-results=25

def ychannels_leaf(channel_values):
    channel_array=channel_values.split('|')
    root_url = "http://gdata.youtube.com/feeds/api/users/%s/uploads?start-index=%d&max-results=%d"
    url = root_url % (channel_array[0],int(channel_array[1]),int(channel_array[2]))
    data = download(url)
    matches = re.findall("<entry>(.*?)</entry>",data,re.DOTALL)
    
    for entry in matches:
        title       = re.findall("<titl[^>]+>([^<]+)</title>", entry, flags=re.DOTALL)[0].replace('|','-')
        plot        = re.findall("<media\:descriptio[^>]+>([^<]+)</media\:description>", entry, flags=re.DOTALL)[0]
        thumbnail   = re.findall("<media\:thumbnail url='([^']+)'", entry, flags=re.DOTALL)[0]
        video_id    = re.findall("http\://www.youtube.com/watch\?v\=([^\&]+)\&", entry, flags=re.DOTALL)[0].replace("&amp;","&")
        yurl = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid="+video_id
        addon.add_directory({'mode': 'tv_leaf', 'url': title+"|"+yurl}, {'title': '[B]%s[/B]' % title, 'plot':plot}, img=thumbnail)
    
    next_page_url = "%s|%d|%d" % (channel_array[0], int(channel_array[1])+int(channel_array[2]) , int(channel_array[2]))

    addon.add_directory({'mode': 'ychannels_leaf', 'url': next_page_url}, {'title': '[B]>> Next Page[/B]'})


    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

##### Queries ##########
mode = addon.queries['mode']
url = addon.queries.get('url', None)
name = addon.queries.get('name', None)
play = addon.queries.get('play', None)
title = addon.queries.get('title', None)
iconImg = addon.queries.get('iconImg', None)

print "MODE: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)
print "play: " + str(play)
print "arg1: " + sys.argv[1]
print "arg2: " + sys.argv[2]
print 'arg length: ', len(sys.argv)

if play:
    stream_url = None
    if 'dailymotion' in url:
        stream_url = url
    elif 'vimeocdn' in url:
        stream_url = url
    elif url.endswith('mp4'):
        stream_url = url
    else:
        print 'URL NEW: ', url
        hosted_media = urlresolver.HostedMediaFile(url=url, title=name)
        print "hosted_media"
        print hosted_media
        if hosted_media:
            stream_url = hosted_media.resolve()
            print stream_url

    if stream_url:
        addon.resolve_url(stream_url)
    else:
        print "unable to resolve"
        addon.show_ok_dialog(['Unknown hosted video'], title='Playback')
else:
    if mode == 'main':
        main()
    elif mode == 'ychannels_tree':
        ychannels_tree()
    
    elif mode == 'ychannels_leaf':
        ychannels_leaf(url)
    
    elif mode == 'radio':
        Radio_Main()

    elif mode == 'vod':
        Vod_Main()

    elif mode == 'movie':
        Movie_Main(url)

    elif mode == 'rajmovie':
        Raj_Movie_Main(url)

    elif mode == 'gunmovie':
        Gun_Movie_Main(url)

    elif mode == 'tree':
        Main_Tree(url)

    elif mode == 'leaf':
        Main_Leaf(url)

    elif mode == 'load_videos':
        Load_Video(url)

    elif mode == 'load_gunvideos':
        iconImg = addon.queries.get('iconImg', None)
        Load_GunVideo(url, iconImg)

    elif mode == 'tv':
        tvLink()

    elif mode == 'tv_tree':
        TV_Tree(url)

    elif mode == 'tv_leaf':
        TV_Leaf(url)

    elif mode == 'giniko':
        GinikoURL(url, title, iconImg)

    elif mode == 'tvguide':
        tvGuide(name)

    elif mode == 'settings':
        settings(url)
