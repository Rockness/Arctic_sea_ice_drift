#!/usr/bin/env python
# coding: utf-8
# self-defined api
import utils_io_api as io_api
import utils_drift_struct as drift_struct
import utils_integral_api as integral_api
# import packages
import numpy as np
import matplotlib.pyplot as plt
import datetime
import cartopy.crs as ccrs 
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


y1 = 2016
y2 = 2017
s = 5

# ============
# calcualtion
# ============
# read data
buoy = io_api.read_buoy_txt(y1,s)
print("Step1: read buoy txt done!")
grid_625 = io_api.read_grid_nc_625km(y1,y2)
print("Step2: read 62.5km nc done!")
grid_25 = io_api.read_grid_nc_25km(y1,y2)
print("Step3: read 25km nc done!")

# calculate points trace lat-lon info & velocity info
D_625 = 5
AREA_625 = 50
trace_lat_625_points_IDW, trace_lon_625_points_IDW, trace_u_625, trace_v_625 = \
    integral_api.points_integral_trace(grid_625, buoy, distance=D_625, area_range=AREA_625, interp='BL')
print("Step4: integral 62.5km done! Get trace & velocity.")

D_25 = 5
AREA_25 = 50
trace_lat_25_points_IDW, trace_lon_25_points_IDW, trace_u_25, trace_v_25 = \
    integral_api.points_integral_trace(grid_25, buoy, distance=D_25, area_range=AREA_25, interp='BL')
print("Step5: integral 25km done! Get trace & velocity.")


# plot parameters
real_density = 1
density = 2
axp = ccrs.Stereographic(central_latitude=90, central_longitude=0,scale_factor=40)
x_format = LongitudeFormatter(number_format='.1f',degree_symbol='',dateline_direction_label=True)
y_format = LatitudeFormatter(number_format='.1f',degree_symbol='')
# create figure
fig = plt.figure(figsize=(10,10), dpi=120)
strat_date = buoy.date[0].strftime('%Y-%m-%d')
end_date = buoy.date[-1].strftime('%Y-%m-%d')
fig.suptitle('buoy ' + buoy.name + ' & drift trace from ' + strat_date + ' to '+ end_date +'\n')
plt.subplots_adjust(top=0.88,bottom=0.32,left=0.11,right=0.9,hspace=0.2,wspace=0.2)

# ============
# plot 62.5km
# ============
ax = fig.add_subplot(122,projection=axp)
ax.set_global()
# plot buoy trace
ax.scatter(buoy.lon,buoy.lat,0.1,\
            color='k',marker='.', label='buoy_'+buoy.name, linewidths=1,zorder=5,\
            transform=ccrs.RotatedPole(central_rotated_longitude=180))
fontdict = {'size': 10, 'weight' :'bold', 'color': 'w'}
plt.text(buoy.lon[0],buoy.lat[0], 'start', fontdict=fontdict, \
         rotation=0, rotation_mode='anchor',\
         transform=ccrs.RotatedPole(central_rotated_longitude=180),zorder=1000)
# plot the real trace
num = (int(AREA_625/(2*D_625)) * 2 + 1)**2
trace_lon_625_points_IDW_real = trace_lon_625_points_IDW[int(num/2)]
trace_lat_625_points_IDW_real = trace_lat_625_points_IDW[int(num/2)]
ax.scatter(trace_lon_625_points_IDW_real[::real_density],trace_lat_625_points_IDW_real[::real_density],1,
            color='b',marker='.', zorder=200,
            transform=ccrs.RotatedPole(central_rotated_longitude=180))
# # plot real velocity vector
# trace_u_625_real = trace_u_625[int(num/2)]
# trace_v_625_real = trace_v_625[int(num/2)]
# ql = ax.quiver(trace_lon_625_points_IDW_real[::real_density],trace_lat_625_points_IDW_real[::real_density],\
#     trace_u_625_real[::real_density],trace_v_625_real[::real_density],\
#     units='inches', color='b', scale=1, scale_units = 'inches', width=0.008, headwidth=5., headlength=3., 
#     label='OSISAF(res=62.5km)',zorder = 999,
#     transform=ccrs.RotatedPole(central_rotated_longitude=180))
# plot other generated trace
for i in range(0,num,1):
    trace_lon_i = trace_lon_625_points_IDW[i]
    trace_lat_i = trace_lat_625_points_IDW[i]
    trace_u_i = trace_u_625[i]
    trace_v_i = trace_v_625[i]
    # scatter
    ax.scatter(trace_lon_i[::density],trace_lat_i[::density],0.01,
        color='r',marker='.', linewidths=1,zorder=i+6,
        transform=ccrs.RotatedPole(central_rotated_longitude=180))
    # # velocity vector
    # if(i==0):
    #     qli = ax.quiver(trace_lon_i[::density],trace_lat_i[::density],
    #         trace_u_i[::density],trace_v_i[::density],
    #         units='inches', color='r', zorder=i+6,
    #         scale=1, scale_units = 'inches', width=0.004, headwidth=5., headlength=3.,label='surrounding points',
    #         transform=ccrs.RotatedPole(central_rotated_longitude=180))
    # else:
    #     qli = ax.quiver(trace_lon_i[::density],trace_lat_i[::density],
    #         trace_u_i[::density],trace_v_i[::density],
    #         units='inches', color='r', zorder=i+6,
    #         scale=1, scale_units = 'inches', width=0.004, headwidth=5., headlength=3.,
    #         transform=ccrs.RotatedPole(central_rotated_longitude=180))
# add other elements
ax.add_feature(cfeature.OCEAN, zorder=0)
ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
ax.coastlines(resolution='110m')
ax.legend()
ax.set_title('generate '+str(num-1)+' points around start point\n'+
    'every '+str(D_625)+' km '+'in '+
    str(AREA_625)+'*'+str(AREA_625)+' $km^2$'+' square-area')


# ==========
# plot 25km
# ==========
# plot parameters
num = (int(AREA_25/(2*D_25)) * 2 + 1)**2
ax = fig.add_subplot(121,projection=axp)
ax.set_global()
# plot buoy trace
ax.scatter(buoy.lon,buoy.lat,0.1,\
            color='k',marker='.', label='buoy_'+buoy.name, linewidths=1,zorder=5,\
            transform=ccrs.RotatedPole(central_rotated_longitude=180))
fontdict = {'size': 10, 'weight' :'bold', 'color': 'w'}
plt.text(buoy.lon[0],buoy.lat[0], 'start', fontdict=fontdict, \
         rotation=0, rotation_mode='anchor',zorder=1000,\
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
# ql = ax.quiver(trace_lon_25_points_IDW_real[::real_density],trace_lat_25_points_IDW_real[::real_density],\
#     trace_u_25_real[::real_density],trace_v_25_real[::real_density],\
#     units='inches', color='b', scale=1, scale_units = 'inches', width=0.008, headwidth=5., headlength=3., 
#     label='NSIDC(res=25km)',zorder = 999,
#     transform=ccrs.RotatedPole(central_rotated_longitude=180))
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
    # # velocity vector
    # if(i==0):
    #     qli = ax.quiver(trace_lon_i[::density],trace_lat_i[::density],
    #         trace_u_i[::density],trace_v_i[::density],
    #         units='inches', color='r', zorder=i+6,
    #         scale=1, scale_units = 'inches', width=0.004, headwidth=5., headlength=3.,label='surrounding points',
    #         transform=ccrs.RotatedPole(central_rotated_longitude=180))
    # else:
    #     qli = ax.quiver(trace_lon_i[::density],trace_lat_i[::density],
    #         trace_u_i[::density],trace_v_i[::density],
    #         units='inches', color='r', zorder=i+6,
    #         scale=1, scale_units = 'inches', width=0.004, headwidth=5., headlength=3.,
    #         transform=ccrs.RotatedPole(central_rotated_longitude=180))
# add other elements
# ax.quiverkey(qli, 0.5, 0.8, 0.1, r'$0.1 {m/s}$', coordinates='figure')
# ax.quiverkey(ql, 0.5, 0.75, 0.1, r'$0.1 {m/s}$', coordinates='figure')
ax.add_feature(cfeature.OCEAN, zorder=0)
ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
ax.coastlines(resolution='110m')
ax.legend()
ax.set_title('generate '+str(num-1)+' points around start point\n'+
    'every '+str(D_25)+' km '+ 'in '+
    str(AREA_25)+'*'+str(AREA_25)+' $km^2$'+' square-area')
# show
plt.show()

