import utils_io_api as ia
import utils_coordinate_transform_api as cta
import utils_drift_struct
import netCDF4
import numpy as np
import datetime
import sys
# netcdf remap_grid_T42 {
# dimensions:
#       grid_size = 8192 ;
#       grid_corners = 4 ;
#       grid_rank = 2 ;

# variables:
#       int grid_dims(grid_rank) ;
#       double grid_center_lat(grid_size) ;
#          grid_center_lat:units = "radians";
#       double grid_center_lon(grid_size) ;
#          grid_center_lon:units = "radians" ;
#       int grid_imask(grid_size) ;
#          grid_imask:units = "unitless" ;
#       double grid_corner_lat(grid_size, grid_corners) ;
#          grid_corner_lat:units = "radians" ;
#       double grid_corner_lon(grid_size, grid_corners) ;
#          grid_corner_lon:units ="radians" ;

# // global attributes:
#          :title = "T42 Gaussian Grid" ;
# }

# NSIDC file default path
PATH_25 = '../products_data/drift_25km_v4.1/'
SCRIP_PATH_25 = '../format_SCRIP/'

def grid_to_SCRIP(grid, dst_path=SCRIP_PATH_25):
	x_size = grid.x_size
	y_size = grid.y_size
	lat = grid.lat[:,:]
	lon = grid.lon[:,:]
	# create SCRIP-format nc file
	ncfile = netCDF4.Dataset(dst_path+str(grid.res)+'km_SCRIP.nc',mode='w',format='NETCDF4')
	# create dimensions
	grid_size = y_size * x_size
	grid_corners = 4
	grid_rank = 2 
	ncfile.createDimension('grid_size', grid_size)
	ncfile.createDimension('grid_corners', grid_corners)
	ncfile.createDimension('grid_rank', grid_rank)
	ncfile.title = '(res='+str(grid.res)+'km) SCRIP'
	# create variables
	grid_dims = ncfile.createVariable('grid_dims', np.int64, ('grid_rank'))
	grid_dims.units = 'unitless'
	grid_dims.longname = 'grid_dimesions'
	grid_center_lat = ncfile.createVariable('grid_center_lat', np.float64, ('grid_size'))
	grid_center_lat.units = 'degrees'
	grid_center_lat.longname = 'grid_center_latitude'
	grid_center_lon = ncfile.createVariable('grid_center_lon', np.float64, ('grid_size'))
	grid_center_lon.units = 'degrees'
	grid_center_lon.longname = 'grid_center_longitude'
	grid_imask = ncfile.createVariable('grid_imask', np.int64, ('grid_size'))
	grid_imask.units = 'unitless'
	grid_imask.longname = 'grid_int_mask'
	grid_corner_lat = ncfile.createVariable('grid_corner_lat', np.float64, ('grid_size','grid_corners'))
	grid_corner_lat.units = 'degrees'
	grid_corner_lat.longname = 'grid_corner_latitude'
	grid_corner_lon = ncfile.createVariable('grid_corner_lon', np.float64, ('grid_size','grid_corners'))
	grid_corner_lon.units = 'degrees'
	grid_corner_lon.longname = 'grid_corner_latitude'
	# set variables values
	grid_dims[:] = np.array([y_size,x_size])[:]
	grid_center_lat[:] = lat.reshape(grid_size)[:]
	grid_center_lon[:] = lon.reshape(grid_size)[:]
	grid_imask[:] = 1
	for i in range(0, y_size, 1):
		for j in range(0, x_size, 1):
			grid_corner_lat[i*y_size+j,:] = lat[i,j]
			grid_corner_lon[i*y_size+j,:] = lon[i,j]
	ncfile.close()
	return 1

def gen_high_grid(src_grid, rate=2):
	# rate test
	if(type(rate) != int):
		sys.exit('gen_new_res_grid : Error rate type, must be int!')
	if(1000*src_grid.res%rate != 0):
		sys.exit('gen_new_res_grid : Error rate value, must be a divisor of src grid resolution!')
	# src grid info
	src_res = src_grid.res
	src_xc = src_grid.xc
	src_yc = src_grid.yc

	# new grid info
	new_res = src_res/rate
	new_x_size = int( (src_grid.x_size - 1) *rate + 1)
	new_y_size = int( (src_grid.y_size - 1) *rate + 1)

	if(src_res == 25):
		R0 = 180 * rate
		S0 = -180 * rate
		new_xc = new_res*(np.arange(-R0, R0+1, 1))
		new_yc = new_res*(np.arange(S0, -S0+1, 1))
	elif(src_res == 62.5):
		R0 = 60 * rate
		S0 = 92 * rate
		new_xc = new_res*(np.arange(-R0,-R0+new_x_size,1))
		new_yc = new_res*(np.arange(-S0,-S0+new_y_size,1))
	else:
		sys.exit('gen_new_res_grid : Error src grid resolution!')
	print('To create lat & lon of grid struct...')
	new_lat = np.zeros([new_y_size,new_x_size])
	new_lon = np.zeros([new_y_size,new_x_size])
	for i in range(0,new_y_size,1):
		for j in range(0,new_x_size,1):
			if(src_res == 25):
				lati, loni = cta.transform_to_latlon_25(j,i,C=new_res,r0=R0,s0=S0)
				new_lat[i,j] = lati
				new_lon[i,j] = loni
			elif(src_res == 62.5):
				lati, loni = cta.transform_to_latlon_625(j,i,C=new_res,r0=R0,s0=S0)
				new_lat[i,j] = lati
				new_lon[i,j] = loni
	print('Successfully create lat & lon of grid struct')
	# generate grid struct
	new_grid = drift_struct.grid(new_xc,new_yc,new_lat,new_lon,new_u,new_v,res=new_res)
	return new_grid

def grid_to_SCRIP_xy(grid,dst_path=SCRIP_PATH_25):
	x_size = grid.x_size
	y_size = grid.y_size
	# create SCRIP-format nc file
	ncfile = netCDF4.Dataset(dst_path+str(grid.res)+'km_SCRIP_xy.nc',mode='w',format='NETCDF4')
	# create dimensions
	grid_size = y_size * x_size
	grid_corners = 4
	grid_rank = 2 
	ncfile.createDimension('grid_size', grid_size)
	ncfile.createDimension('grid_corners', grid_corners)
	ncfile.createDimension('grid_rank', grid_rank)
	ncfile.title = '(res='+str(grid.res)+'km) SCRIP'
	# create variables
	grid_dims = ncfile.createVariable('grid_dims', np.int64, ('grid_rank'))
	grid_dims.units = 'unitless'
	grid_dims.longname = 'grid_dimesions'
	grid_center_lat = ncfile.createVariable('grid_center_lat', np.float64, ('grid_size'))
	grid_center_lat.units = 'degrees'
	grid_center_lat.longname = 'grid_center_x'
	grid_center_lon = ncfile.createVariable('grid_center_lon', np.float64, ('grid_size'))
	grid_center_lon.units = 'degrees'
	grid_center_lon.longname = 'grid_center_y'
	grid_imask = ncfile.createVariable('grid_imask', np.int64, ('grid_size'))
	grid_imask.units = 'unitless'
	grid_imask.longname = 'grid_int_mask'
	grid_corner_lat = ncfile.createVariable('grid_corner_lat', np.float64, ('grid_size','grid_corners'))
	grid_corner_lat.units = 'degrees'
	grid_corner_lat.longname = 'grid_corner_x'
	grid_corner_lon = ncfile.createVariable('grid_corner_lon', np.float64, ('grid_size','grid_corners'))
	grid_corner_lon.units = 'degrees'
	grid_corner_lon.longname = 'grid_corner_y'
	# set variables values
	# dimesions
	grid_dims[:] = np.array([y_size,x_size])[:]
	# center lat & lon
	x_index = np.arange(0,x_size,1)
	for i in range(0, y_size, 1):
		grid_center_lat[i*x_size:(i+1)*x_size] = x_index
		grid_center_lon[i*x_size:(i+1)*x_size] = i
	# int mask
	grid_imask[:] = 1
	# corner lat & lon
	grid_corner_lat[:,0] = grid_center_lat[:] - 0.5
	grid_corner_lat[:,1] = grid_center_lat[:] + 0.5
	grid_corner_lat[:,2] = grid_center_lat[:] + 0.5
	grid_corner_lat[:,3] = grid_center_lat[:] - 0.5
	grid_corner_lon[:,0] = grid_center_lat[:] - 0.5
	grid_corner_lon[:,1] = grid_center_lat[:] - 0.5
	grid_corner_lon[:,2] = grid_center_lat[:] + 0.5
	grid_corner_lon[:,3] = grid_center_lat[:] + 0.5
	# set bound = 0
	grid_corner_lat[::x_size,0] = 0
	grid_corner_lat[::x_size,3] = 0
	grid_corner_lon[0:x_size,0] = 0
	grid_corner_lon[0:x_size,1] = 0
	grid_corner_lon[grid_size-x_size:grid_size] = 0
	ncfile.close()
	return

def gen_high_grid_xy(src_grid, rate=100, dst_path=SCRIP_PATH_25):
	# rate test
	if(type(rate) != int):
		sys.exit('gen_new_res_grid : Error rate type, must be int!')
	if(1000*src_grid.res%rate != 0):
		sys.exit('gen_new_res_grid : Error rate value, must be a divisor of src grid resolution!')
	# new grid info
	x_size = src_grid.x_size * rate
	y_size = src_grid.y_size * rate
	# create SCRIP-format nc file
	ncfile = netCDF4.Dataset(dst_path+str(src_grid.res)+'km_to_'+
		str(src_grid.res/rate)+'km_SCRIP_xy.nc',mode='w',format='NETCDF4')
	# create dimensions
	grid_size = y_size * x_size
	grid_corners = 4
	grid_rank = 2 
	ncfile.createDimension('grid_size', grid_size)
	ncfile.createDimension('grid_corners', grid_corners)
	ncfile.createDimension('grid_rank', grid_rank)
	ncfile.title = '(res='+str(src_grid.res/rate)+'km) SCRIP'
	# create variables
	grid_dims = ncfile.createVariable('grid_dims', np.int64, ('grid_rank'))
	grid_dims.units = 'unitless'
	grid_dims.longname = 'grid_dimesions'
	grid_center_lat = ncfile.createVariable('grid_center_lat', np.float64, ('grid_size'))
	grid_center_lat.units = 'degrees'
	grid_center_lat.longname = 'high_grid_center_x'
	grid_center_lon = ncfile.createVariable('grid_center_lon', np.float64, ('grid_size'))
	grid_center_lon.units = 'degrees'
	grid_center_lon.longname = 'high_grid_center_y'
	grid_imask = ncfile.createVariable('grid_imask', np.int64, ('grid_size'))
	grid_imask.units = 'unitless'
	grid_imask.longname = 'high_grid_int_mask'
	grid_corner_lat = ncfile.createVariable('grid_corner_lat', np.float64, ('grid_size','grid_corners'))
	grid_corner_lat.units = 'degrees'
	grid_corner_lat.longname = 'high_grid_corner_x'
	grid_corner_lon = ncfile.createVariable('grid_corner_lon', np.float64, ('grid_size','grid_corners'))
	grid_corner_lon.units = 'degrees'
	grid_corner_lon.longname = 'high_grid_corner_y'
	# set variables values
	# dimesions
	grid_dims[:] = np.array([y_size,x_size])[:]
	print('create dim!')
	# center lat & lon
	x_index = np.arange(0,x_size,1)
	for i in range(0, y_size, 1):
		grid_center_lat[i*x_size:(i+1)*x_size] = x_index
		grid_center_lon[i*x_size:(i+1)*x_size] = i
	print('create center lat & lon!')
	# int mask
	grid_imask[:] = 1
	# corner lat & lon
	grid_corner_lat[:,0] = grid_center_lat[:] - 0.5
	grid_corner_lat[:,1] = grid_center_lat[:] + 0.5
	grid_corner_lat[:,2] = grid_center_lat[:] + 0.5
	grid_corner_lat[:,3] = grid_center_lat[:] - 0.5
	grid_corner_lon[:,0] = grid_center_lat[:] - 0.5
	grid_corner_lon[:,1] = grid_center_lat[:] - 0.5
	grid_corner_lon[:,2] = grid_center_lat[:] + 0.5
	grid_corner_lon[:,3] = grid_center_lat[:] + 0.5
	print('create corner lat & lon!')
	# set bound = 0
	grid_corner_lat[::x_size,0] = 0
	grid_corner_lat[::x_size,3] = 0
	grid_corner_lon[0:x_size,0] = 0
	grid_corner_lon[0:x_size,1] = 0
	grid_corner_lon[grid_size-x_size:grid_size] = 0
	print('set corner bounds!')
	ncfile.close()

	return

# netcdf mesh-esmf {
# dimensions:
#      nodeCount = 9 ;
#      elementCount = 5 ;
#      maxNodePElement = 4 ;
#      coordDim = 2 ;
# variables:
#      double nodeCoords(nodeCount, coordDim);
#             nodeCoords:units = "degrees" ;
#      int elementConn(elementCount, maxNodePElement) ;
#             elementConn:long_name = "Node Indices that define the element /
#                                      connectivity";
#             elementConn:_FillValue = -1 ;
#             elementConn:start_index = 1 ;
#      byte numElementConn(elementCount) ;
#             numElementConn:long_name = "Number of nodes per element" ;
#      double centerCoords(elementCount, coordDim) ;
#             centerCoords:units = "degrees" ;
#      double elementArea(elementCount) ;
#             elementArea:units = "radians^2" ;
#             elementArea:long_name = "area weights" ;
#      int elementMask(elementCount) ;
#             elementMask:_FillValue = -9999. ;
# // global attributes:
#             :gridType="unstructured";
#             :version = "0.9" ;

def grid_to_ESMF(grid,dst_path=SCRIP_PATH_25):
	x_size = grid.x_size
	y_size = grid.y_size
	xc = grid.xc
	yc = grid.yc
	# create SCRIP-format nc file
	ncfile = netCDF4.Dataset(dst_path+str(grid.res)+'km_ESMF_format.nc',mode='w',format='NETCDF4')
	# set global attributes
	ncfile.gridType = 'unstructured'
	ncfile.version = '0.9'
	# create dimensions
	nodeCount = x_size * y_size
	elementCount = (x_size-1) * (y_size-1)
	maxNodePElement = 4
	coordDim = 2
	grid_rank = 1
	ncfile.createDimension('grid_rank', grid_rank)
	ncfile.createDimension('nodeCount', nodeCount)
	ncfile.createDimension('elementCount', elementCount)
	ncfile.createDimension('maxNodePElement', maxNodePElement)
	ncfile.createDimension('coordDim', coordDim)
	ncfile.title = '(res='+str(grid.res)+'km) ESMF format'
	# create variables
	nodeCoords = ncfile.createVariable('nodeCoords', np.float64, ('nodeCount','coordDim'))
	nodeCoords.units = 'km'
	elementConn = ncfile.createVariable('elementConn', np.int32, ('elementCount','maxNodePElement'), fill_value=-1)
	elementConn.longname = 'gNode Indices that define the element connectivity'
	elementConn.start_index = 0
	numElementConn = ncfile.createVariable('numElementConn', np.byte ,('elementCount'))
	numElementConn.long_name = "Number of nodes per element"
	# set variables value
	for i in range(0, y_size, 1):
		nodeCoords[i*x_size:(i+1)*x_size,0] = xc[:]
		nodeCoords[i*x_size:(i+1)*x_size,1] = yc[i]
	conn_index = np.arange(0,x_size-1,1)
	print('xy_to_ESMF_format: Successfully set nodeCoords!')
	for i in range(0, y_size-1, 1):
		elementConn[i*(x_size-1):(i+1)*(x_size-1):,0] = conn_index
		elementConn[i*(x_size-1):(i+1)*(x_size-1):,1] = elementConn[i*(x_size-1):(i+1)*(x_size-1):,0] + 1
		elementConn[i*(x_size-1):(i+1)*(x_size-1):,2] = elementConn[i*(x_size-1):(i+1)*(x_size-1):,0] + x_size + 1
		elementConn[i*(x_size-1):(i+1)*(x_size-1):,3] = elementConn[i*(x_size-1):(i+1)*(x_size-1):,0] + x_size
		conn_index = conn_index + x_size
	print('xy_to_ESMF_format: Successfully set elementConn!')
	numElementConn[:] = 4
	print('xy_to_ESMF_format: Successfully set numElementConn!')
	ncfile.close()
	return

def gen_ESMF_format(grid, rate=10, dst_path=SCRIP_PATH_25):
	x_size = grid.x_size + (grid.x_size-1) * (rate-1)
	y_size = grid.y_size + (grid.y_size-1) * (rate-1)
	xc = grid.xc
	yc = grid.yc
	# create SCRIP-format nc file
	ncfile = netCDF4.Dataset(dst_path+str(src_grid.res)+'km_to_'+
		str(src_grid.res/rate)+'km_ESMF_format.nc',mode='w',format='NETCDF4')
	# set global attributes
	ncfile.gridType = 'unstructured'
	ncfile.version = '0.9'
	# create dimensions
	nodeCount = x_size * y_size
	elementCount = (x_size-1) * (y_size-1)
	maxNodePElement = 4
	coordDim = 2
	grid_rank = 1
	ncfile.createDimension('grid_rank', grid_rank)
	ncfile.createDimension('nodeCount', nodeCount)
	ncfile.createDimension('elementCount', elementCount)
	ncfile.createDimension('maxNodePElement', maxNodePElement)
	ncfile.createDimension('coordDim', coordDim)
	ncfile.title = '(res='+str(grid.res/rate)+'km) ESMF format'
	# create variables
	nodeCoords = ncfile.createVariable('nodeCoords', np.float64, ('nodeCount','coordDim'))
	nodeCoords.units = 'km'
	elementConn = ncfile.createVariable('elementConn', np.int32, ('elementCount','maxNodePElement'), fill_value=-1)
	elementConn.longname = 'gNode Indices that define the element connectivity'
	elementConn.start_index = 0
	numElementConn = ncfile.createVariable('numElementConn', np.byte ,('elementCount'))
	numElementConn.long_name = "Number of nodes per element"
	# set variables value
	new_xc = np.linspace(xc[0],xc[-1],x_size)
	new_yc = np.linspace(yc[0],yc[-1],y_size)
	for i in range(0, y_size, 1):
		nodeCoords[i*x_size:(i+1)*x_size,0] = new_xc[:]
		nodeCoords[i*x_size:(i+1)*x_size,1] = new_yc[i]
	print('gen_ESMF_format: Successfully set nodeCoords!')
	conn_index = np.arange(0,x_size-1,1)
	for i in range(0, y_size-1, 1):
		elementConn[i*(x_size-1):(i+1)*(x_size-1):,0] = conn_index
		elementConn[i*(x_size-1):(i+1)*(x_size-1):,1] = elementConn[i*(x_size-1):(i+1)*(x_size-1):,0] + 1
		elementConn[i*(x_size-1):(i+1)*(x_size-1):,2] = elementConn[i*(x_size-1):(i+1)*(x_size-1):,0] + x_size + 1
		elementConn[i*(x_size-1):(i+1)*(x_size-1):,3] = elementConn[i*(x_size-1):(i+1)*(x_size-1):,0] + x_size
		conn_index = conn_index + x_size
	print('gen_ESMF_format: Successfully set elementConn!')
	numElementConn[:] = 4
	print('gen_ESMF_format: Successfully set numElementConn!')
	ncfile.close()
	return


# velocity calculation
WEIGHT_PATH = '../format_SCRIP/'
W_FILENAME = '25_to_5_weight.nc'

def ESMF_regrid_velocity(y, m, d, src_grid, wfile_path=WEIGHT_PATH, weight_filename=W_FILENAME,):
	# appoint specific time
	start_t = datetime.datetime(y,1,1)
	end_t = datetime.datetime(y,m,d)
	index_t = (end_t-start_t).days
	# read weight file
	ncfile = netCDF4.Dataset(WEIGHT_PATH+weight_filename, mode='r')
	col = ncfile.variables['col'][:]
	row = ncfile.variables['row'][:]
	S = ncfile.variables['S'][:]
	size = S.size
	ncfile.close()
	print('ESMF_regrid: Successfully read ncfile!')
	# read src field
	src_u_2d = src_grid.u[index_t,:,:]
	src_v_2d = src_grid.v[index_t,:,:]
	src_u = src_u_2d.reshape(src_grid.x_size * src_grid.y_size)
	src_v = src_v_2d.reshape(src_grid.x_size * src_grid.y_size)
	print('ESMF_regrid: Suceessfully read src velocity field!')
	# calcualte dst field
	dst_u = np.zeros([size])
	dst_v = np.zeros([size])
	for i in range(0, size, 1):
		dst_u[row[i]] = dst_u[row[i]] + S[i] * src_u[col[i]]
		dst_v[row[i]] = dst_v[row[i]] + S[i] * src_v[col[i]]
	print('ESMF_regrid: Suceessfully calcualte 1d velocity field!')
	dst_u_2d = dst_u.reshape(src_grid.y_size,src_grid.y_size)
	dst_v_2d = dst_v.reshape(src_grid.y_size,src_grid.y_size)
	print('ESMF_regrid: Suceessfully get 2d velocity field!')
	return dst_u, dst_v





# test
PATH_25 = '../products_data/drift_25km_v4.1/'
DST_PATH = '../format_SCRIP/'
y = 2015

# (1) use SCRIP lat-lon format
# grid = ia.read_grid_nc_25km(y,y+1,PATH_25)
# print('Successfully read grid info from 25km ncfile!')
# grid_to_SCRIP(grid,dst_path=DST_PATH)
# print('Successfully transform grid to SCRIP!')
# high_grid = gen_high_grid(grid,rate=10,dst_path=DST_PATH)
# print('Successfully generate high res grid!')
# grid_to_SCRIP(high_grid,dst_path=DST_PATH)
# print('Successfully generate high res grid!')

# (2) use SCRIP x-y format?
grid = ia.read_grid_nc_25km(y,y+1,PATH_25)
print('Successfully read grid info from 25km ncfile!')
grid_to_SCRIP_xy(grid,dst_path=DST_PATH)
print('Successfully transform grid to SCRIP!')
high_grid = gen_high_grid_xy(grid,rate=10,dst_path=DST_PATH)
print('Successfully generate high res SCRIP!')

# (3) use ESMF format (WRONG)

# (4) velocity calculation
# u,v =ESMF_regrid_velocity(2015,10,3,grid)


print('finish!')
