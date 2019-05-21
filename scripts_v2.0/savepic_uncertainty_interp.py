# /usr/bin/env python3
import utils_io_api
import utils_integral_api
# import plot package
import matplotlib.pyplot as plt
import cartopy.crs as ccrs 
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

SAVE_PATH = '../pic_results_v2.0/uncertainty_interpolations/'

def uncertainty_interps_plot(y1, y2, s, save_path=SAVE_PATH):
	buoy = io_api.read_buoy_txt(y1,s)
	grid = io_api.read_grid_nc_25km(y1,y2)
	trace_lat_25_IDW, trace_lon_25_IDW = integral_api.integral_trace(grid, buoy, interp='IDW')
	trace_lat_25_BL, trace_lon_25_BL = integral_api.integral_trace(grid, buoy, interp='BL')
	trace_lat_25_BC, trace_lon_25_BC = integral_api.integral_trace(grid, buoy, interp='BC')
	grid = io_api.read_grid_nc_625km(y1,y2)
	trace_lat_625_IDW, trace_lon_625_IDW = integral_api.integral_trace(grid, buoy, interp='IDW')
	trace_lat_625_BC, trace_lon_625_BC = integral_api.integral_trace(grid, buoy, interp='BC')
	trace_lat_625_BL, trace_lon_625_BL = integral_api.integral_trace(grid, buoy, interp='BL')
	# plot parameters
	axp = ccrs.Stereographic(central_latitude=90, central_longitude=0,scale_factor=40)
	x_format = LongitudeFormatter(number_format='.1f',degree_symbol='',dateline_direction_label=True)
	y_format = LatitudeFormatter(number_format='.1f',degree_symbol='')
	fontdict = {'size': 8, 'weight' :'bold', 'color': 'w'}
	# create figure
	fig = plt.figure(figsize=(16,10), dpi=160)
	start_date = buoy.date[0].strftime('%Y-%m-%d')
	end_date = buoy.date[-1].strftime('%Y-%m-%d')
	fig.suptitle('buoy ' + buoy.name + ' & drift trace from ' + start_date + ' to '+ end_date)
	plt.subplots_adjust(top=1.0,bottom=0.31,left=0.06,right=0.83,hspace=0.2,wspace=0.47)
	# plot NSIDC
	ax = fig.add_subplot(121,projection=axp)
	ax.set_global()
	# plot buoy
	ax.scatter(buoy.lon,buoy.lat,0.1, \
		color='k',marker='.', label='buoy_'+buoy.name, linewidths=1,\
		transform=ccrs.RotatedPole(central_rotated_longitude=180))
	# plot 25km
	ax.scatter(trace_lon_25_IDW,trace_lat_25_IDW,5, \
		color='b',marker='.', label='NSIDC_25km_IDW',linewidths=1, \
		transform=ccrs.RotatedPole(central_rotated_longitude=180))
	ax.scatter(trace_lon_25_BL,trace_lat_25_BL,5, \
		color='y',marker='.', label='NSIDC_25km_Bilinear',linewidths=1, \
		transform=ccrs.RotatedPole(central_rotated_longitude=180))
	ax.scatter(trace_lon_25_BC,trace_lat_25_BC,5, \
		color='r',marker='.', label='NSIDC_25km_Bicubic',linewidths=1, \
		transform=ccrs.RotatedPole(central_rotated_longitude=180))
	ax.add_feature(cfeature.OCEAN, zorder=0)
	ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
	ax.coastlines(resolution='110m')
	ax.legend(bbox_to_anchor=(1,1))
	# plot OSISAF
	ax = fig.add_subplot(122,projection=axp)
	ax.set_global()
	# plot buoy
	ax.scatter(buoy.lon,buoy.lat,0.1, \
		color='k',marker='.', label='buoy_'+buoy.name, linewidths=1,\
		transform=ccrs.RotatedPole(central_rotated_longitude=180))
	# plot 62.5km
	ax.scatter(trace_lon_625_IDW,trace_lat_625_IDW,5, \
		color='b',marker='.', label='OSISAF_62.5km_IDW',linewidths=1, \
		transform=ccrs.RotatedPole(central_rotated_longitude=180))
	ax.scatter(trace_lon_625_BL,trace_lat_625_BL,5, \
		color='y',marker='.', label='OSISAF_62.5km_Bilinear',linewidths=1, \
		transform=ccrs.RotatedPole(central_rotated_longitude=180))
	ax.scatter(trace_lon_625_BC,trace_lat_625_BC,5, \
		color='r',marker='.', label='OSISAF_62.5km_Bicubic',linewidths=1, \
		transform=ccrs.RotatedPole(central_rotated_longitude=180))
	ax.add_feature(cfeature.OCEAN, zorder=0)
	ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
	ax.coastlines(resolution='110m')
	ax.legend(bbox_to_anchor=(1,1))
	# save picture
	start_date = buoy.date[0].strftime('%Y%m%d')
	end_date = buoy.date[-1].strftime('%Y%m%d')
	plt.savefig(save_path+str(y1)+'-'+str(y2)+
		'/uncertainty_interpolations_'+buoy.name+'-'+start_date +'-'+ end_date+'.jpg',quality=95)
	print('***********************************************************')
	print("Successfully save picture:",'buoy ' + buoy.name + ' & drift trace from ' + start_date + ' to '+ end_date)
	print('***********************************************************')
	return plt

buoy_s_2015 = [1,2,3,9,10,11,12,13]
buoy_s_2016 = [1,2,3,4,5]

# plot 2015
for s in buoy_s_2015:
	uncertainty_interps_plot(2015,2016,s)
# plot 2016
for s in buoy_s_2016:
	uncertainty_interps_plot(2016,2017,s)
