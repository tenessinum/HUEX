import random
from json import load
from math import atan2, pi

threshold = 0.2  # meters
dangerous_threshold = 0.3


def get_distance(x1, y1, z1, x2, y2, z2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5


class Clever:
    z = 0
    yaw = -pi / 2
    voltage = 0
    led = '#000000'
    status = "land"
    last_point = -1
    force_landed = False

    def __init__(self, ip):
        self.path = []
        self.busy_points = []
        self.x = random.randint(0, 100) / 100
        self.y = random.randint(0, 100) / 100
        self.ip = ip

    def random(self):
        r = lambda: random.randint(0, 255)
        self.led = '#%02X%02X%02X' % (r(), r(), r())
        self.x = random.randint(0, 2000) / 1000
        self.y = random.randint(0, 2000) / 1000
        self.z = random.randint(0, 2000) / 1000
        self.yaw = random.randint(0, 62831) / 10000

    def toDict(self):
        return {
            "led": self.led,
            "status": self.status,
            "pose": {
                "x": self.x, "y": self.y, "z": self.z,
                "yaw": self.yaw
            }
        }

    def toTelem(self, copters=[]):
        return {
            "ip": self.ip,
            "led": self.led,
            "status": self.status,
            "pose": {
                "x": self.x, "y": self.y, "z": self.z,
                "yaw": self.yaw
            },
            "voltage": self.voltage,
            "nextp": self.toNewTelem(copters)
        }

    def toNewTelem(self, copters=[]):
        if self.force_landed:
            return {
                "led": self.led,
                "status": 'force_land',
                "pose": {
                    "x": self.x, "y": self.y, "z": self.z,
                    "yaw": self.yaw
                }
            }
        if not self.path:
            self.busy_points = []
            # print("Empty paths, return land")
            self.status = 'land'
            return {
                "led": self.led,
                "status": 'land',  # fly, land
                "pose": {
                    "x": self.x, "y": self.y, "z": 1.5,
                    "yaw": self.yaw
                }
            }
        else:
            with open('static/roads.json', 'r') as f:
                file_data = load(f)

                if self.path[0] == '-1':
                    self.last_point = self.path.pop(0)
                    self.status = 'land'
                    return {
                        "led": self.led,
                        "status": 'land',
                        "pose": {
                            "x": self.x, "y": self.y, "z": 1.5,
                            "yaw": self.yaw
                        }
                    }
                self.status = 'fly'
                n = int(self.path[0][:-1])
                # print('My path is now', self.path)
                nav_point = file_data['points'][n]
                nav_point['z'] = 1.5

                if self.path[0][-1:] == '0':
                    nav_point['z'] = 1.5
                elif self.path[0][-1:] == '1':
                    nav_point['z'] = 2.5
                dist = get_distance(nav_point['x'], nav_point['y'], nav_point['z'], self.x, self.y, self.z)
                collisions = check_collisions(self, copters)
                if (dist < threshold) and (not collisions):
                    self.last_point = self.path.pop(0)
                    return self.toNewTelem(copters)
                else:
                    # print(self.ip, 'dist to point is', dist)
                    return {
                        "led": self.led,
                        "status": 'fly',  # fly, land
                        "pose": {
                            "x": nav_point['x'], "y": nav_point['y'], "z": nav_point['z'],
                            "yaw": self.yaw
                        }
                    }


def check_collisions(c, copters):
    # print(c.ip)
    paths = []

    # print(c.ip, 'Checking drone for collisions', copters)

    for copter in copters:
        if copter.ip != c.ip:
            # print(copter.ip, 'status is', copter.status)
            if copter.status != 'land':
                try:
                    # print(copter.ip, 'last point and path are', copter.last_point, copter.path)
                    if copter.last_point != -1:
                        paths.append(copter.last_point)
                except:
                    pass
                try:
                    paths.append(copter.path[0])
                except:
                    pass

    # print(c.ip, 'Busy points are', *paths)

    try:
        fact = c.path[1] in paths
        # (c.ip, 'I am flying to', c.path[0], 'next point is', c.path[1], 'and my enemies are flying to', paths, 'fact is', fact)
    except:
        fact = False

    '''if fact:
        pass
        print(c.ip, "I am going to crush into someone")
    else:
        print(c.ip, "Everything is ok")
        for i in copters:
            if i != c:
                if get_d(c, i) < dangerous_threshold:
                    if get_d_to_point(i, i.path[0]) < get_d_to_point(c, c.path[0]):
                        c.force_landed = True
                        i.force_landed = True'''

    return fact


def get_d(c1, c2):
    return get_distance(c1.x, c1.y, c1.z, c2.x, c2.y, c2.z)


def get_d_to_point(c, p):
    with open('static/roads.json', 'r') as f:
        file_data = load(f)

        n = int(p[:-1])
        nav_point = file_data['points'][n]
        nav_point['z'] = 1.5

        if p[-1:] == '0':
            nav_point['z'] = 1.5
        elif p[-1:] == '1':
            nav_point['z'] = 2.5

        return get_distance(nav_point['x'], nav_point['y'], nav_point['z'], c.x, c.y, c.z)


def get_angle(o, n):
    try:
        return -pi / 2  # atan2((o['x'] - n['x']), (o['y'] - n['y'])) - pi / 2
    except:
        return -pi / 2
