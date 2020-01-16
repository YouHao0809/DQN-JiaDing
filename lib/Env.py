"""
environment class for the deep Q network (DQN)
"""

from lib.Agents import *
from lib.Demand import *
from lib.Constants import *

import gym
from gym import spaces
import copy
import itertools

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory


class RebalancingEnv(gym.Env):
    """
    RebalancingEnv is the environment class for DQN
    Attributes:
        model: AMoD system to train
        dT: time interval for training
        penalty: penalty of rebalancing a vehicle
        action_space: action space
        state: the system state
        center: the centroid of cells
        input_dim: input dimension
    """

    def __init__(self, model, penalty=-10, osrm=None):  # 修改
        self.model = model
        self.frames = []
        self.dT = INT_REBL
        self.penalty = penalty
        self.action_space = spaces.Discrete(9)  # 动作空间数目
        self.state = np.zeros((4, Mlng, Mlat))  # 从3改为了4
        self.center = np.zeros((Mlng, Mlat, 2))
        self.input_dim = 3 * Mlng * Mlat
        self.step_count = 0
        self.epi_count = 0
        self.total_reward = 0.0
        self.osrm = osrm  # 修改
        self.orp_action = None  # 前50步采取orp确定action

    def edge_value(self):
        #记录订单数
        memo = [[0] * Nlng for i in range(Nlat)]
        print(len(self.model.reqs))
        if(len(self.model.reqs)<100):
            for req in self.model.reqs:
                lng = req.olng
                lat = req.olat
                a = int((lng-Olng)/Elng)
                b = int((lat-Olat)/Elat)
                memo[a][b] += 20
        else:
            for i in range(1,101):
                lng = self.model.reqs[-i].olng
                lat = self.model.reqs[-i].olat
                a = int((lng - Olng) / Elng)
                b = int((lat - Olat) / Elat)
                memo[a][b] += 20
        #车辆的所在方格
        mylat = self.model.vehs[-1].lat
        mylng = self.model.vehs[-1].lng
        my_xindex = int((mylng-Olng)/Elng)
        my_yindex = int((mylat-Olat)/Elat)
        #计算value
        value = 0
        print("-"*10,my_xindex,my_yindex,"-"*10)
        #按照订单
        for i in range(-4,5):
            for j in range(-4,5):
                if(my_xindex+i<Nlng>=0 and my_xindex+i<Nlng and my_yindex+j>=0 and my_yindex+j<Nlat):
                    value+=memo[my_xindex+i][my_yindex+j]
        #按照地域
        if (mylat > down1 and mylat < up1 and mylng > left1 and mylng < right1):
            value += 50
        if(not (mylat>down1 and mylat<up1 and mylng>left1 and mylng<right1)):
            value -= 50
        if(not (mylat>down2 and mylat<up2 and mylng>left2 and mylng<right2)):
            value -= 50
        if(not (mylat>down3 and mylat<up3 and mylng>left3 and mylng<right3)):
            value -= 50
        print("-"*10,value,"-"*10)
        return value

    def step(self, action, logpath=None):
        self.step_count += 1
        print("#{} i'm at the start of the step~".format(self.step_count))
        print('idle cnt:', sum([self.model.vehs[vid].idle for vid in range(FLEET_SIZE)]))
        print('    time:{}  request:{}  reject:{}'.format(self.model.T, len(self.model.reqs), len(self.model.rejs)))
        reqs_0 = len(self.model.reqs)
        rejs_0 = len(self.model.rejs)
        model_ = copy.deepcopy(self.model)

        # if self.step_count > 50:
        #     self.act(action)
        # else: # 前50步采取orp确定action
        #     self.orp_action, route = self.model.get_orp_action(self.osrm, self.model.T)
        #     self.model.vehs[-1].build_route(self.osrm, route)
        self.act(action)

        reward = 0 if action == 0 else self.penalty
        flag = False
        T = self.model.T
        T_ = self.model.T + INT_REBL
        while T < T_:
            T += INT_ASSIGN
            self.model.dispatch_at_time(self.osrm, T)  # 修改
            # self.frames.append(copy.deepcopy(self.model.vehs))
            model_.dispatch_at_time(self.osrm, T)  # 修改
            if not self.is_vehicle_idle():
                reward += model_.get_total_cost() - self.model.get_total_cost()
                reward += self.edge_value()
                flag = True
                break
        while T < T_:
            T += INT_ASSIGN
            self.model.dispatch_at_time(self.osrm, T)  # 修改
            # self.frames.append(copy.deepcopy(self.model.vehs))  
        while not self.is_vehicle_idle():
            # print("#{} i'm in a while loop~".format(self.step_count))
            # print('idle cnt: ', sum([self.model.vehs[vid].idle for vid in range(FLEET_SIZE)]))
            T = self.model.T
            T_ = self.model.T + INT_REBL
            while T < T_:
                T += INT_ASSIGN
                self.model.dispatch_at_time(self.osrm, T)  # 修改
                # self.frames.append(copy.deepcopy(self.model.vehs))

        print('    time:{}  request add:{}  reject add:{}'.format(self.model.T,
                                                                  len(self.model.reqs) - reqs_0,
                                                                  len(self.model.rejs) - rejs_0))

        if flag:
            self.epi_count += 1
            self.total_reward += reward
            msg = "step %d; T: %d; total reward: %.2f; average reward: %.2f - action: %s; reward: %.2f" % (
                self.step_count, self.model.T, self.total_reward, self.total_reward / self.epi_count,
                "noop" if action == 0 else
                "ne" if action == 1 else
                "e" if action == 2 else
                "se" if action == 3 else
                "s" if action == 4 else
                "sw" if action == 5 else
                "w" if action == 6 else
                "nw" if action == 7 else
                "n" if action == 8 else "error!", reward)
            print(msg)
            if logpath is not None:
                with open(logpath, 'a') as f:
                    f.write(msg + '\n')
        self.update_state()
        # print(self.state)
        return self.state, reward, flag, {}

    def act(self, action, vid=-1):
        veh = self.model.vehs[vid]
        self.model.act(self.osrm, veh, action, self.center)  # 修改

    def reset(self):
        self.update_state()
        # self.amods.append( copy.deepcopy(self.amod) )
        return self.state

    def is_vehicle_idle(self, vid=-1):
        return self.model.vehs[vid].idle

    def update_state(self, vid=-1):
        veh = self.model.vehs[vid]
        self.state, self.center = self.model.get_state(veh)  # 这里很慢
