import numpy as np
import sys

# =========================================
# default constant for coordinate transform
# =========================================
EARTH_R = 6371.228 # Radius of the Earth (unit:km) ~ 6371.228 km
RES = 25 # Ease-grid nominal resolution (unit:km) = 25 km
R0 = 180 # Map origin column
S0 = -180 # Map origin row
PRECISION = 1e-4 # coordinate transform precision

# ================================
# # coordinate transform 25/62.5km
# ================================

# ==================
# (x,y) to (lat,lon)
# ==================
# input:
#   x: x Coordinate
#   y: y Coordinate
#   res: resolution choice (25 or 62.5)
# output:
#   lat: latitude (degrees, +90 to -90)
#   lon: longitude (degrees, 0 to 360)
def transform_to_latlon(x, y, res):
    if (res==25):
        lat, lon = transform_to_latlon_25(x, y)
    elif (res==62.5):
        lat, lon = transform_to_latlon_625(x, y)
    else:
        sys.exit("Plz give a resolution!")
    return lat, lon

# ===================
# (lat,lon) to (x,y) 
# ===================
# input:
#   lat: latitude (degrees, +90 to -90)
#   lon: longitude (degrees, 0 to 360)
#   res: resolution choice (25 or 62.5)
# output:
#   x: x Coordinate
#   y: y Coordinate
def transform_to_xy(lat, lon, res):
    if (res==25):
        x, y = transform_to_xy_25(lat, lon)
    elif (res==62.5):
        x, y = transform_to_xy_625(lat, lon)
    else:
        sys.exit("Plz give a resolution!")
    return x,y


# ===================================================
# tansfer lon-lat coordinate to r-s (x-y) cooradinate
# ===================================================
# input:
#   lon : longitude (unit: Radians)
#   lat : latitude (unit: Radians)
#   R : earth radius (unit: km) DEFAULT = EARTH_R
#   C : resolution (unit: km) DEFAULT = RES
#   R0 : map origin column (unit: km) CONSTANT
#   S0 : map origin row (unit: km) CONSTANT
# output:
#   r : column coordinate (unit: None) x 
#   s : row coordinate (unit: None) (negative) y
def transform_to_xy_25(lat, lon, R=EARTH_R, C=RES, r0=R0, s0=S0):
    r = 2*R/C * np.sin(lon) * np.sin(np.pi/4 - lat/2) + r0
    s = 2*R/C * np.cos(lon) * np.sin(np.pi/4 - lat/2) + s0
    return r, -s

# ===================================================
# tansfer lon-lat coordinate to r-s (x-y) cooradinate
# ===================================================
# input:
#   lon : longitude (unit: Radians)
#   lat : latitude (unit: Radians)
#   R : earth radius (unit: km) DEFAULT = EARTH_R
#   C : resolution (unit: km) DEFAULT = RES
#   R0 : map origin column (unit: km) CONSTANT
#   S0 : map origin row (unit: km) CONSTANT
# output:
#   r : column coordinate (unit: None) x 
#   s : row coordinate (unit: None) (negative) y  
def transform_to_latlon_25(r, s, R=EARTH_R, C=RES, r0=R0, s0=S0):
    if(np.abs(r-r0)<PRECISION and np.abs(s+s0)<PRECISION):
        return 90,0 # arctic pole use lat=90, lon=0
    elif (np.abs(s+s0)<PRECISION): 
        if (r > r0): # lon = 90 degree
            lat = 2 * (np.pi/4 - np.arcsin(C/(2*R)*(r-r0)))
            return lat*180/np.pi, 90
        elif (r < r0): # lon = -90 degree
            lat = 2 * (np.pi/4 + np.arcsin(C/(2*R)*(r-r0)))
            return lat*180/np.pi, -90
    elif (np.abs(r-r0)<PRECISION): 
        if (s < -s0): # lon = 0
            lat = 2 * (np.pi/4 - np.arcsin(C/(2*R)*(-s-s0)))
            return lat*180/np.pi, 0
        if (s > -s0): # lon = 180
            lat = 2 * (np.pi/4 + np.arcsin(C/(2*R)*(-s-s0)))
            return lat*180/np.pi, 180
    elif (s < -s0): # -90 < lon < 90 degree
        lon = np.arctan((r0-r) / (s+s0))  
        lat = 2*(np.pi/4 - np.arcsin((-s0-s)*C/(2*R*np.cos(lon))))
        return lat*180/np.pi, lon*180/np.pi
    elif (s > -s0 and r < r0): # -180 < lon < -90 degree
        lon = np.arctan((r0-r) / (s+s0)) - np.pi
        lat = 2*(np.pi/4 - np.arcsin((-s0-s)*C/(2*R*np.cos(lon))))
        return lat*180/np.pi, lon*180/np.pi
    elif (s > -s0 and r > r0): # 90 < lon < 180 degree
        lon = np.arctan((r0-r) / (s+s0)) + np.pi
        lat = 2*(np.pi/4 - np.arcsin((-s0-s)*C/(2*R*np.cos(lon))))
        return lat*180/np.pi, lon*180/np.pi
    else:
        print('r-s: fuck u !',r,s)

# ==============================
# # coordinate transform 62.5km
# ==============================
# input:
#   x: Polar Stereographic x Coordinate
#   y: Polar Stereographic y Coordinate
#   SLAT: Standard latitude for the SSM/I grids is 70 degrees.
#   SGN: Sign of the latitude (positive = north latitude, negative = south latitude)
# output:
#   ALAT: Geodetic Latitude (degrees, +90 to -90)
#   ALONG: Geodetic Longitude (degrees, -180 to 180)
def transform_to_latlon_625(x, y, C=62.5, r0=60, s0=92, SLAT=70, SGN=1):
    # transform index x,y to distance X,Y
    X = (x-r0)*C
    Y = (s0-y)*C
    # conversion constant
    CDR = 57.29577951
    # Eccentricity squared
    E2 = 0.006693883
    E = np.sqrt(E2)
    # Radius of the earth in kilometers
    RE = 6371.228
    PI = 3.141592654
    SL = SLAT*PI/180
    RHO = np.sqrt(X**2+Y**2)
    if (RHO > 0.1):
        CM = np.cos(SL)/np.sqrt(1.0-E2*(np.sin(SL)**2))
        T = np.tan((PI/4.0)-(SL/(2.0))) / ((1.0-E*np.sin(SL)) / \
            (1.0+E*np.sin(SL)))**(E/2.0)
        if (np.abs(SLAT-90) < 1e-5):
            T = RHO * np.sqrt((1+E)**(1+E)*(1-E)**(1-E))/(2*RE)
        else:
            T = RHO * T / (RE*CM)
        CHI = (PI/2.0) - 2.0*np.arctan(T)
        ALAT = CHI + ((E2/2.0)+(5.0*E2**2.0/24.0)+(E2**3.0/12.0))*np.sin(2*CHI)+ \
        ((7.0*E2**2.0/48.0)+(29.0*E2**3/240.0))*np.sin(4.0*CHI)+ \
        (7.0*E2**3.0/120.0)*np.sin(6.0*CHI)
        ALAT = SGN * ALAT
        ALONG = np.arctan2(SGN*X,-SGN*Y)
        ALONG = SGN*ALONG
        lat = ALAT*180/np.pi
        lon = ALONG*180/np.pi
    else:
        ALAT = 90.0*SGN
        ALONG = 0.0
        lat = ALAT
        lon = ALONG
    # longitude rotate 45 degrees clockwise
    if (-180<=lon<-135):
        lon += 315
    else:
        lon -= 45
    return lat, lon

# ==============================
# # coordinate transform 62.5km
# ==============================
# input:
#   ALAT: Geodetic Latitude (degrees, +90 to -90)
#   ALONG: Geodetic Longitude (degrees, -180 to 180)
#   SLAT: Standard latitude for the SSM/I grids is 70 degrees.
#   SGN: Sign of the latitude (positive = north latitude, negative = south latitude)
# output:
#   x: Polar Stereographic x Coordinate
#   y: Polar Stereographic y Coordinate
def transform_to_xy_625(lat, lon, C=62.5, r0=60, s0=92, SLAT=70, SGN=1):
    # longitude rotate 45 degrees anti-clockwise
    if (np.pi*3/4<=lon<np.pi):
        lon -= np.pi*7/4
    else:
        lon += np.pi/4
    ALAT = lat
    ALONG = lon
    # conversion constant
    CDR = 57.29577951
    # Eccentricity squared
    E2 = 0.006693883
    E = np.sqrt(E2)
    # Radius of the earth in kilometers
    RE = 6371.228
    PI = 3.141592654
    if (np.abs(ALAT) < PI/2):
        T = np.tan(PI/4-ALAT/2)/((1-E*np.sin(ALAT))/(1+E*np.sin(ALAT)))**(E/2)
        if (np.abs(90-SLAT) < 1e-5):
            RHO = 2*RE*T((1+E)**(1+E)*(1-E)**(1-E))**(1.0/2.0)
        else:
            SL = SLAT*PI / 180
            TC = np.tan(PI/4-SL/2)/((1-E*np.sin(SL))/(1+E*np.sin(SL)))**(E/2)
            MC = np.cos(SL)/np.sqrt(1.0-E2*(np.sin(SL)**2))
            RHO = RE*MC*T/TC
        Y = -RHO*SGN*np.cos(SGN*ALONG)
        X = RHO*SGN*np.sin(SGN*ALONG)
    else:
        X = 0.0
        Y = 0.0
    # transform distance to x,y index
    x = X/C + r0
    y = s0 - Y/C
    return x,y