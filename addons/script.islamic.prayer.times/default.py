import sys
import os
import xbmcaddon

__scriptname__ = "Islamic Prayer times"
__author__     = "Abdul Rahuman"
__GUI__        = "Abdul Rahuman"
__scriptId__   = "script.islamic.prayer.times"
__settings__   = xbmcaddon.Addon(id=__scriptId__)
__language__   = __settings__.getLocalizedString
__version__    = __settings__.getAddonInfo("version")
__cwd__        = __settings__.getAddonInfo('path')

__resource__   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
sys.path.append (__resource__)

xbmc.log("##### [%s] - Version: %s" % (__scriptname__,__version__,),level=xbmc.LOGDEBUG )

if ( __name__ == "__main__" ):
    import gui
    print "what is %s"
    ui = gui.GUI( "%s.xml" % __scriptId__.replace(".","-") , __cwd__, "Default")
    ui.doModal()
    del ui
    #sys.modules.clear()