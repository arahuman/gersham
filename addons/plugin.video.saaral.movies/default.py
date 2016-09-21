import urllib,urllib2,re,sys,xbmcplugin,xbmcgui
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging,calendar
import xbmcaddon
from xml.dom.minidom import parse, parseString
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json

def unescape(url):
      htmlCodes = [ 
            ['&', '&amp;'],
            ['<', '&lt;'],
            ['>', '&gt;'],
            ['"', '&quot;'],
        ]
      for code in htmlCodes:
           url = url.replace(code[1], code[0]) 
      return url
    
def getFullPath( resource ):
    path = xbmc.translatePath( os.path.join( __home__, resource ) )
    #print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%" + path
    return path

def get_params():
   param=[]
   paramstring=sys.argv[2]
   if len(paramstring)>=2:
      params=sys.argv[2]
      cleanedparams=params.replace('?','')
      if (params[len(params)-1]=='/'):
         params=params[0:len(params)-2]
      pairsofparams=cleanedparams.split('&')
      param={}
      for i in range(len(pairsofparams)):
         splitparams={}
         splitparams=pairsofparams[i].split('=')
         if (len(splitparams))==2:
            param[splitparams[0]]=splitparams[1]
                               
      return param

def Add_Link( name, url, iconimage):
   print "Add_Link url=" + url
   ok=True
   liz=xbmcgui.ListItem( name, iconImage="DefaultVideo.png", thumbnailImage=iconimage )
   liz.setInfo( type="Video", infoLabels={ "Title": name } )
   ok=xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=url, listitem=liz )
   return ok

def Add_Dir( name, url, mode, iconimage ):
   print "Add_Dir url=" + url
   u = sys.argv[0] + "?url=" + urllib.quote_plus( url )+ "&mode=" + str( mode ) + "&name=" + urllib.quote_plus( name )
   ok=True
   liz=xbmcgui.ListItem( name, iconImage="DefaultFolder.png", thumbnailImage=iconimage )
   liz.setInfo( type="Video", infoLabels={ "Title": name } )
   #if skin_used == 'skin.confluence':
   xbmc.executebuiltin('Container.SetViewMode(500)') # "Thumbnail" view   
   ok=xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True )
   return ok

def Add_Playable_Movie_Link(name,url,mode,iconimage):
   print "Add_Playable_Movie_Link url=" + url
   u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
   ok=True
   liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
   liz.setInfo( type="Video", infoLabels={ "Title": name } )
   # adding context menus
   ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
   return ok

def Load_and_Play_Video(url,name):
   ok=True
   print "Load_and_Play_Video:" + url
   req = urllib2.Request(url)
   req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
   response = urllib2.urlopen(req)
   baseUrl = response.geturl()
   link=response.read()
   response.close()

   match=re.search('IFRAME SRC="(.+?)"',link).group(1)
   print "################# Link ################" + match
   req = urllib2.Request(match)
   req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
   response = urllib2.urlopen(req)
   baseUrl = response.geturl()
   link=response.read()
   response.close()

   match=re.search('{file:"(.+?)"',link).group(1)
   print "Video link ##############################" + match
   #for url in match:
   #videoUrl = url
   #xbmcPlayer = xbmc.Player()
   #xbmcPlayer.play(videoUrl)
   Add_Link(name,match,'')
   return ok
   
def Main_Categories():
   url = "http://tamilyogi.cc"
   print "URL = " + url   
   Add_Dir( '[B]DVD ripped Movies[/B]', url + '/category/tamilyogi-dvdrip-movies/', 2, '')
   Add_Dir( '[B]New Movies[/B]', url + '/category/tamilyogi-full-movie-online', 2, '')
   Add_Dir( '[B]Bluray Movies[/B]', url + '/category/tamilyogi-bluray-movies/', 2, '')
   Add_Dir( '[B]Dubbed Movies[/B]', url + '/category/tamilyogi-dubbed-movies-online/', 2, '')
   Add_Dir( '[B]HD Movies[/B]', url + '/tamil-hd-movies-tamilyogi/', 2, '')
   Add_Dir( '[B]HD Trailers[/B]', url + '/tamil-new-movies-tamilyogi/', 2, '')

def Year_List( url ):
   print "Year List url = " + url
   req = urllib2.Request(url)
   req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
   response = urllib2.urlopen(req)
   baseUrl = response.geturl()
   link=response.read()
   response.close()
   
   match=re.compile('<a href="\?(.+?)Year">(.+?)</a>').findall(link)
   baseurl="http://www.einthusan.com"
   suburl = "/movies/index.php?"
   for url,year in match:
      if year != 'n/a':
         Add_Dir( year, baseurl+suburl+url+"Year", 31, '' )
         #print "year:" + year + " " + "url:" + baseurl+suburl+url+"Year"

def Movie_List(url):
   print "Movie List url = " + url
   req = urllib2.Request(url)
   req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
   response = urllib2.urlopen(req)
   baseUrl = response.geturl()
   link=response.read()
   response.close()    
   # Find the movies in the current category
   match=re.compile('<a href="(.+?)" title="(.+?)"><img src="(.+?)"').findall( link )
   #baseurl="http://www.einthusan.com"
   #suburl = "/movies/index.php"
   for movurl,name,thumb in match:
      Add_Dir(name, movurl, 32, thumb )
      #print "name:" + name + " " + "url:" + url
   match=re.compile('<a class="next page-numbers" href="(.+?)">').findall(link)
   #totpages=len(match)
   #pDialog = xbmcgui.DialogProgress()
   #ret = pDialog.create('Loading pages...')
   #pDialog.update(0,'Please wait for the process to retrieve video link.','test')
   for page in match:
      Add_Dir("Next Page >>", page, 2, "" )

       #print "percent :" + str((int(page)*100)/totpages)
       #pDialog.update((int(page)*100/totpages),'Please wait for the process to retrieve video link.','Now downloading page '+ str(page) +' of ' + str(totpages))
       #if (pDialog.iscanceled()):
       #    return False
       #if page!="1":
       #    pageurl = url+"&page="+page
       #    print pageurl
        #   req = urllib2.Request(pageurl)
        #   req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        #   response = urllib2.urlopen(req)
        #   link=response.read()
        #   response.close()    
           # Find the movies in the current category
        #   match=re.compile('<a class="movie-title" href="..(.+?)">(.+?)</a>.+?<img src="..(.+?)".+?/>').findall( link )
        #   baseurl="http://www.einthusan.com"
           #suburl = "/movies/index.php"
        #   for movurl,name,thumb in match:


              
        
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

ttSettings = xbmcaddon.Addon(id='plugin.video.saaral.movies')
__home__ = ttSettings.getAddonInfo('path')
PagestoParseOption = [1, 2, 3, 5, 10]

print "MODE: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "arg1: "+sys.argv[1]
print "arg2: "+sys.argv[2]

if mode==None or url==None or len(url)<1:
   Main_Categories()
       
elif mode == 2:
   Movie_List( url )

elif mode == 1:
   Movie_List( url, name )

elif mode == 3:
   Load_and_Play_Video_Links( url, name )

elif mode == 30:
   Year_List( url )

elif mode == 31:
   ( url )

elif mode == 32:
   print "#################### URL ############" + url + "$$$$$$$$$$$" + name
   Load_and_Play_Video(url,name)
   
xbmcplugin.endOfDirectory(int(sys.argv[1]))
