#!/usr/bin/env python
# coding: utf-8
import numpy as np

class point_latlon():
    def __init__(self,lat=0,lon=0):
        self.lat = lat
        self.lon = lon

class point_xy():
    def __init__(self,x=0,y=0,u=0,v=0):
        self.x = x
        self.y = y
        self.u = u
        self.v = v

class grid():
    def __init__(self,xc,yc,lat,lon,u,v,res=None):
        self.res = res
        self.xc = xc
        self.yc = yc
        self.lat = lat
        self.lat_radian = lat*np.pi/180
        self.lon = lon
        self.lon_radian = lon*np.pi/180
        self.x_size = int(xc.size)
        self.y_size = int(yc.size)
        self.u = u
        self.v = v

class buoy():
    def __init__(self,date,lat,lon,velocity,name=None,year=None):
        self.name = name
        self.year = year
        self.date = date
        self.lat = lat
        self.lat_radian = lat/180*np.pi
        self.lon = lon
        self.lon_radian = lon/180*np.pi
        self.velocity = velocity

