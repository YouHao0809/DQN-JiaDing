"""
constants are found here
"""

from lib.Demand import *

# fleet size and vehicle capacity
FLEET_SIZE = 40
VEH_CAPACITY = 4

# demand matrix, demand volume and its nickname
DMD_MAT = M_MIT
DMD_VOL = D_MIT
DMD_STR = "MIT"

# warm-up time, study time and cool-down time of the simulation (in seconds)
T_WARM_UP = 60 * 30
T_STUDY = 60 * 60
T_COOL_DOWN = 60 * 30
T_TOTAL = (T_WARM_UP + T_STUDY + T_COOL_DOWN)

# methods for vehicle-request assignment, reoptimization and rebalancing
# ins = insertion heuristics
# hsa = hybrid simulated annealing
# sar = simple anticipatory rebalancing, orp = optimal rebalancing problem, dqn = deep Q network
MET_ASSIGN = "ins"
MET_REOPT = "no"
MET_REBL = "dqn"  # 在仿真时用的再平衡方式，训练时始终为 “no”

# intervals for vehicle-request assignment, reoptimization and rebalancing
INT_ASSIGN = 120  # 派单时间间隔，原来为30s
INT_REOPT = 120  # 优化时间间隔，原来为30s
INT_REBL = 600  # 再平衡时间，原来为150s

# if road network is enabled, use the routing server; otherwise use Euclidean distance
IS_ROAD_ENABLED = False  # False则不使用路网计算距离
# if true, activate the animation
IS_ANIMATION = False

# maximum detour factor and maximum wait time window
MAX_DETOUR = 1.5
MAX_WAIT = 60 * 10  # 最大等待时间

# constant vehicle speed when road network is disabled (in meters/second)
CST_SPEED = 10  # 车辆速度，原来为6m/s

# probability that Elng request is sent in advance (otherwise, on demand)
PROB_ADV = 0.0
# time before which system gets notified of the in-advance requests
T_ADV_REQ = 60 * 30

# coefficients for wait time and in-vehicle travel time in the utility function
COEF_WAIT = 1.5
COEF_INVEH = 1.0

# map width and height
MAP_WIDTH = 4.65
MAP_HEIGHT = 4.23

# coordinates
# (Olng, Olat) lower left corner
Olng = 121.163896  # 修改后经度
Olat = 31.257747
# (Dlng, Dlat) upper right corner
Dlng = 121.344491  # 修改后经度，经纬度构成一个正方形
Dlat = 31.438342
# number of cells in the gridded map
Nlng = 20 # 网格大小
Nlat = 20
# number of moving cells centered around the vehicle
Mlng = 20  # 车辆感知范围
Mlat = 20
# length of edges of Elng cell
Elng = (Dlng - Olng) / Nlng
Elat = (Dlat - Olat) / Nlat

#边界
left1 = Olng+Elng*0.4
left2 = Olng+Elng*0.3
left3 = Olng+Elng*0.2
right1 = Olng+Elng*0.6
right2 = Olng+Elng*0.7
right3 = Olng+Elng*0.8
up1 = Olat+Elat*0.4
up2 = Olat+Elat*0.3
up3 = Olat+Elat*0.2
down1 = Olat+Elat*0.6
down2 = Olat+Elat*0.7
down3 = Olat+Elat*0.8

INSERTION_OUTPUT = False  # 是否显示启发式插入结果
INT_SAVE = 100  # 保存权重间隔
MODEL_OUTPUT = False  # 是否输出模型
