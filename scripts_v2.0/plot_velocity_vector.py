#!/usr/bin/env python
import utils_io_api as ia
import utils_velocity_transform_api as vta
# import packages
import datetime
import numpy as np 
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as ccrs 
import cartopy.feature as cfeature

def plot_velocity_vector(y1,y2,y,m,d):
	date = datetime.date(y,m,d)
	date_index = (date - datetime.date(y1,1,1)).days
	# read data
	grid_25 = ia.read_grid_nc_25km(y1,y2)
	print("Step1: read 25km nc done!")
	grid_625 = ia.read_grid_nc_625km(y1,y2)
	print("Step2: read 62.5km nc done!")
	# save 25km data
	lon_25_degree = grid_25.lon
	lat_25_degree = grid_25.lat
	u_25, v_25 = vta.velocity_transform(grid_25.u,grid_25.v,lat_25_degree,lon_25_degree)
	u_ll_25 = u_25[date_index,:,:]
	v_ll_25 = v_25[date_index,:,:]
	# save 62.5km data
	lon_625_degree = grid_625.lon
	lat_625_degree = grid_625.lat
	u_625, v_625 = vta.velocity_transform(grid_625.u,-grid_625.v,lat_625_degree,lon_625_degree,angle=-np.pi/4)
	u_ll_625 = u_625[date_index,:,:]
	v_ll_625 = v_625[date_index,:,:]
	# plot parameters
	density_25 = 4
	density_625 = 3
	axp = ccrs.Stereographic(central_latitude=90, central_longitude=0)
	# create figure
	fig = plt.figure(figsize=(12,10), dpi=120)
	date_str = date.strftime('%Y-%m-%d')
	fig.suptitle('Daily average velocity of ice motion in '+date_str)

	# plot NSIDC (25km)
	ax1 = fig.add_subplot(121,projection=axp)
	ql1 = ax1.quiver(lon_25_degree[::density_25,::density_25],lat_25_degree[::density_25,::density_25],\
	    u_ll_25[::density_25,::density_25],v_ll_25[::density_25,::density_25],\
	    units='inches', color='black', scale=1, scale_units = 'inches',
	    width=0.008, headwidth=3., headlength=3., label='NSIDC',
	    transform=ccrs.RotatedPole(central_rotated_longitude=180))
	qk1 = ax1.quiverkey(ql1, 0.45, 0.9, 0.1, r'$0.1 {m/s}$', coordinates='figure')
	ax1.add_feature(cfeature.OCEAN, zorder=0)
	ax1.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
	ax1.coastlines(resolution='110m')
	plt.legend(bbox_to_anchor=(1,1))

	# # plot OSISAF (62.5km)
	ax1 = fig.add_subplot(122,projection=axp)
	ql1 = ax1.quiver(lon_625_degree[::density_625,::density_625],lat_625_degree[::density_625,::density_625],\
	    u_ll_625[::density_625,::density_625],v_ll_625[::density_625,::density_625],\
	    units='inches', color='red', scale=1, scale_units = 'inches',
	    width=0.008, headwidth=3., headlength=3., label='OSISAF',
	    transform=ccrs.RotatedPole(central_rotated_longitude=180))
	qk1 = ax1.quiverkey(ql1, 0.55, 0.9, 0.1, r'$0.1 {m/s}$', coordinates='figure')
	ax1.add_feature(cfeature.OCEAN, zorder=0)
	ax1.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
	ax1.coastlines(resolution='110m')
	# # show()
	plt.legend(bbox_to_anchor=(1,1))
	plt.show()
	return

y1 = 2015
y2 = 2016

plot_velocity_vector(y1,y2,2016,1,2)