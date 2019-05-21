#!/usr/bin/env python
# coding: utf-8
# self-defined api
import io_api
import drift_struct
import integral_api
# import packages
import numpy as np
import matplotlib.pyplot as plt
import datetime
import cartopy.crs as ccrs 
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


y1 = 2015
y2 = 2016
s = 1

# read data
buoy = io_api.read_buoy_txt(y1,s)
print("Step1: read buoy txt done!")
grid_25 = io_api.read_grid_nc_25km(y1,y2)
print("Step2: read 25km nc done!")

# calculate points trace lat-lon info & velocity info
D = 5
AREA = 25
trace_lat_25_points_IDW, trace_lon_25_points_IDW, trace_u_25, trace_v_25 = \
    integral_api.points_integral_trace(grid_25, buoy, distance=D, area_range=AREA, interp='IDW')
print("Step3: integral 25km done! Get trace & velocity.")


# 
# plot 25km
# 
# plot parameters
real_density = 1
density = 3
num = (int(AREA/(2*D)) * 2 + 1)**2
axp = ccrs.Stereographic(central_latitude=90, central_longitude=0,scale_factor=40)
x_format = LongitudeFormatter(number_format='.1f',degree_symbol='',dateline_direction_label=True)
y_format = LatitudeFormatter(number_format='.1f',degree_symbol='')
# create figure
fig = plt.figure(figsize=(10,10), dpi=120)
ax = fig.add_subplot(111,projection=axp)
ax.set_global()
# plot buoy trace
ax.scatter(buoy.lon,buoy.lat,0.1,\
            color='k',marker='.', label='buoy_'+buoy.name, linewidths=1,zorder=5,\
            transform=ccrs.RotatedPole(central_rotated_longitude=180))
fontdict = {'size': 10, 'weight' :'bold', 'color': 'k'}
plt.text(buoy.lon[0],buoy.lat[0], 'start', fontdict=fontdict, \
         rotation=0, rotation_mode='anchor',\
         transform=ccrs.RotatedPole(central_rotated_longitude=180))

# plot the real trace
trace_lon_25_points_IDW_real = trace_lon_25_points_IDW[int(num/2)]
trace_lat_25_points_IDW_real = trace_lat_25_points_IDW[int(num/2)]
ax.scatter(trace_lon_25_points_IDW_real[::real_density],trace_lat_25_points_IDW_real[::real_density],1,
            color='b',marker='.', zorder=200,
            transform=ccrs.RotatedPole(central_rotated_longitude=180))
# plot real velocity vector
trace_u_25_real = trace_u_25[int(num/2)]
trace_v_25_real = trace_v_25[int(num/2)]
ql = ax.quiver(trace_lon_25_points_IDW_real[::real_density],trace_lat_25_points_IDW_real[::real_density],\
    trace_u_25_real[::real_density],trace_v_25_real[::real_density],\
    units='inches', color='b', scale=1, scale_units = 'inches', width=0.008, headwidth=5., headlength=3., label='NSIDC(res=25km)',\
    transform=ccrs.RotatedPole(central_rotated_longitude=180))
# plot other generated trace
for i in range(0,num,1):
    trace_lon_i = trace_lon_25_points_IDW[i]
    trace_lat_i = trace_lat_25_points_IDW[i]
    trace_u_i = trace_u_25[i]
    trace_v_i = trace_v_25[i]
    # scatter
    ax.scatter(trace_lon_i[::density],trace_lat_i[::density],0.01,
        color='r',marker='.', linewidths=1,zorder=i+6,
        transform=ccrs.RotatedPole(central_rotated_longitude=180))
    # velocity vector
    if(i==0):
        qli = ax.quiver(trace_lon_i[::density],trace_lat_i[::density],
            trace_u_i[::density],trace_v_i[::density],
            units='inches', color='r', zorder=i+6,
            scale=1, scale_units = 'inches', width=0.004, headwidth=5., headlength=3.,label='surrounding points',
            transform=ccrs.RotatedPole(central_rotated_longitude=180))
    else:
        qli = ax.quiver(trace_lon_i[::density],trace_lat_i[::density],
            trace_u_i[::density],trace_v_i[::density],
            units='inches', color='r', zorder=i+6,
            scale=1, scale_units = 'inches', width=0.004, headwidth=5., headlength=3.,
            transform=ccrs.RotatedPole(central_rotated_longitude=180))
# add other elements
ax.quiverkey(qli, 0.8, 0.9, 0.1, r'$0.1 {m/s}$', coordinates='figure')
ax.quiverkey(ql, 0.84, 0.9, 0.1, r'$0.1 {m/s}$', coordinates='figure')
ax.add_feature(cfeature.OCEAN, zorder=0)
ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
ax.coastlines(resolution='110m')
ax.legend()
strat_date = buoy.date[0].strftime('%Y-%m-%d')
end_date = buoy.date[-1].strftime('%Y-%m-%d')
ax.set_title('buoy ' + buoy.name + ' & drift trace from ' + strat_date + ' to '+ end_date +'\n'+
    'Generate '+str(num-1)+' points in '+str(AREA)+'*'+str(AREA)+' $km^2$'+' around start point every '+str(D)+' km !')
# show
plt.show()

