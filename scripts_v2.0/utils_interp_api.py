import utils_drift_struct as drift_struct
import numpy as np
import sys
# =============================================
# inverse distance weighted (IDW) interpolation
# =============================================
# input:
#   p_xy : the point (type: point_xy)
#   grid : the grid info (type: grid)
#   t : datetime days
#   type : choose interpolations - 'IDW','BL','BC'
# output: 
#   u,v (unit: m/s)
def interp(grid,p_xy,t,type):
    if(type == 'IDW'):
        u, v = inverse_distance_weigthed(grid,p_xy,t)
    elif(type == 'BL'):
        u, v = bilinear(grid,p_xy,t)
    elif(type == 'BC'):
        u, v = bicubic(grid,p_xy,t)
    else:
        sys.exit('interp: ERROR input type of interpolation!')
    return u, v


# =====================================================================================
# calculate the non-dimensionalized distance between two points in cartesian coordinate
# =====================================================================================
# input:
#   p1_xy : type(point_xy) use x-y coordinate
#   p2_xy : type(point_xy) use x-y coordinate
# output: 
#   non-dimensionalized distance (unit: None)
def cal_points_distance(p1_xy,p2_xy):
    return np.sqrt((p1_xy.x-p2_xy.x)**2 + (p1_xy.y-p2_xy.y)**2)

# =============================================
# inverse distance weighted (IDW) interpolation
# =============================================
# input:
#   p_xy : the point (type: point_xy)
#   grid : the grid info (type: grid)
#   t : datetime days
# output: 
#   u,v (unit: m/s)
def inverse_distance_weigthed(grid,p_xy,t):
        x = int(p_xy.x)
        y = int(p_xy.y)
        p1 = drift_struct.point_xy(x=x,y=y)
        p2 = drift_struct.point_xy(x=x+1,y=y)
        p3 = drift_struct.point_xy(x=x+1,y=y+1)
        p4 = drift_struct.point_xy(x=x,y=y+1)
        # calculate 
        p1_d_inversion = 1/cal_points_distance(p_xy,p1)
        p2_d_inversion = 1/cal_points_distance(p_xy,p2)
        p3_d_inversion = 1/cal_points_distance(p_xy,p3)
        p4_d_inversion = 1/cal_points_distance(p_xy,p4)
        total = p1_d_inversion + p2_d_inversion + p3_d_inversion +p4_d_inversion
        # get weight : top-left, top-right, bottom-right, bottom-left
        p1_weight = p1_d_inversion/total
        p2_weight = p2_d_inversion/total
        p3_weight = p3_d_inversion/total
        p4_weight = p4_d_inversion/total
        # calculate velocity
        u = grid.u[t,y,x]*p1_weight + grid.u[t,y,x+1]*p2_weight + grid.u[t,y+1,x+1]*p3_weight + grid.u[t,y+1,x]*p4_weight
        v = grid.v[t,y,x]*p1_weight + grid.v[t,y,x+1]*p2_weight + grid.v[t,y+1,x+1]*p3_weight + grid.v[t,y+1,x]*p4_weight
        if(type(u)==np.ma.core.MaskedConstant or type(v)==np.ma.core.MaskedConstant):
            u = 0
            v = 0
        # print(t)
        # print(u,v)
        # print(grid.u[t,y,x],grid.u[t,y,x+1],grid.u[t,y+1,x+1],grid.u[t,y+1,x])
        return u, v

# ======================
# Bilinear interpolation
# ======================
# input:
#   p_xy : the point (type: point_xy)
#   grid : the grid info (type: grid)
#   t : datetime days
# output: 
#   u,v (unit: m/s)
def bilinear(grid,p_xy,t):
    x = int(p_xy.x)
    y = int(p_xy.y)
    p1 = drift_struct.point_xy(x=x,y=y)
    p2 = drift_struct.point_xy(x=x+1,y=y)
    p3 = drift_struct.point_xy(x=x+1,y=y+1)
    p4 = drift_struct.point_xy(x=x,y=y+1)
    # x-direction linear interpolation
    u_x1 = grid.u[t,y,x]*(p_xy.x-p1.x) + grid.u[t,y,x+1]*(p2.x-p_xy.x)
    v_x1 = grid.v[t,y,x+1]*(p_xy.x-p1.x) + grid.v[t,y,x+1]*(p2.x-p_xy.x)
    u_x2 = grid.u[t,y+1,x]*(p_xy.x-p4.x) + grid.u[t,y+1,x+1]*(p3.x-p_xy.x)
    v_x2 = grid.v[t,y+1,x]*(p_xy.x-p4.x) + grid.v[t,y+1,x+1]*(p3.x-p_xy.x)
    # y-direction linear interpolation
    u = u_x1*(p_xy.y-y) + u_x2*(y+1-p_xy.y)
    v = v_x1*(p_xy.y-y) + v_x2*(y+1-p_xy.y)
    if(type(u)==np.ma.core.MaskedConstant or type(v)==np.ma.core.MaskedConstant):
        u = 0
        v = 0
    return u,v


# ======================
# Bi-cubic interpolation
# ======================
# input:
#   p_xy : the point (type: point_xy)
#   grid : the grid info (type: grid)
#   t : datetime days
# output: 
#   u,v (unit: m/s)

def bicubic(grid,p_xy,t):
    x = int(p_xy.x)
    y = int(p_xy.y)
    dx = p_xy.x - (x+0.5)
    dy = p_xy.y - (y+0.5)
    # A, B, C
    A = [[S(dx+1), S(dx), S(dx-1), S(dx-2)]]
    A = np.array(A)
    Bu = grid.u[t,y-1:y+3,x-1:x+3]
    # print(np.array(Bu))
    Bv = grid.v[t,y-1:y+3,x-1:x+3]
    C = [[S(dy+1), S(dy), S(dy-1), S(dy-2)]]
    C = np.array(C)
    C_T = C.transpose(1,0)
    # calculate u, v
    u = np.dot(np.dot(A,Bu),C_T)
    v = np.dot(np.dot(A,Bv),C_T)
    u = u[0,0]
    v = v[0,0]
    if(type(u)==np.ma.core.MaskedConstant or type(v)==np.ma.core.MaskedConstant):
        u = 0
        v = 0
    return u, v

# ========================
# Bi-cubic weight function
# ========================
def S(x, a=-0.5):
    if(abs(x)>=0 and abs(x)<1):
        w = (a+2)*np.abs(x**3) - (a+3)*(x**2) + 1
    elif(abs(x)>=1 and abs(x)<2):
        w = a*abs(x**3) - 5*a*(x**2) + 8*a*abs(x) - 4*a
    else:
        w = 0
    return w