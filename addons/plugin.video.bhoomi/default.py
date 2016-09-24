# import urllib
# import urllib2
# import xbmcplugin
# import xbmcgui
# import xbmc
# import xbmcaddon
# import re
# import sys
# import cgi
# import os
# import urlresolver
# from t0mm0.common.addon import Addon
# from t0mm0.common.net import Net
# from BeautifulSoup import BeautifulSoup
# import unicodedata
# import xml.etree.ElementTree as ET
# import json
# import update

import urllib, urllib2
import xbmcplugin, xbmcgui, xbmc, xbmcaddon
import re, sys, cgi, os
import urlresolver
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from BeautifulSoup import BeautifulSoup
import unicodedata
import xml.etree.ElementTree as ET
import time


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

YOGI_URL = "http://tamilyogi.cc"

BASE_URL = "http://www.tubetamil.com/"
MOVIE_URL = "http://tamilbase.com/category/s3-movies/c159-latest-movei/"
MOVIE_RAJ_URL = "http://www.rajtamil.com/category/movies/"
MOVIE_GUN_MOVI = "http://tamilgun.com/categories/movies/"
EINTHUSAN      = "http://www.einthusan.com/"

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
addonLocation = xbmc.translatePath(os.path.join('special://home', 'addons', addonId))


import string
digs = string.digits + string.letters


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def get_pack(file):
    import hashlib
    return hashlib.md5(open(os.path.join(addonLocation,file)).read()).hexdigest()

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

def int2base(x, base):
    if x < 0: sign = -1
    elif x == 0: return digs[0]
    else: sign = 1
    x *= sign
    digits = []
    while x:
        digits.append(digs[x % base])
        x /= base
    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)

def unpack(p, a, c, k, e=None, d=None):
    ''' unpack
    Unpacker for the popular Javascript compression algorithm.

    @param  p  template code
    @param  a  radix for variables in p
    @param  c  number of variables in p
    @param  k  list of c variable substitutions
    @param  e  not used
    @param  d  not used
    @return p  decompressed string
    '''
    # Paul Koppen, 2011
    for i in xrange(c-1,-1,-1):
        if k[i]:
            p = re.sub('\\b'+int2base(i,a)+'\\b', k[i], p)
    return p

def thumb():
    xbmc.executebuiltin('Container.SetViewMode(500)')

def thumbnailView():
    xbmc.executebuiltin('Container.SetViewMode(500)')

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

def downloadPythonFile(programPath, pyfile):
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)    
    urlStr = "http://cyberrule.com/tv/tamilkodi/" + pyfile
    req = urllib2.Request(urlStr)
    r = opener.open(req)
    the_page = r.read()

    with open(os.path.abspath(programPath + "/" + pyfile), 'w') as f:
        f.write(the_page)



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def main():

    addon.add_directory({'mode': 'yogi_root', 'url': YOGI_URL}, {'title' : '[B]Movies - Yogi[/B]'},
                        img=getImgPath('yogi'))
    addon.add_directory({'mode': 'raj_root', 'url': MOVIE_RAJ_URL}, {'title': '[B]Movies - Raj[/B]'},
                        img='https://lh3.googleusercontent.com/-D9l_X6D0Fp0/VTBYHBgDB0I/AAAAAAAACPE/npl7vo6x_-Q/s300-Ic42/tamilmovies_rajtamil.png')
    addon.add_directory({'mode': 'gun_root', 'url': MOVIE_GUN_MOVI}, {'title': '[B]Movies - TamilGun[/B]'},
                        img='https://lh3.googleusercontent.com/-H5GL4O0J95s/VTBYJXyNY9I/AAAAAAAACRQ/6Xnv1fAwrfY/s300-Ic42/tamilmovies_tamilgun.png')
    addon.add_directory({'mode': 'einthusan', 'url': EINTHUSAN}, {'title': '[B]Movies - Einthusan[/B]'},
                        img='https://lh3.googleusercontent.com/-V0sr2aR40lA/VjW3Z4zHcZI/AAAAAAAAClM/G7iXP0Xrhw4/s300-Ic42/einthusan.png')
    addon.add_directory({'mode': 'settings'}, {'title': '[B]Settings[/B]'},
                        img='https://lh3.googleusercontent.com/-XmQchEnyeWs/VTBYFAUm6_I/AAAAAAAACOs/AfaY71aUFz0/s300-Ic42/settings.png')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def yogi_root(url):
    addon.add_directory({'mode': 'yogi_movies_list', 'url': url + '/category/tamilyogi-dvdrip-movies/'}, {'title' : '[B]DVD HQ Movies[/B]'}, img=getImgPath('Movies'))
    addon.add_directory({'mode': 'yogi_movies_list', 'url': url + '/category/tamilyogi-full-movie-online'}, {'title' : '[B]New Movies[/B]'}, img=getImgPath('Movies'))
    addon.add_directory({'mode': 'yogi_movies_list', 'url': url + '/category/tamilyogi-bluray-movies/'}, {'title' : '[B]New Movies[/B]'}, img=getImgPath('Movies'))    
    addon.add_directory({'mode': 'yogi_movies_list', 'url': url + '/category/tamilyogi-dubbed-movies-online/'}, {'title' : '[B]Dubbed Movies[/B]'}, img=getImgPath('Movies'))
    addon.add_directory({'mode': 'yogi_movies_list', 'url': url + '/tamil-hd-movies-tamilyogi/'}, {'title' : '[B]HD Movies[/B]'}, img=getImgPath('Movies'))
    addon.add_directory({'mode': 'yogi_movies_list', 'url': url + '/tamil-new-movies-tamilyogi/'}, {'title' : '[B]HD Trailers[/B]'}, img=getImgPath('Movies'))
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def yogi_movies_list(url):
    response = net.http_GET(url)
    data = response.content
    # Find the movies in the current category
    match=re.compile('<a href="(.+?)" title="(.+?)"><img src="(.+?)"').findall( data )
    for movurl,name,thumb in match:
        addon.add_directory({'mode': 'yogi_play', 'url': movurl, 'title' : name }, {'title' : name }, img=thumb)
    match=re.compile('<a class="next page-numbers" href="(.+?)">').findall(data)
    for page in match:
        addon.add_directory({'mode': 'yogi_movies_list', 'url': page}, {'title' : 'Next Page >>' }, img="https://lh3.googleusercontent.com/-NsVeHCUW0lo/V4b8r67FVSI/AAAAAAAAD7U/G1ifDqs0nFENPck0-oKCQgc3-Gdm_JM7QCCo/s574/next_574x358.png" )
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

def yogi_play(url,title,iconImg):
    response = net.http_GET(url)
    data = response.content
    match=re.search('IFRAME SRC="(.+?)"',data).group(1)
    
    response = net.http_GET(match)
    data = response.content

    stream_url=re.search('{file:"(.+?)"',data).group(1)
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Please wait ....', 'Opening stream ' + "\n" +title )

    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    listitem = xbmcgui.ListItem(title, thumbnailImage=iconImg)
    playlist.add(stream_url, listitem)
    xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)

def raj_root( url ):
    print "main_movie:" + url
    nav, link = raj_parse_page( url )
    #print 'print link => '
    #print link #edit
 
    print 'Navigation ==> ',nav
    index = 1
    for ( page, title ), img in link:
        if index == 2 or index == 3:
            stitle = 'test'
        try:
            title =  addon.unescape(title).encode('utf8', 'ignore')
        except UnicodeDecodeError:
            title = 'Unicodechar'
            pass
        title = title.replace('Watch ', '', 1)
        title = title.replace(' Movie Online', '', 1)
        title = title.replace(' movie online', '', 1)
        #print "title =>> ",title
        #title = unicodedata.normalize('NFKD', unicode(title)).encode('ascii', 'ignore')
        #title = title.encode('ascii', 'ignore')
        #print 'image================>',img
        index = index + 1
        thumb()
        addon.add_directory( { 'mode' : 'cloud_movie_scrub', 'url' : page , 'iconImg' : img}, { 'title' : title }, img=img, total_items=len(link) )
    if nav:
        addon.add_directory( { 'mode' : 'raj_root', 'url' : nav }, { 'title' : '[B]Next Page...[/B]' },img="https://lh3.googleusercontent.com/-NsVeHCUW0lo/V4b8r67FVSI/AAAAAAAAD7U/G1ifDqs0nFENPck0-oKCQgc3-Gdm_JM7QCCo/s574/next_574x358.png"  )
 
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

def raj_parse_page( url ):
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
    #print html

    srcRegex = '<div class="post-thumb">*\n<a href="(.+?)" title="(.+?)"'
    imgRegex = '<div class="post-thumb">*\n.*title.+?>*\n<img src="(.+?)".*alt="'
    #navRegex = '<a class=\'page-numbers\' href=\'(.+?)\?' #working
    navRegex = '<a class="next page-numbers" href="(.+?)(?:"|\?)'
    #class="next page-numbers" href="

    src = re.compile( srcRegex ).findall( html )
    img = re.compile( imgRegex ).findall( html )
    nav = re.compile( navRegex ).findall( html )[0]
    
    #print "src===>",img

    return nav, zip( src, img )

def cloud_movie_scrubber( url, iconImg , secrun = ''):
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
 
    try:
        req = urllib2.Request(url)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        r = opener.open(req)
        html = r.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass
    
    
    sourceVideos = []
    
    try:
        iframe = re.compile('(?:iframe src|IFRAME SRC)="(.+?)"').findall(html)[0]
        print "iframe===>>",iframe
     
        try:
             req = urllib2.Request(iframe)
             req.add_header('Referer', 'http://tamilgun.com')
             html2 = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
             html2 = e.fp.read()
             pass
         
        moviefile = re.compile("file:'(.*?)'").findall(html2.read())
        print "Movie FIle", moviefile
        sourceVideos += moviefile
    except:
        print 'iframe skipped'
        pass
 
    #html = net.http_GET( url ).content
    soup = BeautifulSoup( html )
    #print 'html',html
 
    # Handle href tags
    for a in soup.findAll('a', href=True):
        if a['href'].find("youtu.be") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')
        if a['href'].find("playhd.video") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')
        if a['href'].find("player.vimeo.com") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')
        if a['href'].find("cloudy.ec") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')
        if a['href'].find("mersalaayitten.com") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')
  
        if a['href'].find("youtube") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')
  
        if a['href'].find("dailymotion") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + ' ' +  ('width = ""'))
        if secrun == '':
            if a['href'].find("view_video.php") != -1:
                #sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')
                url1 = a['href'].split()[0]
                if 'vdogun.com' in url1:
                    print 'log: found vdogun url1 ', url1
                    sourVideo = cloud_movie_scrubber(url1, iconImg, 'secrun')
                    print 'getmovie url', sourVideo
                    x = sourVideo
                    sourceVideos.append(x)
                    print 'log: running after vdogun '
 
    # Handle embed tags
    #sourceVideos += re.compile( '<embed(.+?)>', flags=re.DOTALL).findall( html )
 
    #iframe videowraper
    #videoWrapper = 'class="videoWrapper player">.*<iframe src="(.+?)"'
    mp4Video = re.compile('file: \'(.*?)\'').findall( html )
    #sourceVideos.append(re.compile('file: \'(.*?)\''))
    sourceVideos += re.compile('file: \'(.*?)\'').findall( html )
    sourceVideos += re.compile('file:\'(.*?)\'').findall( html )
    sourceVideos += re.compile('file:"(.*?)"').findall( html )
    sourceVideos += re.compile('"file":"(.*?)"').findall( html )
    sourceVideos += re.compile('type="video/mp4" src="(.*?)"').findall( html )
    print 'print sourcevideos', sourceVideos
    #file:'http://vod.zecast.net/tamilgun/mp4:budhan.mp4/playlist.m3u8'type="video/mp4"
 
    # Handle iframe tags
    #sourceVideos += re.compile( videoWrapper).findall( html )
    sourceVideos += re.compile( '<(?:iframe|IFRAME)(.+?)>').findall( html )
    
    sourceVideos += re.compile( '<source(.+?)>').findall( html )
    
    sourceVideos += re.compile( '<video.*src="(.+?)">').findall( html )
    print 'source videos',sourceVideos
 
    # Handle Youtube new window
    src = re.compile( 'onclick="window.open\((.+?),' ).findall( html )
    if src:
        sourceVideos += [ 'src=' + src[ 0 ] ]
 
    if len( sourceVideos ) == 0:
        print "No video sources found!!!!"
        addon.show_ok_dialog( [ 'Page has unsupported video' ], title='Playback' )
        return
 
    videoItem = []
    for sourceVideo in sourceVideos:
        print "sourceVideo=" + sourceVideo
        sourceVideo = sourceVideo.replace('\/', '/')
        try:
            sourceVideo = re.compile( '(?:src|SRC)=(?:\"|\')(.+?)(?:\"|\')' ).findall( sourceVideo )[0]
            sourceVideo = urllib.unquote( sourceVideo )
        except:
            sourceVideo = sourceVideo
        print "sourceVideo=" + sourceVideo
        sourceVideo = sourceVideo.replace('nowvideo.co', 'nowvideo.ch')
        link = urllib2.urlparse.urlsplit( sourceVideo )
        host = link.hostname
        try:
            host = host.replace( 'www.', '' )
            host = host.replace( '.com', '' )
            sourceName = host.capitalize()
            print "sourceName = " + sourceName
        except:
            pass
            host = ''
  
        if 'dailymotion' in host:
            sourceVideo = parseDailymotion( sourceVideo )
            for video in sourceVideo:
                print "sourceVideo : " + video
                videoId = re.compile('dailymotion\.com/(.+)').findall( video )[ 0 ]
                video = 'plugin://plugin.video.dailymotion_com/?mode=playVideo&url=' + videoId
                print 'Dailymotion parsed video:', video
                videoItem.append( (video, sourceName, video ) )
        
        if 'Tamilgun' in sourceName:
            videoItem.append( ((sourceVideo+'|Referer='+url), sourceName, 'ToolsTube' ) )
  
        if 'facebook' in host:
            print 'skip facebook iframe'
            pass
  
        elif 'youtube' in host:
            sourceVideo = parseYoutube( sourceVideo )
            for video in sourceVideo:
                print "sourceVideo : " + video
                hosted_media = urlresolver.HostedMediaFile( url=video, title=sourceName )
                if not hosted_media:
                    print "Skipping video " + sourceName
                    continue
                videoItem.append( (video, sourceName, hosted_media ) )
  
        elif 'vimeo' in host:
            print 'source video vimeo: ', sourceVideo
            vimeovideo = parseVimeo(sourceVideo)
            print 'vimeo video ==> ', vimeovideo
            if vimeovideo:
                videoItem.append( (vimeovideo, sourceName, vimeovideo ) )
            print 'log vid item',videoItem
  
        elif 'toolstube' in host:
            print 'toolstube found'
            videoItem.append( (parse_cloud_url(sourceVideo), sourceName, 'ToolsTube' ) )
        
        elif 'mersalaayitten' in host:
            print 'hello mersal'
            videoItem.append( (parse_cloud_url(sourceVideo), sourceName, 'Mersal' ) )
        
        elif 'fastplay' in host:
            print 'Fast play in host'
            videoItem.append( (parse_cloud_url(sourceVideo), sourceName, 'Fastplay' ) )
        elif 'megamp4' in host:
            print 'Megamp4 in host'
            videoItem.append( (parse_cloud_url(sourceVideo), sourceName, 'MegaMP4' ) )
        
            
        elif 'playhd.video' in sourceVideo:
            print 'hello playhd'
            if sourceVideo.endswith('.mp4'):
                videoItem.append((sourceVideo, sourceName, 'mp4'))
            else:
                purl = parse_cloud_url(sourceVideo)
                videoItem.append( (purl, sourceName, 'playhd' ) )
                print 'log: playhd catched', purl
        elif 'googleplay.tv' in sourceVideo:
            videoItem.append( (parse_cloud_url(sourceVideo), sourceName, 'googleplay' ) )
  
  
        elif sourceVideo.endswith('.mp4'):
            if secrun != '':
                return sourceVideo
            else:
                videoItem.append((sourceVideo, sourceName, 'mp4'))
      
        elif sourceVideo.endswith('.m3u8'):
            if secrun != '':
                return sourceVideo
            else:
                videoItem.append((sourceVideo, sourceName, 'm3u8'))
  
        else:
            print "sourceVideo else: " + sourceVideo
            hosted_media = urlresolver.HostedMediaFile( url=sourceVideo, title=sourceName )
            if not hosted_media:
                print "Skipping video " + sourceName
                continue
            videoItem.append( (sourceVideo, sourceName, hosted_media ) )
 
 
    print 'videoitem lenth : ' + str(len(videoItem))
    if len( videoItem ) == 0:
        addon.show_ok_dialog( [ 'Video does not exist' ], title='Playback' )
    elif len(videoItem) == 1:
        url, title, hosted_media = videoItem[ 0 ]
        print 'video item array: ', videoItem[0]
        if 'dailymotion' in url:
            stream_url = url
        elif 'Player.vimeo' == title:
            if not url:
                addon.show_ok_dialog( [ 'Video does not exist' ], title='Playback' )
            else:
                print 'vimeo url: ', len(url[0])
                if len(url[0]) < 5:
                    stream_url = url
                else:
                    stream_url = url[0]
                title = 'Vimeo Video'
                print 'im vimeo video: ', stream_url
        elif url.endswith('.mp4'):
            stream_url = url
        elif url.endswith('.m3u8'):
            stream_url = url
        elif 'cloudy' in url:
            print 'in cloudy gun'
            stream_url = parseCustomURL(url)
        elif 'videoraj' in url:
            print 'in videoraj gun'
            stream_url = parseCustomURL(url)
        elif 'grab.php' in url:
            print 'in tamilgun google video', url
            stream_url = url
        elif 'play.php' in url:
            print 'in tamilgun play php google video', url
            stream_url = url
        elif 'playhd.video' in url:
            stream_url = url
        else:
            hosted_media = urlresolver.HostedMediaFile( url=url, title=sourceName )
            surl = hosted_media.resolve()
            if surl != False:
                stream_url = surl
            else: pass
            print 'im in hostedmedia else'
        #print "stream_url " + stream_url
  
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
   
            title = sourceName + ' Part# ' + str( partNo )
            print 'icon=====>',iconImg
            addon.add_video_item( { 'url' : sourceVideo }, { 'title' : title } , img=iconImg, fanart=iconImg)
            partNo += 1
  
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def parse_cloud_url(url):
    if 'toolstube' in url:
        api_html = net.http_GET(url).content
        rapi = re.search('var files = \'{".*":"(.+?)"}', api_html)
        print 'this is ------------------ toolstube',
        return urllib.unquote(rapi.group(1)).replace('\\/', '/')+'|Referer=http://toolstube.com/'
    
    if 'playhd.video' in url:
        api_html = net.http_GET(url).content
        rapi = re.search('source src="(.+?)" type=\'video/mp4\'', api_html)
        reg1 = 'source src="(.+?)" type=\'video/mp4\''
        playurl = re.compile(reg1).findall( api_html )
        print 'this is ------------------ playhd', playurl
        print 'non'
        #return rapi.group(1)+'|Referer=http://www.playhd.video/embed.php?'
        return playurl[0]+'|Referer=http://www.playhd.video/embed.php?'
    
    if 'mersalaayitten.com' in url:
        #http://mersalaayitten.com/media/nuevo/econfig.php?key=1639
        id = url.split('/embed/')[1]
        newUrl = 'http://mersalaayitten.com/media/nuevo/econfig.php?key='+id
        #"http://mersalaayitten.com/media/nuevo/player.swf"
        api_html = net.http_GET(newUrl, headers={'Referer':'http://mersalaayitten.com/media/nuevo/player.swf'}).content
        print 'api_html', api_html
        rapi = re.search('<html5>(.*?)</html5>', api_html)
        return rapi.group(1)
        print 'mersalayitten id='+id
    if 'googleplay' in url:
        api_html = net.http_GET(url).content
        reg1 = '<source src="(.*?)" type="video/mp4"'
        videourl = re.compile(reg1).findall( api_html )[0]
        return videourl+'|Referer=http://googleplay.tv'
    if 'fastplay' in url:
        api_html = net.http_GET(url).content
        fastReg1 = '\|\|div\|vvad\|(.*?)\|'
        fastReg2 = '\|mp4\|(.*?)\|'
        doplay = re.compile(fastReg1).findall( api_html )[0]
        vhash = re.compile(fastReg2).findall( api_html )[0]
        return 'http://'+doplay+'.fastplay.sx/'+vhash+'/v.mp4|Referer=http://fastplay.sx'
    if 'megamp4' in url:
        api_html = net.http_GET(url).content
        if not api_html == 'File was deleted':
            evalreg = "javascript'>(.*?)\n"
            s = re.compile(evalreg).findall( api_html )[0]
            js = eval('unpack' + s[s.find('}(')+1:-1])
            moviereg = 'file:"(.*?)"'
            movieurl = re.compile(moviereg).findall( js )[0]
            return movieurl
        else:
            print "megamp4 file deleted"
            return False

def gun_root( url ):
    #print "main_movie:" + url
    nav, link = gun_parse_page( url )
    #print "nav => ",nav[0]
 
    for ( page, title ), img in link:
        try:
            title =  addon.unescape(title).encode('utf8', 'ignore')
        except UnicodeDecodeError:
            pass
        thumb()
        if not "http://" in img:
            img = "http:"+img
        #print 'tamilgun img: ', img
        addon.add_directory( { 'mode' : 'cloud_movie_scrub', 'url' : page , 'iconImg' : img}, { 'title' : title }, img=img, total_items=len(link) )
    if nav:
        addon.add_directory( { 'mode' : 'gun_root', 'url' : nav[0] }, { 'title' : '[B]Next Page...[/B]' }, img="https://lh3.googleusercontent.com/-NsVeHCUW0lo/V4b8r67FVSI/AAAAAAAAD7U/G1ifDqs0nFENPck0-oKCQgc3-Gdm_JM7QCCo/s574/next_574x358.png" )
 
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

def gun_parse_page(url):
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


##### Queries ##########
mode = addon.queries['mode']
url = addon.queries.get('url', None)
name = addon.queries.get('name', None)
play = addon.queries.get('play', None)
title = addon.queries.get('title', None)
iconImg = addon.queries.get('iconImg', None)

print "MODE: " + str(mode)
print "URL: " + str(url)
print "title " +str(title)
print "Name: " + str(name)
print "play: " + str(play)
print "arg1: " + sys.argv[1]
print "arg2: " + sys.argv[2]
print 'arg length: ', len(sys.argv)

if play:
   print 'log: in play section', url
   stream_url = None
   if 'dailymotion' in url:
      stream_url = get_daily_media_url(url)
   elif 'vimeocdn' in url:
      stream_url = url
   elif 'toolstube' in url:
       print 'log: toolstube true'
       stream_url = url+'|Referer=http://toolstube.com/player/embed_player.php'
   elif 'playhd.video' in url:
       print 'log: playhd.video play'
       stream_url = url+'|referer='+url
   elif url.endswith('mp4'):
       stream_url = url
   elif url.endswith('m3u8'):
       stream_url = url
   elif 'cloudy' in url:
       pass
       stream_url = parseCustomURL(url)
   elif 'videoraj' in url:
       stream_url = parseCustomURL(url)
   elif 'play.php' in url:
            print 'in tamilgun play php google video', url
            stream_url = url
   elif 'fastplay' in url:
        print 'in fastplay ', url
        stream_url = url
   else:
      print 'URL NEW: ', url
      hosted_media = urlresolver.HostedMediaFile( url=url, title=name )
      print "hosted_media"
      print hosted_media
      if hosted_media:
         stream_url = hosted_media.resolve()
         print 'stream url', stream_url

   if stream_url:
      print 'stream url true', stream_url
      xbmcplugin.setResolvedUrl(addon_handle, True,
                                      xbmcgui.ListItem(path=stream_url))
      #addon.resolve_url(stream_url)
   else:
      print "unable to resolve"
      addon.show_ok_dialog( [ 'Unknown hosted video' ], title='Playback' )
else:
    if mode == 'main':
        main()
    
    elif mode == 'yogi_root':
        yogi_root(url)
    
    elif mode == 'yogi_movies_list':
        yogi_movies_list(url)
    
    elif mode == 'yogi_play':
        yogi_play(url,title,iconImg)

    elif mode == 'raj_root':
        raj_root(url)

    elif mode == 'cloud_movie_scrub':
       iconImg = addon.queries.get('iconImg', None)
       cloud_movie_scrubber(url, iconImg)

    elif mode == 'gun_root':
        gun_root(url)

    elif mode == 'einthusan':
        #try:    
            from resources.einthusan import *
            print 'Log: einthusan import success'
            isDirectory = addon.queries.get('isDirectory', None)
            #einthusan(url, mode, isDirectory)
            print 'inthusan', get_pack('resources/einthusan.py')
            if '27b79dbcf28b3180b17fc0252066e520' != get_pack('resources/einthusan.py'):
                getdov
            
            params=get_params()
            url=''
            name=''
            submode=0
            language=''
            try:
                url=urllib.unquote_plus(params["url"])
            except:
                pass
            
            try:
                name=urllib.unquote_plus(params["name"])
            except:
                pass
            
            try:
                submode=int(params["submode"])
                print 'submode value: '+submode
            except:
                pass
            
            try:
                language=urllib.unquote_plus(params["lang"])
            except:
                pass
            
            function_map = {}
            function_map[0] = main_categories
            function_map[1] = get_movies_and_music_videos
            function_map[2] = play_video
            function_map[3] = show_recent_sections
            function_map[4] = show_featured_movies
            function_map[5] = show_top_rated_options
            function_map[6] = show_search_box
            function_map[7] = inner_categories
            function_map[8] = show_A_Z
            function_map[9] = show_list
            function_map[10] = show_list
            function_map[11] = show_list
            function_map[12] = display_setting
            function_map[13] = display_BluRay_listings
            function_map[14] = list_music_videos
            function_map[15] = list_movies_from_JSON_API
            function_map[16] = mp3_menu
            print 'submode value 2: ', submode
            function_map[submode](name, url, language, submode)
        # except:
        #     #try:
        #         dialog = xbmcgui.Dialog()
        #         dialog.ok("Loading at first time", "Downloading necessary files. Won't be shown next time.")
        #         downloadPythonFile(os.path.abspath(programPath + "/" + 'resources'), '__init__.py')
        #         downloadPythonFile(os.path.abspath(programPath + "/" + 'resources'), 'einthusan.py')
        #         downloadPythonFile(os.path.abspath(programPath + "/" + 'resources'), 'DBInterface.py')
        #         downloadPythonFile(os.path.abspath(programPath + "/" + 'resources'), 'HTTPInterface.py')
        #         downloadPythonFile(os.path.abspath(programPath + "/" + 'resources'), 'JSONInterface.py')
        #         xbmc.executebuiltin("XBMC.Notification(TamilKodi Notification,Einthusan Movies Loaded,5000,"+xbmcaddon.Addon().getAddonInfo('icon')+")")
            #except:
            #    xbmc.executebuiltin("XBMC.Notification(TamilKodi Error,Einthusan Import failed,5000,"+xbmcaddon.Addon().getAddonInfo('icon')+")")
    elif mode == 'settings':
        settings(url)
