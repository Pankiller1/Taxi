import geopandas as gpd  
import pandas as pd
from shapely.geometry import Polygon,Point
import math 
import numpy as np
def rect_grids(bounds,accuracy = 500):
    '''
    生成研究范围内的方形栅格

    输入
    -------
    bounds : List
        生成范围的边界，[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 
    accuracy : number
        栅格大小（米）
                                               

    输出
    -------
    grid : GeoDataFrame
        栅格的GeoDataFrame，其中LONCOL与LATCOL为栅格的编号，HBLON与HBLAT为栅格的中心点坐标 
    params : List
        栅格参数(lonStart,latStart,deltaLon,deltaLat)，分别为栅格左下角坐标与单个栅格的经纬度长宽
    '''
    #导入math包  
    #划定栅格划分范围
    lon1 = bounds[0]
    lat1 = bounds[1]
    lon2 = bounds[2]
    lat2 = bounds[3]
    #取得左下角的经纬度  
    latStart = min(lat1, lat2);  
    lonStart = min(lon1, lon2);  
    #计算栅格的经纬度增加量大小▲Lon和▲Lat，地球半径取6371004米  
    deltaLon = accuracy * 360 / (2 * math.pi * 6371004 * math.cos((lat1 + lat2) * math.pi / 360));  
    deltaLat = accuracy * 360 / (2 * math.pi * 6371004);  
    #定义空的GeoDataFrame表，再往里加栅格  
    data = gpd.GeoDataFrame()  
    #定义空的list，后面循环一次就往里面加东西  
    LONCOL_list = []  
    LATCOL_list = []  
    geometry_list = []  
    HBLON_list = []  
    HBLAT_list = []  
    #计算行列要生成的栅格数量  
    #lon方向是lonsnum个栅格  
    lonsnum = int((lon2-lon1)/deltaLon)+1  
    #lat方向是latsnum个栅格  
    latsnum = int((lat2-lat1)/deltaLat)+1  
    for i in range(lonsnum):  
        for j in range(latsnum):  
            #第i列，第j行的栅格中心点坐标  
            HBLON = i*deltaLon + lonStart   
            HBLAT = j*deltaLat + latStart  
            #用周围的栅格推算三个顶点的位置
            HBLON_1 = (i+1)*deltaLon + lonStart  
            HBLAT_1 = (j+1)*deltaLat + latStart  
            #生成栅格的Polygon形状  
            grid_ij = Polygon([  
            (HBLON-deltaLon/2,HBLAT-deltaLat/2),  
            (HBLON_1-deltaLon/2,HBLAT-deltaLat/2),  
            (HBLON_1-deltaLon/2,HBLAT_1-deltaLat/2),  
            (HBLON-deltaLon/2,HBLAT_1-deltaLat/2)]) 
            #把生成的数据都加入到前面定义的空list里面  
            LONCOL_list.append(i)  
            LATCOL_list.append(j)  
            HBLON_list.append(HBLON)  
            HBLAT_list.append(HBLAT)  
            geometry_list.append(grid_ij)  
    #为geopandas文件的每一列赋值为刚刚的list  
    data['LONCOL'] = LONCOL_list  
    data['LATCOL'] = LATCOL_list  
    data['HBLON'] = HBLON_list  
    data['HBLAT'] = HBLAT_list  
    data['geometry'] = geometry_list  
    params = (lonStart,latStart,deltaLon,deltaLat)
    return data,params 

def grid_params(bounds,accuracy = 500):
    '''
    栅格参数获取

    输入
    -------
    bounds : List
        生成范围的边界，[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 
    accuracy : number
        栅格大小（米）
                                               

    输出
    -------
    params : List
        栅格参数(lonStart,latStart,deltaLon,deltaLat)，分别为栅格左下角坐标与单个栅格的经纬度长宽

    Examples
    -------
    >>> import transbigdata as tbd
    >>> bounds = [113.6,22.4,114.8,22.9]
    >>> tbd.grid_params(bounds,accuracy = 500)
    (113.6, 22.4, 0.004872390756896538, 0.004496605206422906)
    
    '''
    #划定栅格划分范围
    lon1 = bounds[0]  #经度1
    lat1 = bounds[1]  #纬度1
    lon2 = bounds[2]  #经度2
    lat2 = bounds[3]  #纬度2
    #取得左下角的经纬度  
    latStart = min(lat1, lat2);  
    lonStart = min(lon1, lon2);  
    #计算栅格的经纬度增加量大小▲Lon和▲Lat，地球半径取6371004米  
    deltaLon = accuracy * 360 / (2 * math.pi * 6371004 * math.cos((lat1 + lat2) * math.pi / 360));  
    deltaLat = accuracy * 360 / (2 * math.pi * 6371004);  
    return (lonStart,latStart,deltaLon,deltaLat)

def GPS_to_grids(lon,lat,params):
    '''
    GPS数据对应栅格编号。输入数据的经纬度列与栅格参数，输出对应的栅格编号

    输入
    -------
    lon : Series
        经度列
    lat : Series
        纬度列
    params : List
        栅格参数(lonStart,latStart,deltaLon,deltaLat)，分别为栅格左下角坐标与单个栅格的经纬度长宽
                                               
    输出
    -------
    LONCOL : Series
        经度栅格编号列
    LATCOL : Series
        纬度栅格编号列
    '''
    (lonStart,latStart,deltaLon,deltaLat) = params
    import numpy as np
    loncol = np.floor(((lon - (lonStart - deltaLon / 2))/deltaLon)).astype('int')  #np.floor()返回不大于输入参数的最大整数
    latcol = np.floor(((lat - (latStart - deltaLat / 2))/deltaLat)).astype('int')   
    return loncol,latcol


def grids_centre(loncol,latcol,params):
    '''
    栅格编号对应栅格中心点经纬度。输入数据的栅格编号与栅格参数，输出对应的栅格中心点

    输入
    -------
    LONCOL : Series
        经度栅格编号列
    LATCOL : Series
        纬度栅格编号列
    params : List
        栅格参数(lonStart,latStart,deltaLon,deltaLat)，分别为栅格左下角坐标与单个栅格的经纬度长宽
                                               
    输出
    -------
    HBLON : Series
        栅格中心点经度列
    HBLAT : Series
        栅格中心点纬度列
    '''
    (lonStart,latStart,deltaLon,deltaLat) = params
    hblon = loncol*deltaLon + lonStart #格子编号*格子宽+起始横坐标=格子中心横坐标  
    hblat = latcol*deltaLat + latStart
    return hblon,hblat

def gridid_to_polygon(loncol,latcol,params):
    '''
    栅格编号生成栅格的地理信息列。输入数据的栅格编号与栅格参数，输出对应的地理信息列

    输入
    -------
    LONCOL : Series
        经度栅格编号列
    LATCOL : Series
        纬度栅格编号列
    params : List
        栅格参数(lonStart,latStart,deltaLon,deltaLat)，分别为栅格左下角坐标与单个栅格的经纬度长宽
                                               
    输出
    -------
    geometry : Series
        栅格的矢量图形列
    '''
    (lonStart,latStart,deltaLon,deltaLat) = params
    HBLON = loncol*deltaLon + lonStart   
    HBLAT = latcol*deltaLat + latStart  
    #用周围的栅格推算三个顶点的位置
    HBLON_1 = (loncol+1)*deltaLon + lonStart  
    HBLAT_1 = (latcol+1)*deltaLat + latStart  
    df = pd.DataFrame()
    df['HBLON'] = HBLON
    df['HBLAT'] = HBLAT
    df['HBLON_1'] = HBLON_1
    df['HBLAT_1'] = HBLAT_1
    return df.apply(lambda r:Polygon([  
    (r['HBLON']-deltaLon/2,r['HBLAT']-deltaLat/2),  
    (r['HBLON_1']-deltaLon/2,r['HBLAT']-deltaLat/2),  
    (r['HBLON_1']-deltaLon/2,r['HBLAT_1']-deltaLat/2),  
    (r['HBLON']-deltaLon/2,r['HBLAT_1']-deltaLat/2)]),axis = 1)

def hexagon_grids(bounds,accuracy = 500):
    '''
    生成研究范围内的六边形渔网。

    输入
    -------
    bounds : List
        生成范围的边界，[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 
    accuracy : number
        六边形的边长（米）
                                               
    输出
    -------
    hexagon : GeoDataFrame
        六边形渔网的矢量图形
    ''' 
    #划定栅格划分范围
    (lon1,lat1,lon2,lat2) = bounds
    #取得左下角的经纬度  
    latStart = min(lat1, lat2);  
    lonStart = min(lon1, lon2);  
    latEnd = max(lat1, lat2);  
    lonEnd = max(lon1, lon2);  
    origin = gpd.GeoDataFrame([Point(lonStart,latStart),Point(lonEnd,latEnd)],columns = ['geometry'])
    origin.crs = {'init':'epsg:4326'}
    origin = origin.to_crs(epsg = 3857)
    x_o = origin['geometry'].iloc[0].x
    y_o = origin['geometry'].iloc[0].y
    x_d = origin['geometry'].iloc[1].x
    y_d = origin['geometry'].iloc[1].y

    lonsnum = (x_d-x_o)/accuracy
    latsnum = (y_d-y_o)/accuracy
    #1
    xs = np.arange(0,lonsnum,3)
    ys = np.arange(0,latsnum,2*(3/4)**0.5)
    xs = pd.DataFrame(xs,columns = ['x'])
    xs['tmp'] = 1
    ys = pd.DataFrame(ys,columns = ['y'])
    ys['tmp'] = 1
    df1 = pd.merge(xs,ys)
    #2
    xs = np.arange(1.5,lonsnum,3)
    ys = np.arange((3/4)**0.5,latsnum,2*(3/4)**0.5)
    xs = pd.DataFrame(xs,columns = ['x'])
    xs['tmp'] = 1
    ys = pd.DataFrame(ys,columns = ['y'])
    ys['tmp'] = 1
    df2 = pd.merge(xs,ys)
    df = pd.concat([df1,df2])
    df['x'],df['y'] = x_o+df['x']*accuracy,y_o+df['y']*accuracy
    def get_hexagon(x,y,accuracy):
        return Polygon([(x-accuracy,y),
             (x-accuracy/2,y+accuracy*(3/4)**0.5),
             (x+accuracy/2,y+accuracy*(3/4)**0.5),
             (x+accuracy,y),
             (x+accuracy/2,y-accuracy*(3/4)**0.5),
             (x-accuracy/2,y-accuracy*(3/4)**0.5),
             (x-accuracy,y)
            ]) 
    df['geometry'] = df.apply(lambda r:get_hexagon(r['x'],r['y'],accuracy),axis = 1)
    df = gpd.GeoDataFrame(df)
    df.crs = {'init':'epsg:3857'}
    df = df.to_crs(epsg = 4326)
    df = df[['geometry']]
    df['ID'] = range(len(df))
    return df


def gridid_sjoin_shape(data,shape,params,col = ['LONCOL','LATCOL']):
    '''
    输入数据（带有栅格经纬度编号两列），矢量图形与栅格化参数，输出数据栅格并对应矢量图形。
    
    输入
    -------
    data : DataFrame
        数据,（带有栅格经纬度编号两列）
    shape : GeoDataFrame
        矢量图形
    params : List
        栅格化参数
    col : List
        列名，[经度栅格编号，纬度栅格编号]

    输出
    -------
    data1 : DataFrame
        数据栅格并对应矢量图形
    '''
    LONCOL,LATCOL = col
    data1 = data.copy()
    data1 = gpd.GeoDataFrame(data1)
    data1['geometry'] = gridid_to_polygon(data1[LONCOL],data1[LATCOL],params)
    data1 = gpd.sjoin(data1,shape)
    return data1

def grid_params_gini(data,col = ['lon','lat'],accuracy = 500,gini = 'max',gap = 10,sample = 10000):
    '''
    获取最佳的栅格化参数，以基尼系数为标准
    输入
    ----------
    data : DataFrame
        数据
    col : List
        经纬度列
    accuracy : number
        网格大小
    gini : number
        min,max,或者median。基尼系数的选取标准
    gap : number
        精度,越大越精确，效果越好，计算量越大
    sample : number
        抽样多少数据做测试

    输出
    ----------
    params : List
        最佳的栅格化参数
    '''
    trajdata = data.copy()
    if len(trajdata)>sample:
        trajdata = trajdata.sample(sample)
    lon,lat = col
    lon1 = trajdata[lon].mean()
    lat1 = trajdata[lat].mean()
    bounds = [lon1,lat1,lon1,lat1]
    params = grid_params(bounds,accuracy = accuracy)
    lonstart,latstart,deltalon,deltalat = params
    x = np.linspace(lonstart,lonstart+deltalon,gap)
    y = np.linspace(latstart,latstart+deltalat,gap)
    xx,yy = np.meshgrid(x,y)
    tmp1 = pd.DataFrame()
    xx=xx.reshape(1,-1)
    yy=yy.reshape(1,-1)
    tmp1['lon'] = xx[0]
    tmp1['lat'] = yy[0]
    r = tmp1.iloc[0]
    #估算基尼系数
    def GiniIndex(p):
        cum = np.cumsum(sorted(np.append(p, 0)))
        sum = cum[-1]
        x = np.array(range(len(cum))) / len(p)
        y = cum / sum
        B = np.trapz(y, x=x)
        A = 0.5 - B
        G = A / (A + B)
        return G
    def getgini(r):
        lon1,lat1 = r['lon'], r['lat']
        params_tmp=[lon1,lat1,deltalon,deltalat]
        tmp = pd.DataFrame()
        tmp['LONCOL'],tmp['LATCOL'] = GPS_to_grids(trajdata[lon], trajdata[lat], params_tmp)
        tmp['count'] = 1
        tmp = tmp.groupby(['LONCOL','LATCOL'])['count'].sum().reset_index()
        Gini = GiniIndex(list(tmp['count']))
        return Gini
    tmp1['gini'] = tmp1.apply(lambda r:getgini(r),axis = 1)
    if gini == 'max':
        r = tmp1[tmp1['gini'] == tmp1['gini'].max()].iloc[0]
        print('Gini index: '+str(r['gini']))
    elif gini == 'min':
        r = tmp1[tmp1['gini'] == tmp1['gini'].min()].iloc[0]
        print('Gini index: '+str(r['gini']))
    elif gini == 'median':
        tmp1['tmp'] = abs(tmp1['gini']-tmp1['gini'].median())
        tmp1 = tmp1.sort_values(by = 'tmp')
        r = tmp1.iloc[0]
        print('Gini index: '+str(r['gini']))
    else:
        raise Exception('gini参数设定错误') 
    params = [r['lon'],r['lat'],deltalon,deltalat]
    return params