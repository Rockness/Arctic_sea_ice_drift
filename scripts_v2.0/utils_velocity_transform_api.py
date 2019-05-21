 #!/usr/bin/env python
# coding: utf-8
import numpy as np 

# ===============
# tansfer velocities in r-s (x-y) cooradinate to the ones in lon-lat coordinate
# ===============
# input:
#   lon : longitude (unit: degree)
#   lat : latitude (unit: degree)
#   u : r-s u velocity of ice (unit: m/s) 
#   v : r-s u velocity of ice (unit: m/s) 
# output:
#   u_lat : latitude-axis velocity of ice (unit: m/s) 
#   v_lon : longitude-axis velocity of ice (unit: m/s) 
def velocity_transform(u, v, lat, lon, angle=0):
    u_lat = u * np.cos(-lon*np.pi/180+angle) - v * np.sin(-lon*np.pi/180+angle)
    v_lon = u * np.sin(-lon*np.pi/180+angle) + v * np.cos(-lon*np.pi/180+angle)
    return u_lat,v_lon