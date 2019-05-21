import numpy as np
import utils_drift_struct as drift_struct
import utils_interp_api as ia
import utils_coordinate_transform_api as cta
import utils_velocity_transform_api as vta
import sys
import datetime

# ======================
# integral to get trace
# ======================
# input:
#   grid_info : the grid 2 continuous year info (type: grid) ()
#   buoy_info : the buoy info (type: buoy) (use the start point and integral period)
#   dt : integral delta time (unit: s)
#   interp : 'IDW' or 'BL' (type: string) - use IDW or Bilinear interpolation (add 'BC' - Bicubic)
# output: 
#   trace_lat, trace_lon : latitude and longitude of each point of trace (unit: degree)
def integral_trace(grid_info,buoy_info,dt=24*3600, interp='IDW'):
    # (0) time process
    ref_t = datetime.datetime(int(buoy_info.year),1,1)
    start_t = buoy_info.date[0] # change datetime to date
    end_t = buoy_info.date[-1] # change datetime to date
    steps = (end_t - start_t).days # integral steps
    t0 = (start_t-ref_t).days # start days
    # (1) transfer the buoy start lat-lon coordinate to cartesian (r-s) coordinate
    buoy_start_r, buoy_start_s = cta.transform_to_xy(buoy_info.lat_radian[0], buoy_info.lon_radian[0], grid_info.res)
    buoy_start_point = drift_struct.point_xy(y=buoy_start_s,x=buoy_start_r)
    # (2) interpolation
    if(interp=='IDW'):
        print('integral use IDW interpolation!')
    elif(interp=='BL'):
        print('integral use Bilinear interpolation!')
    elif(interp=='BC'):
        print('integral use Bicubic interpolation!')
    else:
        sys.exit("interp parameter ERROR!")
    u,v = ia.interp(grid_info, buoy_start_point, t0, interp)
    # fulfill velocity info of buoy start point
    buoy_start_point.u = u
    buoy_start_point.v = v
    # (3) integral dt = 24h
    # trace result
    trace_lat = [buoy_info.lat[0]]
    trace_lon = [buoy_info.lon[0]]
    # initialize point
    point = buoy_start_point
    # integral
    print('start drift point (lat-lon): ',buoy_info.lat[0], buoy_info.lon[0])
    print('start drift point (x-y): ',point.x,point.y)
    print('start drift point (u-v): ',point.u,point.v)
    for t in range(1,steps,1):
        next_x = point.x + point.u * dt / (grid_info.res*1000)
        next_y = point.y + point.v * dt / (grid_info.res*1000)
        # map to lat-lon coordinate
        next_lat, next_lon = cta.transform_to_latlon(next_x,next_y,grid_info.res)
        trace_lat.append(next_lat)
        trace_lon.append(next_lon)
        # make next point
        point = drift_struct.point_xy(x=next_x,y=next_y)
        # if (x,y) is integer, directly use u,v in x-y velocity
        if(point.x==int(point.x) and point.y==int(point.y)):
            u = point.u
            v = point.v
        else: # interpolation
            u,v = ia.interp(grid_info, point, t+t0, interp)
        point.u = u
        point.v = v
    # transform list to array
    trace_lat = np.array(trace_lat)
    trace_lon = np.array(trace_lon)
    print('integral done!')
    return trace_lat, trace_lon


# 
# ========================================================================================
# Generate several points every specific distance in a square area around the buoy start point 
# and calculate the integral of buoy start point and generated points around it.
# ========================================================================================
#   grid_info : the grid 2 continuous year info (type: grid) ()
#   buoy_info : the buoy info (type: buoy) (use the start point and integral period)
#   dt : integral delta time (unit: s)
#   distance: distance between two adjacnet evenly-distributed points (unit: km)
#   area_range: length of side of square area (unit: km)
#   interp : 'IDW' or 'BL' (type: string) - use IDW or Bilinear interpolation (add 'BC' - Bicubic)
# output: 
#   trace_lat, trace_lon : latitude and longitude of each point of trace (unit: degree)
#   trace_u, trace_v : u and v velocity of each point of trace in lat-lon coordinate (unit: m/s)
def points_integral_trace(grid_info, buoy_info, distance=0.3, area_range=3.0, interp='IDW'):
    dt=24*3600
    # calculate cartesian coordinate of buoy start point
    buoy_start_r, buoy_start_s = cta.transform_to_xy(buoy_info.lat_radian[0], buoy_info.lon_radian[0], grid_info.res)
    buoy_point_xy = drift_struct.point_xy(y=buoy_start_s,x=buoy_start_r)
    print('buoy start point(x-y): ',buoy_start_r,buoy_start_s)
    print('buoy start point(lat-lon): ', buoy_info.lat[0],buoy_info.lon[0])
    # generate evenly distributed points around the buoy start point
    num = int(area_range/(2*distance)) * 2 + 1
    disp = int(area_range/(2*distance)) * distance / grid_info.res
    min_x = buoy_point_xy.x - disp
    min_y = buoy_point_xy.y - disp
    delta = distance / grid_info.res
    points_x = np.zeros(num)
    points_y = np.zeros(num)
    for i in range(0,num,1):
        points_x[i] = min_x + i * delta
        points_y[i] = min_y + i * delta
    print('Generate',num**2-1,'points in',area_range,'*',area_range,
        'km^2 around point','(',buoy_point_xy.x,',',buoy_point_xy.y,')','every',distance,'km !')
    # calculate integral of every generated points
    lat_points = []
    lon_points = []
    u_points = []
    v_points = []
    for i in range(0,num,1):
        for j in range(0,num,1):
            buoy_point_i = drift_struct.point_xy(x=points_x[i],y=points_y[j])
            lati_array,loni_array,ui_array,vi_array = specific_point_integral_trace(grid_info,buoy_info,buoy_point_i,interp)
            # transform x-y velocity to lat-lon velocity
            if(grid_info.res == 25):
                ui_array, vi_array = vta.velocity_transform(ui_array, vi_array, lati_array, loni_array)
            elif(grid_info.res == 62.5):
                ui_array, vi_array = vta.velocity_transform(ui_array, -vi_array, lati_array, loni_array, angle=-np.pi/4)
            elif(grid_info.res == 20):
                ui_array, vi_array = vta.velocity_transform(ui_array, vi_array, lati_array, loni_array)
            else:
                print('Invalid grid resolution! transform x-y velocity to lat-lon velocity ERROR!')
            # append
            lat_points.append(lati_array)
            lon_points.append(loni_array)
            u_points.append(ui_array)
            v_points.append(vi_array)
    return lat_points, lon_points, u_points, v_points


# ========================================
# calculate the integral of specific point
# ========================================
def specific_point_integral_trace(grid_info, buoy_info, buoy_point_xy, interp='IDW'):
    dt = 24*3600
    # (0) time process
    ref_t = datetime.datetime(int(buoy_info.year),1,1)
    start_t = buoy_info.date[0] # change datetime to date
    end_t = buoy_info.date[-1] # change datetime to date
    steps = (end_t - start_t).days # integral steps
    t0 = (start_t-ref_t).days # start days
    # (1) use specific point (x,y) as buoy_start_point
    buoy_start_point = drift_struct.point_xy(y=buoy_point_xy.y,x=buoy_point_xy.x)
    # (2) interpolation
    u,v = ia.interp(grid_info, buoy_start_point, t0, interp)
    buoy_start_point.u = u
    buoy_start_point.v = v
    # (3) integral dt = 24h
    # trace result
    trace_lat = [buoy_info.lat[0]]
    trace_lon = [buoy_info.lon[0]]
    trace_u = [buoy_start_point.u]
    trace_v = [buoy_start_point.v]
    # initialize point
    point = buoy_start_point
    # integral
    for t in range(1,steps,1):
        next_x = point.x + point.u * dt / (grid_info.res*1000)
        next_y = point.y + point.v * dt / (grid_info.res*1000)
        # map to lat-lon coordinate
        next_lat, next_lon = cta.transform_to_latlon(next_x,next_y,grid_info.res)
        trace_lat.append(next_lat)
        trace_lon.append(next_lon)
        # make next point
        point = drift_struct.point_xy(x=next_x,y=next_y)
        # if (x,y) is integer, directly use u,v in r-s velocity
        if(point.x==int(point.x) and point.y==int(point.y)):
            u = point.u
            v = point.v
        else: # interpolation
            u,v = ia.interp(grid_info, point, t+t0, interp)
        point.u = u
        point.v = v
        # append u, v
        trace_u.append(point.u)
        trace_v.append(point.v)
    # transform list to array
    trace_lat = np.array(trace_lat)
    trace_lon = np.array(trace_lon)
    trace_u = np.array(trace_u)
    trace_v = np.array(trace_v)
    return trace_lat, trace_lon, trace_u, trace_v

