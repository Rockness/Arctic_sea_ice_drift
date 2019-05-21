# /usr/bin/env python3
import utils_io_api
import utils_integral_api
# import plot package
import matplotlib.pyplot as plt
import cartopy.crs as ccrs 
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

SAVE_PATH = '../pic_results_v2.0/uncertainty_products/'

def uncertainty_products_plot(y1, y2, s, save_path=SAVE_PATH):
	buoy = io_api.read_buoy_txt(y1,s)
	grid = io_api.read_grid_nc_25km(y1,y2)
	trace_lat_25_IDW, trace_lon_25_IDW = integral_api.integral_trace(grid, buoy, interp='IDW')
	grid = io_api.read_grid_nc_625km(y1,y2)
	trace_lat_625_IDW, trace_lon_625_IDW = integral_api.integral_trace(grid, buoy, interp='IDW')
	# plot parameters
	axp = ccrs.Stereographic(central_latitude=90, central_longitude=0,scale_factor=45)
	x_format = LongitudeFormatter(number_format='.1f',degree_symbol='',dateline_direction_label=True)
	y_format = LatitudeFormatter(number_format='.1f',degree_symbol='')
	# create figure
	fig = plt.figure(figsize=(16,10), dpi=160)
	# plot
	ax = fig.add_subplot(111,projection=axp)
	ax.set_global()
	# plot buoy
	ax.scatter(buoy.lon,buoy.lat,0.1, \
		color='k',marker='.', label='buoy_'+buoy.name, linewidths=1,\
		transform=ccrs.RotatedPole(central_rotated_longitude=180))
	# plot NSIDC
	ax.scatter(trace_lon_25_IDW,trace_lat_25_IDW,1, \
		color='r',marker='.', label='NSIDC_25km_IDW',linewidths=1, \
		transform=ccrs.RotatedPole(central_rotated_longitude=180))
	# plot OSISAF
	ax.scatter(trace_lon_625_IDW,trace_lat_625_IDW,1, \
		color='b',marker='.', label='OSISAF_62.5km_IDW',linewidths=1, \
		transform=ccrs.RotatedPole(central_rotated_longitude=180))
	# add plot elements
	ax.add_feature(cfeature.OCEAN, zorder=0)
	ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
	ax.coastlines(resolution='110m')
	ax.legend(bbox_to_anchor=(1,1))
	start_date = buoy.date[0].strftime('%Y-%m-%d')
	end_date = buoy.date[-1].strftime('%Y-%m-%d')
	ax.set_title('buoy ' + buoy.name + ' & drift trace from ' + start_date + ' to '+ end_date +'\n')
	# show
	start_date = buoy.date[0].strftime('%Y%m%d')
	end_date = buoy.date[-1].strftime('%Y%m%d')
	plt.savefig(save_path+str(y1)+'-'+str(y2)+
		'/uncertainty_products_'+buoy.name+'-'+start_date +'-'+ end_date+'.jpg',quality=95)
	# plt.show()
	print('***********************************************************')
	print("Successfully save picture:",'buoy ' + buoy.name + ' & drift trace from ' + strat_date + ' to '+ end_date)
	print('***********************************************************')
	return plt

buoy_s_2015 = [1,2,3,9,10,11,12,13]
buoy_s_2016 = [1,2,3,4,5]

# plot 2015
for s in buoy_s_2015:
	uncertainty_products_plot(2015,2016,s)
# plot 2016
for s in buoy_s_2016:
	uncertainty_products_plot(2016,2017,s)
