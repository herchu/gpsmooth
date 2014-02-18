import gpxpy
import gpxpy.gpx
import sys
from datetime import timedelta
import math

"""
Script to "smooth" a GPX file by interpolating positions where the file
has blanks (long time intervals without a logged point).

This can be used to improve the source data coming from GPS devices like
Garmin (author's is eTrex Vista hCX) before uploading the track to 
runkeeper.com. In this way, less stop/resume points are created, and the
statistics like track length and elevation gain are more accurate 
(and larger!).

Update Feb'14: I found other GPS units that create different "segments" 
every time you stop walking (or... when they want it). Runkeeper also
considers this pauses -- which is right, I suppose. So this script,
when join_segments is True (default value) will also merge all segments
from a track into one.

(c) 2013 - Hernan Badenes -- December 6, 2013

GPX parsing and generation code from gpxpy library github:
https://github.com/tkrajina/gpxpy ,
"""

def printp(p, pfx=None):
    if pfx is None:
        pfx = " "
    print '{0} @{1} ({2},{3}) -> {4}'.format(pfx, p.time, p.latitude, p.longitude, p.elevation)

if len(sys.argv)<2:
    raise Exception("Provide a base file name as argument! (.gpx is assumed)")
    
in_name = sys.argv[1]
gpx_file = open(in_name+'.gpx', 'r')
gpx = gpxpy.parse(gpx_file)

# Magic numbers for Runkeeper. All intervals greater than 10s but less than
# 600s will be divided in smaller segments, points added by interpolating 
# new positions.
min_threshold = 10
max_threshold = 600

join_segments = True

newg = gpxpy.gpx.GPX()
fixed = 0
not_fixed = 0
created = 0
for track in gpx.tracks:
    newt = gpxpy.gpx.GPXTrack()
    news = None
    lastp = None
    delta = 0    
    maxdelta = None
    for segment in track.segments:
        if not join_segments or news==None:
            news = gpxpy.gpx.GPXTrackSegment()
            newt.segments.append(news)
            lastp = None
            delta = 0
            maxdelta = None
        for point in segment.points:
            if lastp is not None:
                diff = (point.time - lastp.time).total_seconds()
                delta += diff
                if diff>=max_threshold: # Too big to fix
                    not_fixed += 1
                    print "* Warning, delta of %ds. Too long, not fixing it!" % diff
                elif diff>=min_threshold: # Try fixing this interval
                    # Calculate number of new points to add
                    newpoints = int(math.ceil(float(diff)/min_threshold))
                    #print "* Warning, delta of %ds. Adding %d new points" % (diff, newpoints)
                    #printp(lastp, " { ")
                    fixed += 1
                    
                    dlat = point.latitude - lastp.latitude
                    dlng = point.longitude - lastp.longitude
                    dele = point.elevation - lastp.elevation if point.elevation!=None and lastp.elevation!=None else None
                    
                    #print "    To create %d new points. Delta lat,lng=%8f,%8f" % (newpoints, dlat, dlng)
                    for i in range(newpoints):
                        frac = float(i+1)/(newpoints+1)
                        lat = lastp.latitude + dlat*frac
                        lng = lastp.longitude + dlng*frac
                        s = diff/(newpoints+1)*(i+1)
                        t = lastp.time + timedelta(seconds = s)
                        e = None if dele is None else lastp.elevation + dele*frac
                        newp = gpxpy.gpx.GPXTrackPoint(lat, lng, time=t, elevation = e)
                        news.points.append(newp)
                        #printp(newp, "  "+str(i))
                        created += 1
                    #printp(point, " } ")
            news.points.append(point)
            lastp = point
        print "Total time delta %sd, avg %fs" % (delta, float(delta)/len(segment.points))

    newg.tracks.append(newt)
print "Fixed %d intervals in range [%ds,%ds]. Other %d intervals were too long, not fixed. Created: %d new points" % (fixed, min_threshold, max_threshold, not_fixed, created)

## Write output to new file
newfilename = in_name+".new.gpx"
new_file = open(newfilename, "w")
new_file.write(newg.to_xml())
new_file.close()
print "Output written to %s" % newfilename
