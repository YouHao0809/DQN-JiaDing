"""
Open Source Routing Machine (OSRM)
"""

import os
import requests
import json
import time
import math
import numpy as np
from subprocess import Popen, PIPE

from lib.Constants import *

import time
import collections


class OsrmEngine(object):
    """
    OsrmEngine is the class for the routing server
    Attributes:
        exe_loc: path of the routing server (osrm-routed executable)
        map_loc: path of the road network file
        ghost: host ip address
        gport: host port
        cst_speed: constant vehicle speed when road network is disabled (in meters/second
    """

    def __init__(self,
                 exe_loc,
                 map_loc,
                 ghost='localhost',
                 gport=5000,
                 cst_speed=CST_SPEED):
        # if not os.path.isfile(exe_loc):
        #     raise Exception("Could not find the routing server at %s" % exe_loc)
        # else:
        #     self.exe_loc = exe_loc
        # if not os.path.isfile(map_loc):
        #     raise Exception("Could not find osrm road network data at %s" % map_loc)
        # else:
        #     self.map_loc = map_loc
        self.map_loc = map_loc
        self.exe_loc = exe_loc
        self.ghost = ghost
        self.gport = gport
        self.cst_speed = cst_speed
        self.history = collections.OrderedDict()
        self.history_size = 80000
        # remove any open instance
        # if self.check_server():
        #     self.kill_server()

    # kill any routing server currently running before starting something new
    def kill_server(self):
        pass

    # check if server is already running
    def check_server(self):
        try:
            if requests.get("http://%s:%d" % (self.ghost, self.gport)).status_code == 400:
                return True
        except requests.ConnectionError:
            return False

    # start the routing server
    def start_server(self):
        pass

    # restart the routing server
    def restart_server(self):
        pass

    # generate the request in url format
    def create_url(self, olng, olat, dlng, dlat, steps="false", annotations="false"):
        return "http://%s:%d/route/v1/driving/%.6f,%.6f;%.6f,%.6f?alternatives=false&steps=%s&annotations=%s&geometries=geojson" % (
            self.ghost, self.gport, olng, olat, dlng, dlat, steps, annotations)

    # send the request and get the response in Json format
    def call_url(self, url):
        if url in self.history:
            return self.history[url]
        count = 0
        while count < 100:
            try:
                response = requests.get(url, timeout=0.005)
                json_response = response.json()
                code = json_response['code']
                if code == 'Ok':
                    if len(self.history) >= self.history_size:
                        self.history.popitem()
                    self.history[url] = (json_response, True)
                    return (json_response, True)
                else:
                    print("Error: %s" % (json_response['message']))
                    print(url)
                    return (json_response, False)
            except requests.exceptions.Timeout:
                # print(url)
                self.restart_server()
                count += 1
            except Exception as err:
                print("Failed: %s" % (url))
                return (None, False)
        print("The routing server \"http://%s:%d\" fails after 10 retries... :(" % (self.ghost, self.gport))

    # get the best route from origin to destination
    def get_routing(self, olng, olat, dlng, dlat):
        if IS_ROAD_ENABLED:
            url = self.create_url(olng, olat, dlng, dlat, steps="true", annotations="false")
            (response, code) = self.call_url(url)
            if code:
                return response['routes'][0]['legs'][0]
            else:
                return None
        else:
            dis, dur = self.get_distance_duration(olng, olat, dlng, dlat)
            leg = {'distance': dis, 'duration': dur}
            steps = []

            step = {'distance': dis, 'duration': dur}
            step['geometry'] = {'coordinates': [[olng, olat], [dlng, dlat]]}
            steps.append(step)

            if not np.isclose(dis, 0.0):
                step = {'distance': 0, 'duration': 0}
                step['geometry'] = {'coordinates': [[dlng, dlat], [dlng, dlat]]}
                steps.append(step)

            leg['steps'] = steps
            return leg

    # get the distance of the best route from origin to destination
    # if road network is not enabled, return Euclidean distance
    def get_distance(self, olng, olat, dlng, dlat):
        try:
            if IS_ROAD_ENABLED:
                url = self.create_url(olng, olat, dlng, dlat, steps="false", annotations="false")
                (response, code) = self.call_url(url)
                if code:
                    return response['routes'][0]['distance']
                else:
                    return None
            else:
                return (6371000 * 2 * math.pi / 360 * np.sqrt(
                    (math.cos((olat + dlat) * math.pi / 360) * (olng - dlng)) ** 2 + (olat - dlat) ** 2))
        except:
            print(olng, olat, dlng, dlat)

    # get the duration of the best route from origin to destination
    # if road network is not enabled, return the duration based on Euclidean distance and constant speed
    def get_duration(self, olng, olat, dlng, dlat):
        if IS_ROAD_ENABLED:
            url = self.create_url(olng, olat, dlng, dlat, steps="false", annotations="false")
            (response, code) = self.call_url(url)
            if code:
                return response['routes'][0]['duration']
            else:
                return None
        else:
            return self.get_distance(olng, olat, dlng, dlat) / self.cst_speed

    # get both distance and duration
    def get_distance_duration(self, olng, olat, dlng, dlat):
        if IS_ROAD_ENABLED:
            url = self.create_url(olng, olat, dlng, dlat, steps="false", annotations="false")
            (response, code) = self.call_url(url)
            if code:
                return (response['routes'][0]['distance'], response['routes'][0]['duration'])
            else:
                return None
        else:
            return self.get_distance(olng, olat, dlng, dlat), self.get_duration(olng, olat, dlng, dlat)
