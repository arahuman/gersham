#!/usr/bin/env python
# moon.py, based on code by John Walker (http://www.fourmilab.ch/)
# ported to Python by Kevin Turner <acapnotic@twistedmatrix.com>
# on June 6, 2001 (JDN 2452066.52491), under a full moon.
#
# This program is in the public domain: "Do what thou wilt shall be
# the whole of the law".

"""Functions to find the phase of the moon.

Ported from \"A Moon for the Sun\" (aka moontool.c), a program by the
venerable John Walker.  He used algoritms from \"Practical Astronomy
With Your Calculator\" by Peter Duffett-Smith, Second Edition.

For the full history of the code, as well as references to other
reading material and other entertainments, please refer to John
Walker's website,
http://www.fourmilab.ch/
(Look under the Science/Astronomy and Space heading.)

The functions of primary interest provided by this module are phase(),
which gives you a variety of data on the status of the moon for a
given date; and phase_hunt(), which given a date, finds the dates of
the nearest full moon, new moon, etc.
"""

from math import sin, cos, floor, sqrt, pi, tan, atan # asin, atan2
import bisect
import datetime
import time
import math 

#try:
#    import DateTime
#except ImportError:
#    from mxnew import DateTime

__TODO__ = [
    'Add command-line interface.',
    'Make front-end modules for ASCII and various GUIs.',
    ]

# Precision used when describing the moon's phase in textual format,
# in phase_string().
PRECISION = 0.05
NEW =   0 / 4.0
FIRST = 1 / 4.0
FULL = 2 / 4.0
LAST = 3 / 4.0
NEXTNEW = 4 / 4.0

MJD0 = 2400000.5 # 1858 November 17, 00:00:00 hours

class MoonPhase:
    """I describe the phase of the moon.

    I have the following properties:
        date - a DateTime instance
        phase - my phase, in the range 0.0 .. 1.0
        phase_text - a string describing my phase
        illuminated - the percentage of the face of the moon illuminated
        angular_diameter - as seen from Earth, in degrees.
        sun_angular_diameter - as seen from Earth, in degrees.

        new_date - the date of the most recent new moon
        q1_date - the date the moon reaches 1st quarter in this cycle
        full_date - the date of the full moon in this cycle
        q3_date - the date the moon reaches 3rd quarter in this cycle
        nextnew_date - the date of the next new moon
    """

    def __init__(self, date=datetime.datetime.now()):
        """MoonPhase constructor.

        Give me a date, as either a Julian Day Number or a DateTime
        object."""
        #print "Date Debug #0 : date[%s]" % (str(date))
        #print "Date Debug #0..1: date[%s]" % (str(datetime.datetime.now()))
        if not isinstance(date, datetime.datetime):
            self.date = caldate(date-MJD0)
            #print "Date Debug #0.1 : date[%s]" % (str(self.date))
        else:
            self.date = date
            #print "Date Debug #0.2 : date[%s]" % (str(self.date))

        self.__dict__.update(phase(self.date))

        self.phase_text = phase_string(self.phase)

    def __getattr__(self, a):
        if a in ['new_date', 'q1_date', 'full_date', 'q3_date',
                 'nextnew_date']:

            (self.new_date, self.q1_date, self.full_date,
             self.q3_date, self.nextnew_date) = phase_hunt(self.date)

            return getattr(self,a)
        raise AttributeError(a)

    def __repr__(self):
        if type(self.date) is int:
            jdn = self.date
        else:
            jdn = self.date.jdn

        return "<%s(%d)>" % (self.__class__, jdn)

    def __str__(self):
        if type(self.date) is int:
            d = caldate(self.date-MJD0)
        else:
            d = self.date
        s = "%s for %s, %s (%%%.2f illuminated)" %\
            (self.__class__, d.strftime(), self.phase_text,
             self.illuminated * 100)

        return s


class AstronomicalConstants:

    # JDN stands for Julian Day Number
    # Angles here are in degrees

    # 1980 January 0.0 in JDN
    # XXX: DateTime(1980).jdn yields 2444239.5 -- which one is right?
    epoch = 2444238.5

    # Ecliptic longitude of the Sun at epoch 1980.0
    ecliptic_longitude_epoch = 278.833540

    # Ecliptic longitude of the Sun at perigee
    ecliptic_longitude_perigee = 282.596403

    # Eccentricity of Earth's orbit
    eccentricity = 0.016718

    # Semi-major axis of Earth's orbit, in kilometers
    sun_smaxis = 1.49585e8

    # Sun's angular size, in degrees, at semi-major axis distance
    sun_angular_size_smaxis = 0.533128

    ## Elements of the Moon's orbit, epoch 1980.0

    # Moon's mean longitude at the epoch
    moon_mean_longitude_epoch = 64.975464
    # Mean longitude of the perigee at the epoch
    moon_mean_perigee_epoch = 349.383063

    # Mean longitude of the node at the epoch
    node_mean_longitude_epoch = 151.950429

    # Inclination of the Moon's orbit
    moon_inclination = 5.145396

    # Eccentricity of the Moon's orbit
    moon_eccentricity = 0.054900

    # Moon's angular size at distance a from Earth
    moon_angular_size = 0.5181

    # Semi-mojor axis of the Moon's orbit, in kilometers
    moon_smaxis = 384401.0
    # Parallax at a distance a from Earth
    moon_parallax = 0.9507

    # Synodic month (new Moon to new Moon), in days
    synodic_month = 29.53058868

    # Base date for E. W. Brown's numbered series of lunations (1923 January 16)
    lunations_base = 2423436.0

    ## Properties of the Earth

    earth_radius = 6378.16

c = AstronomicalConstants()

# Little handy mathematical functions.

fixangle = lambda a: a - 360.0 * floor(a/360.0)
torad = lambda d: d * pi / 180.0
todeg = lambda r: r * 180.0 / pi
dsin = lambda d: sin(torad(d))
dcos = lambda d: cos(torad(d))

def phase_string(p):
    phase_strings = (
        (NEW + PRECISION, "New Moon"),
        (FIRST - PRECISION, "Waxing Crescent"),
        (FIRST + PRECISION, "First Quarter"),
        (FULL - PRECISION, "Waxing Gibbous"),
        (FULL + PRECISION, "Full Moon"),
        (LAST - PRECISION, "Waning Gibbous"),
        (LAST + PRECISION, "Last Quarter"),
        (NEXTNEW - PRECISION, "Waning Crescent"),
        (NEXTNEW + PRECISION, "New Moon"))

    i = bisect.bisect([a[0] for a in phase_strings], p)

    return phase_strings[i][1]


def phase(phase_date=datetime.datetime.now()):
    """Calculate phase of moon as a fraction:

    The argument is the time for which the phase is requested,
    expressed in either a DateTime or by Julian Day Number.

    Returns a dictionary containing the terminator phase angle as a
    percentage of a full circle (i.e., 0 to 1), the illuminated
    fraction of the Moon's disc, the Moon's age in days and fraction,
    the distance of the Moon from the centre of the Earth, and the
    angular diameter subtended by the Moon as seen by an observer at
    the centre of the Earth."""

    # Calculation of the Sun's position

    # date within the epoch
    #print ("Debug 1 %s " % str(datetime.datetime.strftime()) )
    if hasattr(phase_date, "jdn"):
        day = phase_date.jdn - c.epoch
    else:
        day = jdn_from_datetime(phase_date) - c.epoch
    #print ("Debug 2 %s " % str(day) )
    # Mean anomaly of the Sun
    N = fixangle((360/365.2422) * day)
    # Convert from perigee coordinates to epoch 1980
    M = fixangle(N + c.ecliptic_longitude_epoch - c.ecliptic_longitude_perigee)

    # Solve Kepler's equation
    Ec = kepler(M, c.eccentricity)
    Ec = sqrt((1 + c.eccentricity) / (1 - c.eccentricity)) * tan(Ec/2.0)
    # True anomaly
    Ec = 2 * todeg(atan(Ec))
    # Suns's geometric ecliptic longuitude
    lambda_sun = fixangle(Ec + c.ecliptic_longitude_perigee)

    # Orbital distance factor
    F = ((1 + c.eccentricity * cos(torad(Ec))) / (1 - c.eccentricity**2))

    # Distance to Sun in km
    sun_dist = c.sun_smaxis / F
    sun_angular_diameter = F * c.sun_angular_size_smaxis

    ########
    #
    # Calculation of the Moon's position

    # Moon's mean longitude
    moon_longitude = fixangle(13.1763966 * day + c.moon_mean_longitude_epoch)

    # Moon's mean anomaly
    MM = fixangle(moon_longitude - 0.1114041 * day - c.moon_mean_perigee_epoch)

    # Moon's ascending node mean longitude
    # MN = fixangle(c.node_mean_longitude_epoch - 0.0529539 * day)

    evection = 1.2739 * sin(torad(2*(moon_longitude - lambda_sun) - MM))

    # Annual equation
    annual_eq = 0.1858 * sin(torad(M))

    # Correction term
    A3 = 0.37 * sin(torad(M))

    MmP = MM + evection - annual_eq - A3

    # Correction for the equation of the centre
    mEc = 6.2886 * sin(torad(MmP))

    # Another correction term
    A4 = 0.214 * sin(torad(2 * MmP))

    # Corrected longitude
    lP = moon_longitude + evection + mEc - annual_eq + A4

    # Variation
    variation = 0.6583 * sin(torad(2*(lP - lambda_sun)))

    # True longitude
    lPP = lP + variation

    #
    # Calculation of the Moon's inclination
    # unused for phase calculation.
    
    # Corrected longitude of the node
    # NP = MN - 0.16 * sin(torad(M))

    # Y inclination coordinate
    # y = sin(torad(lPP - NP)) * cos(torad(c.moon_inclination))

    # X inclination coordinate
    # x = cos(torad(lPP - NP))

    # Ecliptic longitude (unused?)
    # lambda_moon = todeg(atan2(y,x)) + NP

    # Ecliptic latitude (unused?)
    # BetaM = todeg(asin(sin(torad(lPP - NP)) * sin(torad(c.moon_inclination))))

    #######
    #
    # Calculation of the phase of the Moon

    # Age of the Moon, in degrees
    moon_age = lPP - lambda_sun

    # Phase of the Moon
    moon_phase = (1 - cos(torad(moon_age))) / 2.0

    # Calculate distance of Moon from the centre of the Earth
    moon_dist = (c.moon_smaxis * (1 - c.moon_eccentricity**2))\
                / (1 + c.moon_eccentricity * cos(torad(MmP + mEc)))

    # Calculate Moon's angular diameter
    moon_diam_frac = moon_dist / c.moon_smaxis
    moon_angular_diameter = c.moon_angular_size / moon_diam_frac

    # Calculate Moon's parallax (unused?)
    # moon_parallax = c.moon_parallax / moon_diam_frac

    res = {
        'phase': fixangle(moon_age) / 360.0,
        'illuminated': moon_phase,
        'age': c.synodic_month * fixangle(moon_age) / 360.0 ,
        'distance': moon_dist,
        'angular_diameter': moon_angular_diameter,
        'sun_distance': sun_dist,
        'sun_angular_diameter': sun_angular_diameter
        }

    return res
# phase()


def phase_hunt(sdate=datetime.datetime.now()):
    """Find time of phases of the moon which surround the current date.

    Five phases are found, starting and ending with the new moons
    which bound the current lunation.
    """
    #print "Date Debug #1 : sdate[%s]" % (str(sdate))
    if type(sdate) is float:
        sdate = caldate(sdate-MJD0)
    #print "Date Debug #1.5 : sdate[%s]" % (str(sdate))
    adate = sdate + datetime.timedelta(days= - 45)
    #print "Mine: Date Debug #1.15 : adate [%s],sdate[%s]" % (str(datetime.datetime.now() + datetime.timedelta(days= - 45)),str(sdate))
    #print "Orig: Date Debug #2 : adate [%s],sdate[%s]" % (str(adate),str(sdate))
    k1 = floor((adate.year + ((adate.month - 1) * (1.0/12.0)) - 1900) * 12.3685)

    nt1 = meanphase(adate, k1)
    adate = nt1

    sdate = jdn_from_datetime(sdate)

    while 1:
        adate = adate + c.synodic_month
        k2 = k1 + 1
        nt2 = meanphase(adate,k2)
        if nt1 <= sdate < nt2:
            break
        nt1 = nt2
        k1 = k2

    phases = list(map(truephase,
                 [k1,    k1,    k1,    k1,    k2],
                 [0/4.0, 1/4.0, 2/4.0, 3/4.0, 0/4.0]))

    return phases
# phase_hunt()

def meanphase(sdate, k):
    """Calculates time of the mean new Moon for a given base date.

    This argument K to this function is the precomputed synodic month
    index, given by:

                        K = (year - 1900) * 12.3685

    where year is expressed as a year and fractional year.
    """

    # Time in Julian centuries from 1900 January 0.5
    if type(sdate) is float:        
        delta_t = sdate - julian_date(1900,1,1,12,0,0)
        t = delta_t / 36525
        #print "Date Debug #3 : jdn [%s],delta_t [%s]" % (str(DateTime.DateTime(1900,1,1,12).jdn),str(delta_t))
        #print "Mine: Date Debug #3.5 : jdn [%s],delta_t [%s]" % (str(julian_date(1900,1,1,12,0,0)),str(sdate - julian_date(1900,1,1,12,0,0)))
    else:
        
        delta_t = sdate - datetime.datetime(year=1900,month=1,day=1,hour=12)
        t = delta_t.days / 36525
        #print "Date Debug #4.01 %s" % str(DateTime.DateTime(1900,1,1,12))
        #print "Date Debug #4.02 %s" % str(datetime.datetime(year=1900,month=1,day=1,hour=12))
        #print "Date Debug #4 : delta_t [%s]-sdate[%s]" % (str(delta_t.days),str(sdate))
        #print "Date Debug #4.5 : delta_t [%s]" % (str((datetime.datetime.now() + datetime.timedelta(days= - 45))-datetime.datetime(year=1900,month=1,day=1,hour=12)))
        #print "Julian day %s" % str(datetime.datetime.timetuple(datetime.datetime.now()) [7])
        

    # square for frequent use
    t2 = t * t
    # and cube
    t3 = t2 * t

    nt1 = (
        2415020.75933 + c.synodic_month * k + 0.0001178 * t2 -
        0.000000155 * t3 + 0.00033 * dsin(166.56 + 132.87 * t -
        0.009173 * t2)
        )

    return nt1
# meanphase()

def truephase(k, tphase):
    """Given a K value used to determine the mean phase of the new
    moon, and a phase selector (0.0, 0.25, 0.5, 0.75), obtain the
    true, corrected phase time."""

    apcor = False

    # add phase to new moon time
    k = k + tphase
    # Time in Julian centuries from 1900 January 0.5
    t = k / 1236.85

    t2 = t * t
    t3 = t2 * t

    # Mean time of phase
    pt = (
        2415020.75933 + c.synodic_month * k + 0.0001178 * t2 -
        0.000000155 * t3 + 0.00033 * dsin(166.56 + 132.87 * t -
        0.009173 * t2)
        )

    # Sun's mean anomaly
    m = 359.2242 + 29.10535608 * k - 0.0000333 * t2 - 0.00000347 * t3

    # Moon's mean anomaly
    mprime = 306.0253 + 385.81691806 * k + 0.0107306 * t2 + 0.00001236 * t3

    # Moon's argument of latitude
    f = 21.2964 + 390.67050646 * k - 0.0016528 * t2 - 0.00000239 * t3

    if (tphase < 0.01) or (abs(tphase - 0.5) < 0.01):

        # Corrections for New and Full Moon

        pt = pt + (
            (0.1734 - 0.000393 * t) * dsin(m)
            + 0.0021 * dsin(2 * m)
            - 0.4068 * dsin(mprime)
            + 0.0161 * dsin(2 * mprime)
            - 0.0004 * dsin(3 * mprime)
            + 0.0104 * dsin(2 * f)
            - 0.0051 * dsin(m + mprime)
            - 0.0074 * dsin(m - mprime)
            + 0.0004 * dsin(2 * f + m)
            - 0.0004 * dsin(2 * f - m)
            - 0.0006 * dsin(2 * f + mprime)
            + 0.0010 * dsin(2 * f - mprime)
            + 0.0005 * dsin(m + 2 * mprime)
            )

        apcor = True
    elif (abs(tphase - 0.25) < 0.01) or (abs(tphase - 0.75) < 0.01):

        pt = pt + (
            (0.1721 - 0.0004 * t) * dsin(m)
            + 0.0021 * dsin(2 * m)
            - 0.6280 * dsin(mprime)
            + 0.0089 * dsin(2 * mprime)
            - 0.0004 * dsin(3 * mprime)
            + 0.0079 * dsin(2 * f)
            - 0.0119 * dsin(m + mprime)
            - 0.0047 * dsin(m - mprime)
            + 0.0003 * dsin(2 * f + m)
            - 0.0004 * dsin(2 * f - m)
            - 0.0006 * dsin(2 * f + mprime)
            + 0.0021 * dsin(2 * f - mprime)
            + 0.0003 * dsin(m + 2 * mprime)
            + 0.0004 * dsin(m - 2 * mprime)
            - 0.0003 * dsin(2 * m + mprime)
            )
        if (tphase < 0.5):
            #  First quarter correction
            pt = pt + 0.0028 - 0.0004 * dcos(m) + 0.0003 * dcos(mprime)
        else:
            #  Last quarter correction
            pt = pt + -0.0028 + 0.0004 * dcos(m) - 0.0003 * dcos(mprime)
        apcor = True

    if not apcor:
        raise ValueError(
            "TRUEPHASE called with invalid phase selector",
            tphase)

    return caldate(pt-MJD0)
# truephase()

def kepler(m, ecc):
    """Solve the equation of Kepler."""

    epsilon = 1e-6

    m = torad(m)
    e = m
    while 1:
        delta = e - ecc * sin(e) - m
        e = e - delta / (1.0 - ecc * cos(e))

        if abs(delta) <= epsilon:
            break

    return e

def base60_to_decimal(xyz,delimiter=None):
    """Decimal value from numbers in sexagesimal system.
    
    The input value can be either a floating point number or a string
    such as "hh mm ss.ss" or "dd mm ss.ss". Delimiters other than " "
    can be specified using the keyword ``delimiter``.
    """
    divisors = [1,60.0,3600.0]
    xyzlist = str(xyz).split(delimiter)
    sign = -1 if xyzlist[0].find("-") != -1 else 1
    xyzlist = [abs(float(x)) for x in xyzlist]
    decimal_value = 0
    
    for i,j in zip(xyzlist,divisors): # if xyzlist has <3 values then
                                        # divisors gets clipped.
        decimal_value += i/j
    
    decimal_value = -decimal_value if sign == -1 else decimal_value
    return decimal_value

def decimal_to_base60(deci,precision=1e-8):
    """Converts decimal number into sexagesimal number parts.
    
    ``deci`` is the decimal number to be converted. ``precision`` is how
    close the multiple of 60 and 3600, for example minutes and seconds,
    are to 60.0 before they are rounded to the higher quantity, for
    example hours and minutes.
    """
    sign = "+" # simple putting sign back at end gives errors for small
        # deg. This is because -00 is 00 and hence ``format``,
        # that constructs the delimited string will not add '-'
        # sign. So, carry it as a character.
    if deci < 0:
        deci = abs(deci)
        sign = "-"
    
    frac1, num = math.modf(deci)
    num = int(num) # hours/degrees is integer valued but type is float
    frac2, frac1 = math.modf(frac1*60.0)
    frac1 = int(frac1) # minutes is integer valued but type is float
    frac2 *= 60.0 # number of seconds between 0 and 60
    
    # Keep seconds and minutes in [0 - 60.0000)
    if abs(frac2 - 60.0) < precision:
        frac2 = 0.0
        frac1 += 1
    if abs(frac1 - 60.0) < precision:
        frac1 = 0.0
        num += 1
    
    return (sign,num,frac1,frac2)

def jdn_from_datetime(dt):
    return julian_date(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)

def julian_date(year,month,day,hour,minute,second):
    """Given year, month, day, hour, minute and second return JD.
    
    ``year``, ``month``, ``day``, ``hour`` and ``minute`` are integers,
    truncates fractional part; ``second`` is a floating point number.
    For BC year: use -(year-1). Example: 1 BC = 0, 1000 BC = -999.
    """
    MJD0 = 2400000.5 # 1858 November 17, 00:00:00 hours
    
    year, month, day, hour, minute =\
    int(year),int(month),int(day),int(hour),int(minute)
    
    if month <= 2:
        month +=12
        year -= 1
    
    modf = math.modf
    # Julian calendar on or before 1582 October 4 and Gregorian calendar
    # afterwards.
    if ((10000L*year+100L*month+day) <= 15821004L):
        b = -2 + int(modf((year+4716)/4)[1]) - 1179 
    else:
        b = int(modf(year/400)[1])-int(modf(year/100)[1])+\
          int(modf(year/4)[1]) 
    
    mjdmidnight = 365L*year - 679004L + b + int(30.6001*(month+1)) + day
    
    fracofday = base60_to_decimal(\
      " ".join([str(hour),str(minute),str(second)])) / 24.0
    
    return MJD0 + mjdmidnight + fracofday

def caldate(mjd):
    """Given mjd return calendar date.
    
    Retrns a tuple (year,month,day,hour,minute,second). The last is a
    floating point number and others are integers. The precision in
    seconds is about 1e-4.
    
    To convert jd to mjd use jd - 2400000.5. In this module 2400000.5 is
    stored in MJD0.
    """
    MJD0 = 2400000.5 # 1858 November 17, 00:00:00 hours
    
    modf = math.modf
    a = long(mjd+MJD0+0.5)
    # Julian calendar on or before 1582 October 4 and Gregorian calendar
    # afterwards.
    if a < 2299161: 
        b = 0
        c = a + 1524
    else: 
        b = long((a-1867216.25)/36524.25)
        c = a+ b - long(modf(b/4)[1]) + 1525
    
    d = long((c-122.1)/365.25)
    e = 365*d + long(modf(d/4)[1])
    f = long((c-e)/30.6001)
    
    day = c - e - int(30.6001*f)
    month = f - 1 - 12*int(modf(f/14)[1])
    year = d - 4715 - int(modf((7+month)/10)[1])
    fracofday = mjd - math.floor(mjd)
    hours = fracofday * 24.0
    
    sign,hour,minute,second = decimal_to_base60(hours)
    
    return datetime.datetime(year,month,day,int(sign+str(hour)),minute,int(second))


#
##
#

if __name__ == '__main__':
    j=3
    dt = datetime.datetime(2012,07,2,22,58,11)
    for i in range(j,j+7):
        dt = dt + datetime.timedelta(days= +1)
        m = MoonPhase(dt)
        print "Date [%s]" % str(m.date)
        print "Phase [%s]" % m.phase_text
        print "Illumination [%.1f%%]" % (m.illuminated*100)
        print "Age [%.1f]" % m.age
        print "Distance [%.1f]" % m.distance
        print "Angular Diameter [%.1f]" % m.angular_diameter
        if m.phase_text == 'new':
            print 'new image name : 50.gif'
        if (m.phase_text == 'full'):
            print 'full image name : 100.gif'
        if (m.phase_text == 'waxing crescent' or m.phase_text == 'first quarter'):
            print 'wax & 1 quat image name : %i.gif' % (50 + math.ceil( math.floor(m.illuminated*100)/2))
        if (m.phase_text == 'waxing gibbous'):
            print 'wax gib image name : %i.gif' % (50 + math.floor( math.floor(m.illuminated*100)/2))
        if (m.phase_text == 'waning gibbous' or m.phase_text == 'last quarter'):
            print 'wan gib & last quat image name : %i.gif' % ( math.floor( 100 - math.floor(m.illuminated*100))/2)
        if (m.phase_text == 'waning crescent'):
            print 'wan cre image name : %i.gif' % ( math.ceil( 100 - math.floor(m.illuminated*100))/2)
        
   # print "Sun distance [.1f]" % m.sun_distance
        print "Sun Angular Diameter [%.1f] " % m.sun_angular_diameter
        print "-"*100
    s = """The moon is %s, %.1f%% illuminated, %.1f days old. date is %s,angular diameter %.1f """ %\
        (m.phase_text, m.illuminated * 100, m.age, str(m.date), m.angular_diameter)
    print (s)
    print "the date of the most recent new moon is %s " % str(m.new_date)
    print "the date the moon reaches 1st quarter in this cycle is  %s " % str(m.q1_date)
    print "the date of the full moon in this cycle is %s " % str(m.full_date)
    print "the date the moon reaches 3rd quarter in this cycle is %s " % str(m.q3_date)
    print "the date of the next new moon is %s " % str(m.nextnew_date)
    
