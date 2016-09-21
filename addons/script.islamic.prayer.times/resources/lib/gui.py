# -*- coding: utf-8 -*-
# *
# *      Copyright (C) 2005-2010 Team XBMC
# *      http://www.xbmc.org
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import os, sys, urllib2, base64, socket, simplejson
from time import strptime, mktime
import xbmc
import xbmcgui
import calendar
import prayertimes
import moonPhase
from datetime import datetime, date, timedelta, tzinfo
#import datetime
import time
import math
import Hijri
import _strptime

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__
__settings__ = sys.modules[ "__main__" ].__settings__

POSTAL_LOOKUP_URL = "http://api.geonames.org/postalCodeLookupJSON?postalcode=%s&country=%s&maxRows=1&username=%s"
TIMEZONE_URL =  "http://api.geonames.org/timezoneJSON?lat=%s&lng=%s&username=%s"
socket.setdefaulttimeout(10)

class GUI( xbmcgui.WindowXMLDialog ):

    @staticmethod
    def fetchData(url):
        try:
           req = urllib2.urlopen(url)
           json_string = req.read()
           req.close()
        except:
           json_string = ''
        try:
           json_clean = json_string.replace('"NA"','""')
           parsed_json = simplejson.loads(json_clean)
        except:
           parsed_json = ''
        print "Downloaded data " + str(parsed_json)
        return parsed_json
    @staticmethod
    def get12HTimeString(dt):
        return time.strftime("%I:%M:%S %p", dt)
       
    def __init__( self, *args, **kwargs ):
      global alsaMixerCore
      self.today = date.today()
      
    def onInit( self ):
        PT = prayertimes.PrayTimes('ISNA')
        #PT.setMethod('ISNA')
        geoData = self.fetchData(POSTAL_LOOKUP_URL % ('37174','US','arahuman@gmail.com'))
        latitude =0.0
        longitude =0.0
        cityName=''
        #timezone
        if geoData != '':
            latitude = geoData['postalcodes'][0]['lat']
            longitude = geoData['postalcodes'][0]['lng']
            cityName=geoData['postalcodes'][0]['placeName']
        xbmc.log("Timezone URL is %s" % TIMEZONE_URL % (latitude,longitude,'arahuman@gmail.com'),level=xbmc.LOGDEBUG )
        tzData = self.fetchData(TIMEZONE_URL % (latitude,longitude,'arahuman@gmail.com'))
        if tzData  != '':
            timezone= tzData['dstOffset'] # dstOffset will be the adjusted gmtOffset as per the DST for that location
        print "Lat:%s,Lng:%sTZ:%s" % (str(latitude),str(longitude),str(timezone))
        #now = datetime.datetime(datetime.datetime.year,datetime.datetime.month,datetime.datetime.second,datetime.datetime.hour,datetime.datetime.minute,datetime.datetime.second)
        curdatetime = datetime.now()
        now = datetime(int(curdatetime.year),int(curdatetime.month),int(curdatetime.day),int(curdatetime.hour),int(curdatetime.minute),int(curdatetime.second))
        nowdt = time.localtime()
        print "curdatetime is %s " + str(now)
        times = PT.getTimes((self.today.year, self.today.month, self.today.day), (latitude, longitude), timezone,0,'24h')
        salat = {   
                    '800' : 'Imsak',
                    '801' : 'Fajr', 
                    '802' : 'Sunrise', 
                    '803' : 'Dhuhr',
                    '804' : 'Asr', 
                    '805' : 'Maghrib',
                    '806' : 'Isha'
                 }
        #print "Prayer time is " + times['sunrise']
        #print "Calculation method is " + PT.getMethod()
        #print "Offset is " + str(PT.getOffsets())
        schNames = ['Imsak', 'Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
        FMT = "%H:%M:%S "
        s=""
        w=""
        
        for i in range(len(schNames)):
            #print "datetime object is %s " % str(str(datetime.datetime.date())+times[i.lower()])
            #print (("[%d%02d%02d " % (now.year,now.month,now.day))+ str(times[schNames[i].lower()])+"]")
            fpt = strptime(("%d%02d%02d " % (now.year,now.month,now.day))+ str(times[schNames[i].lower()])+":00","%Y%m%d %H:%M:%S")
            firstPrayTime = datetime.fromtimestamp( mktime( fpt ) )
            #print "time is : " + str(firstPrayTime)
            #firstPrayTime = strptime(times[schNames[i].lower()]+":00",FMT)
            if i<len(schNames)-1:
                npt = strptime(("%d%02d%02d " % (now.year,now.month,now.day))+ str(times[schNames[i+1].lower()]),"%Y%m%d %H:%M")
                nextPrayTime = datetime.fromtimestamp( mktime( npt ) )
            else :
                #nextPrayTime = now + datetime.timedelta(days=1)
                npt = strptime(("%d%02d%02d " % (now.year,now.month,now.day))+ str(times[schNames[1].lower()]),"%Y%m%d %H:%M")
                nextPrayTime = datetime.fromtimestamp( mktime( npt ) )
                nextPrayTime = nextPrayTime + timedelta(days=1);
                #d=dict(nextPrayTime)
                #d['tm_mday'] += 1
                #nextPrayTime = nextPrayTime + 
                #date = datetime.fromtimestamp( mktime( strptime( strdate, '%Y-%m-%dT%H:%M:%S' ) ) )
    
            #print "Time object is %s"  % str(curPrayTime)
            #print "Current time %s " % str(time.strftime("%H:%M", time.localtime(time.time())));
            #prevPrayTime = curPrayTime
            print "First Pray Time : %s , Next Praytime = %s " % (str(firstPrayTime),str(nextPrayTime))
            if (now < firstPrayTime and i==0) :
                s = "Current Waqt : %s" % (str( schNames[len(schNames)-1]) + ': '+ times[schNames[len(schNames)-1].lower()])
                #print("else Current Waqath is " +str( schNames[len(schNames)-1]) + ': '+ times[schNames[len(schNames)-1].lower()])
                w = "%s in %s mins" % (schNames[i+1],str(nextPrayTime-now))
                #print ("%s in %s mins" % (schNames[i+1],str(nextPrayTime-now)))
                break
            else :
                if now >= firstPrayTime and now < nextPrayTime :
                    print "Else Part"
                    if schNames[i]=='Sunrise' or schNames[i]=='Imsak' :
                        #print("Next Waqath is " +str( schNames[i+1]) + ': '+ times[schNames[i+1].lower()])
                        w = "%s in %s mins" % (schNames[i+1],str(nextPrayTime-now))
                        #print ("%s in %s mins" % (schNames[i+1],str(nextPrayTime-now)))
                        print "w is %s" % w
                    elif schNames[i]=='Isha':
                        #print("Current Waqath is " +str( schNames[i]) + ': '+ times[schNames[i].lower()])
                        #print ("%s in %s mins" % (schNames[1],str(nextPrayTime-now)))
                        w = "%s in %s mins" % (schNames[1],str(nextPrayTime-now))
                        s = "Current Waqt : %s" % (str( schNames[i]) + ': '+ times[schNames[i].lower()])
                    else :
                        #print("Current Waqath is " +str( schNames[i]) + ': '+ times[schNames[i].lower()])
                        #print ("%s in %s mins" % (schNames[i+1],str(nextPrayTime-nowdt)))
                        #print ("%s in %s mins" % (schNames[i+1],str(nextPrayTime - now)))
                        s = "Current Waqt : %s" % (str( schNames[i]) + ': '+ times[schNames[i].lower()])
                        w = "%s in %s mins" % (schNames[i+1],str(nextPrayTime-now))
                        
            #print(i+ ': '+ times[i.lower()])
        self.getControl( 208 ).setLabel( w )
        self.getControl( 207 ).setLabel( s )
        
        for id,waqtname in salat.items():
            self.getControl( int(id) ).setLabel(times[waqtname.lower()])
        self.getControl( 200 ).setLabel(cityName)
        # Last updated
        self.getControl( 201 ).setLabel(self.get12HTimeString(time.localtime(time.time())))
        # Hijri
        Hj = Hijri.Hijri()
        arabicDate =  "%i, %s %d" % (Hj.Gregorian2HijriArabicMonth()[0],Hj.Gregorian2HijriArabicMonth()[1],Hj.Gregorian2HijriArabicMonth()[2])
        self.getControl( 203 ).setLabel(arabicDate)
        #self.getControl( 702 ).setLabel(times['sunrise'])
        dt = datetime.now()
        for i in range(1,7):
            dt = dt + timedelta(days= +1)
            m = moonPhase.MoonPhase(dt)
            #print "Date [%s]" % str(m.date)
            #print "Phase [%s]" % m.phase_text
            #print "Illumination [%.1f%%]" % (m.illuminated*100)
            #print "Age [%.1f]" % m.age
            #print "Distance [%.1f]" % m.distance
            #print "Angular Diameter [%.1f]" % m.angular_diameter
            imageName="phases/"
            if m.phase_text == 'New Moon':
                imageName+="50.jpg"
                print 'new moon %s ' % imageName 
            if (m.phase_text == 'Full Moon'):
                imageName+="100.jpg"
                print 'Full moon %s ' % imageName
            if (m.phase_text == 'Waxing Crescent' or m.phase_text == 'First Quarter'):
                imageName+="%i.jpg" % (50 + math.ceil( math.floor(m.illuminated*100)/2))
                print 'wax & 1 quat image name : %s' % (imageName)
            if (m.phase_text == 'Waxing Gibbous'):
                imageName+="%i.jpg" % (50 + math.floor( math.floor(m.illuminated*100)/2))
                print 'wax gib image name : %s' % (imageName)
            if (m.phase_text == 'Waning Gibbous' or m.phase_text == 'Last Quarter'):
                imageName+= "%i.jpg" % (math.floor( 100 - math.floor(m.illuminated*100))/2)
                print 'wan gib & last quat image name : %s' % (imageName)
            if (m.phase_text == 'Waning Crescent'):
                imageName +=  "%i.jpg" % (math.ceil( 100 - math.floor(m.illuminated*100))/2)
                print 'wan cre image name : %s' % (imageName)
            print "Sun Angular Diameter [%.1f] " % m.sun_angular_diameter
            print "-"*100
            if i==1 :
                self.getControl( 901 ).setImage(imageName)
                #illumination
                self.getControl( 204 ).setLabel("Illumination : %.1f%% " % (m.illuminated * 100))
                self.getControl( 205 ).setLabel("Age : %.1f days old" % (m.age))
                self.getControl( 206 ).setLabel("%s " % (m.phase_text))         
        s = """The moon is %s, %.1f%% illuminated, %.1f days old. date is %s,angular diameter %.1f """ %\
            (m.phase_text, m.illuminated * 100, m.age, str(m.date), m.angular_diameter)
        print (s)
        #print "the date of the most recent new moon is %s " % str(m.new_date)
        #print "the date the moon reaches 1st quarter in this cycle is  %s " % str(m.q1_date)
        #print "the date of the full moon in this cycle is %s " % str(m.full_date)
        #print "the date the moon reaches 3rd quarter in this cycle is %s " % str(m.q3_date)
        #print "the date of the next new moon is %s " % str(m.nextnew_date)
# ##--------- End Script -----------##

    def exit_script( self, restart=False ):
      self.close()

# ##--------- Click ----------------##

    def onClick( self, controlId ):
      self.log("controlId: %s" % (controlId))
      print self.start_label



# ##--------- Focus -----------##
   
    def onFocus( self, controlId ):
        self.controlId = controlId
    
# ##--------  Log  ------------##
       
    def log(self, msg):
      xbmc.log("##### [%s] - Debug msg: %s" % (__scriptname__,msg,),level=xbmc.LOGDEBUG )    	
     
# ##--------- End Script ------##

def onAction( self, action ):
    if ( action.getButtonCode() in CANCEL_DIALOG ):
      self.exit_script()