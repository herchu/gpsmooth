gpsmooth
========

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

Versions
========
 * Feb 17, 2014: Merging Segments. Added to Github.
 * Dec 6, 2013: Initial version released

GPX parsing and generation code from gpxpy library github:
https://github.com/tkrajina/gpxpy ,

(c) 2013, 2014 - Hernan Badenes
