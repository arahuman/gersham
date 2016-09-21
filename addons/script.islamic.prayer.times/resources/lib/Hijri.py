#!/usr/bin/env python

import math
from datetime import date

class Hijri():

    arabicMonths = ["Muharram", "Safar", "Rabi Al-Awaal", "Rabi Al-Thani", "Jumada Al-Awwal", "Jumada Al-Akhir", "Rajab", 'Shaban', "Ramadan", "Shawwal", "Thul-Qedah", "Thul-Hijjah"]
    
    def __init__(self, method = "MWL") :
        print 'In Init Method'

    
    def intPart(self,floatNum):
        if floatNum < -0.0000001: return math.ceil(floatNum - 0.0000001)
        return math.floor(floatNum + 0.0000001)
    
    def Gregorian2Hijri(self,yr, mth, day):
        if ((yr > 1582) or ((yr == 1582) and (mth > 10)) or \
            ((yr == 1582) and (mth == 10) and (day > 14))):
            jd1 = self.intPart((1461 * (yr + 4800 + \
                              self.intPart((mth - 14) / 12.0))) / 4)
            jd2 = self.intPart((367 * (mth - 2 - 12 * \
                             (self.intPart((mth - 14) / 12.0)))) / 12)
            jd3 = self.intPart((3 * (self.intPart((yr + 4900 + \
                              self.intPart((mth - 14) / 12.0)) / 100))) / 4)
            jd = jd1 + jd2 - jd3 + day - 32075
        else:
            jd1 = self.intPart((7 * (yr + 5001 + \
                              self.intPart((mth - 9) / 7.0))) / 4)
            jd2 = self.intPart((275 * mth) / 9.0)
            jd = 367 * yr - jd1 + jd2 + day + 1729777
    
        l = jd - 1948440 + 10632
        n = self.intPart((l - 1) /10631.0)
        l = l - 10631 * n + 354
        j1 = (self.intPart((10985 - l) / 5316.0)) * (self.intPart((50 * l) / 17719.0))
        j2 = (self.intPart(l / 5670.0)) * (self.intPart((43 * l) / 15238.0))
        j = j1 + j2
        l1 = (self.intPart((30 - j) / 15.0)) * (self.intPart((17719 * j) / 50.0))
        l2 = (self.intPart(j / 16.0)) * (self.intPart((15238 * j) / 43.0))
        l = l - l1 - l2 + 29
        m = self.intPart((24 * l) / 709.0)
        d = l - self.intPart((709 * m) / 24.0)
        y = 30 * n + j - 30
    
        return (int(y), int(m), int(d))
    
    def Gre2HijriArabicMonth(self, yr, mth, day):
        result = self.Gregorian2Hijri(yr, mth, day )
        return result[0],arabicMonths[result[1]-1],result[2]
    
    def Gregorian2HijriArabicMonth(self,dt=date.today()):
        result = self.Gregorian2Hijri(dt.year, dt.month, dt.day )
        return result[2],self.arabicMonths[result[1]-1],result[0]
    
    def Hijri2Gregorian(self, yr, mth, day):
        jd1 = self.intPart((11 * yr + 3) / 30.0)
        jd2 = self.intPart((mth - 1) / 2.0)
        jd = jd1 + 354 * yr + 30 * mth - jd2 + day + 1948440 - 385
    
        if jd > 2299160:
            l = jd + 68569
            n = self.intPart((4 * l) / 146097.0)
            l = l - self.intPart((146097 * n + 3) / 4.0)
            i = self.intPart((4000 * (l + 1)) / 1461001.0)
            l = l - self.intPart((1461 * i) / 4.0) + 31
            j = self.intPart((80 * l) / 2447.0)
            d = l - self.intPart((2447 * j) / 80.0)
            l = self.intPart(j / 11.0)
            m = j + 2 - 12 * l
            y = 100 * (n - 49) + i + l
        else:
            j = jd + 1402
            k = self.intPart((j - 1) / 1461.0)
            l = j - 1461 * k
            n = self.intPart((l - 1) / 365.0) - self.intPart(l / 1461.0)
            i = l - 365 * n + 30
            j = self.intPart((80 * i) / 2447.0)
            d = i - self.intPart((2447 * j) / 80.0)
            i = self.intPart(j / 11.0)
            m = j + 2 - 12 * i
            y = 4 * k + n + i - 4716
        return (y, m, d)

# Convert from Gregorian to Hijri
#print Gregorian2Hijri(1972, 12, 9)
#print "Hijri date for %s" % str(Gregorian2Hijri(2012, 6, 25))
#print "Hijri date with arabic name  %s" % str(Gre2HijriArabicMonth(2012, 6, 25))

# Convert from Hijri to Gregorian
#print Hijri2Gregorian(1392, 11, 3)
#print Hijri2Gregorian(1428, 12, 29)