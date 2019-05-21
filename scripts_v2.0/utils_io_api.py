import utils_drift_struct as drift_struct
from netCDF4 import Dataset
import numpy as np
import datetime
import calendar

# buoy file default path
BUOY_PATH = '../process/'
# NSIDC file default path
PATH_25 = '../products_data/drift_25km_v4.1/'
# OSISAF file defalut path
PATH_625 = '../products_data/drift_lr/merged/'
# OSISAF file name prefix
OSISAF_FILE_PREFIX = 'ice_drift_nh_polstere-625_multi-oi_'

# ===============
# read buoy txt data
# ===============
# input:
#   y : year (type: int)
#   s : buoy index (type: int)
#   path : file directory (type: string) DEFAULT = PATH
# output: 
#   buoy_info : buoy txt data info (type: buoy)
def read_buoy_txt(y,s,path=BUOY_PATH):
    if(s<10):
        s = '0'+str(s)
    else:
        s = str(s)
    file_name = str(y)+'_S_'+s+'_latlon.txt'
    with open(path+file_name,"r") as f:
        info_s01 = f.readlines()
    file_info = file_name.split('_')
    name = file_info[1]+file_info[2]
    year = file_info[0]
    # process drift data
    date_buoy = []
    lat_buoy = []
    lon_buoy = []
    velocity_buoy = []
    for s in info_s01:
        data = s.split()
        date_buoy.append(data[0]+'-'+data[1]+'-'+data[2])
        lat_buoy.append(float(data[3]))
        lon_buoy.append(float(data[4]))
        velocity_buoy.append(float(data[5]))
    # change date to datetime
    date_buoy = [datetime.datetime.strptime(str, "%Y-%m-%d") for str in date_buoy]
    # change lat, lon, velocity list to np.ndarray
    lat_buoy = np.array(lat_buoy)
    lon_buoy = np.array(lon_buoy)
    velocity_buoy = np.array(velocity_buoy)
    # return buoy struct
    buoy_info = drift_struct.buoy(date=date_buoy,lat=lat_buoy,lon=lon_buoy,velocity=velocity_buoy,                                 name=name,year=year)
    return buoy_info

# =================
# read grid nc data
# =================
# input:
#   year1 : 1st year nc file (type: int)
#   year2 : 2ed year nc file (type: int)
#   path : file directory (type: string) DEFAULT = PATH
# output: 
#   grid_info : grid nc data info (type: grid)
def read_grid_nc_25km(year1,year2,path=PATH_25,mask_value=-9999.0):
    y1 = str(year1)
    y2 = str(year2)
    file_name1='icemotion_daily_nh_25km_'+y1+'_v4.1.nc'
    file_name2='icemotion_daily_nh_25km_'+y2+'_v4.1.nc'
    ncfile1 = Dataset(path+file_name1)
    ncfile2 = Dataset(path+file_name2)
    xc = ncfile1.variables['x'][:]
    yc = ncfile1.variables['y'][:]
    lat = ncfile1.variables['latitude'][:,:]
    lon = ncfile1.variables['longitude'][:,:]
    # save 2-year velocity data (unit: m/s)
    u1 = ncfile1.variables['u'][:,:,:]/100 
    v1 = ncfile1.variables['v'][:,:,:]/100 
    u2 = ncfile2.variables['u'][:,:,:]/100 
    v2 = ncfile2.variables['v'][:,:,:]/100 
    # merge
    u = np.concatenate((u1,u2),axis=0)
    v = np.concatenate((v1,v2),axis=0)
    # mask
    mask = (u==mask_value)
    u = np.ma.array(u, mask=mask)
    v = np.ma.array(v, mask=mask)
    # generate grid struct
    grid_info = drift_struct.grid(xc,yc,lat,lon,u,v,res=25)
    return grid_info


# =============================================
# read 2 years data and save in one grid struct
# =============================================
# input:
#   year1 : first year (type: int)
#   year2 : next year (type: int)
# output:
#   grid : grid info (type: grid)
def read_grid_nc_625km(year1,year2,path=PATH_625):
    # read two years data
    grid_1 = read_grid_nc_625km_year(year1,path)
    grid_2 = read_grid_nc_625km_year(year2,path)
    # save 2-year velocity data (unit: m/s)
    u1 = grid_1.u
    u2 = grid_2.u
    v1 = grid_1.v
    v2 = grid_2.v
    # merge
    u = np.concatenate((u1,u2),axis=0)
    v = np.concatenate((v1,v2),axis=0)
    mask_u = (u==-1.0e10) # -- will change to -1.0e10 when transform list to array
    mask_v = (v==-1.0e10)
    u = np.ma.array(u,mask=mask_u)
    v = np.ma.array(v,mask=mask_v)
    # read other info
    xc = grid_1.xc
    yc = grid_1.yc
    lat = grid_1.lat
    lon = grid_1.lon
    # generate grid struct
    grid_info = drift_struct.grid(xc,yc,lat,lon,u,v,res=62.5)
    return grid_info

# =========================
# calculate 62.5km velocity
# =========================
# input:
#   dx : x displacement (unit: km)
#   dy : y displacement (unit: km)
# output: 
#   u, v : u,v velocity (unit: m/s)
def get_625_velocity(dx, dy, mask_x = None, mask_y = None):
    dt = 48 * 3600 # interval = 2 days
    xsize = dx[0,:].size
    ysize = dx[:,0].size
    u = np.zeros([ysize,xsize])
    v = np.zeros([ysize,xsize])
    dx = np.ma.array(dx,mask=mask_x)
    dy = np.ma.array(dy,mask=mask_y)
    u = dx / dt
    v = dy / dt
    return u, -v

# =========================
# read 62.5km one year data
# =========================
# input:
#   year: year (type: int)
# output:
#   grid : grid info (type: grid)
def read_grid_nc_625km_year(year,path=PATH_625):
    # read grid info (same info for all nc files)
    ncfile = Dataset(path+str(year)+'/12/'+OSISAF_FILE_PREFIX+str(year)+'12291200-'+str(year)+'12311200.nc')
    xc = ncfile.variables['xc'][:]
    yc = ncfile.variables['yc'][:]
    lat = ncfile.variables['lat'][:,:] # lat[379,559] : latitude of grid point (unit: degree)
    lon = ncfile.variables['lon'][:,:] # lon[379,559] : longitude of grid point (unit: degree) 
    # read 12 months velocity data
    u = []
    v = []
    for m in range(1,13,1):
        # get the number of days every month
        monthRange = calendar.monthrange(year,m)
        days = monthRange[1]
        # read daily data
        for d in range(1,days+1,1):
            # get date
            date=datetime.date(year,m,d)
            delay = datetime.timedelta(days=-2)
            date_start = date + delay
            # transfer to string
            date_start_str = date_start.strftime('%Y%m%d')
            date_str = date.strftime('%Y%m%d')
            year_str = date.strftime('%Y')
            month_str = date.strftime('%m') # 01,02,03...
            # get file name
            filename = OSISAF_FILE_PREFIX+date_start_str+'1200-'+date_str+'1200.nc'
            # read data
            try:
                ncfile = Dataset(path+year_str+'/'+month_str+'/'+filename)
            except:
                print('Warning! No Such File! Skip it: \n'+filename)
                dX = np.zeros([yc.size,xc.size])
                dY = np.zeros([yc.size,xc.size])
            else:
                # save data
                dX = ncfile.variables['dX'][0,:,:]*1000 # dX_20[379,559] x-axis displacement of ice (unit: km) FILL_VALUE = NaN
                dY = ncfile.variables['dY'][0,:,:]*1000 # dY_20[379,559] y-axis displacement of ice (unit: km) FILL_VALUE = NaN
                # calculate veloctiy (m/s)
            u_daily, v_daily = get_625_velocity(dx=dX,dy=dY)
            u.append(u_daily)
            v.append(v_daily)
    # transform list to array
    u = np.array(u)
    v = np.array(v)
    mask_u = (u==-1.0e10) # -- will change to -1.0e10 when transform list to array
    mask_v = (v==-1.0e10)
    u = np.ma.array(u,mask=mask_u)
    v = np.ma.array(v,mask=mask_v)
    # generate grid struct
    grid_info = drift_struct.grid(xc,yc,lat,lon,u,v,res=62.5)
    return grid_info

