import random
from json import load
from math import atan2, pi

threshold = 0.2  # meters
dangerous_threshold = 0.3


def get_distance(x1, y1, z1, x2, y2, z2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5


class Clever:
    def __init__(self, ip):
        self.led = '#000000'
        self.status = "land"
        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0
        self.ip = ip
        self.voltage = 0
        self.commands = []
        self.path = []
        self.from_to = {
            'f': -1,
            't': -1
        }
        self.force_landed = False

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

    def addCommand(self, command):
        self.commands.append({
            "led": self.led,
            "status": command['command'],
            "pose": {
                "x": float(command['x']), "y": float(command['y']), "z": float(command['z']),
                "yaw": self.yaw
            }
        })

    def toTelem(self):
        return {
            "ip": self.ip,
            "led": self.led,
            "status": self.status,
            "pose": {
                "x": self.x, "y": self.y, "z": self.z,
                "yaw": self.yaw
            },
            "voltage": self.voltage,
            "nextp": self.toNewTelem()
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
            # print("Empty paths, return land")
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

                n = int(self.path[0][:-1]) \
                    # print('My path is now', self.path)
                nav_point = file_data['points'][n]
                nav_point['z'] = 1.5

                if self.path[0][-1:] == '0':
                    nav_point['z'] = 1.5
                elif self.path[0][-1:] == '1':
                    nav_point['z'] = 2.5

                dist = get_distance(nav_point['x'], nav_point['y'], nav_point['z'], self.x, self.y, self.z)
                if (dist < threshold) and (not checkCollisions(self, copters)):
                    try:
                        old_point = file_data['points'][int(self.path[0][:-1])]
                        self.path.pop(0)
                        new_point = file_data['points'][int(self.path[0][:-1])]
                        self.yaw = get_angle(old_point, new_point)
                    except:
                        pass
                    return self.toNewTelem(copters)

                else:
                    # print('Navigating to point', nav_point)
                    return {
                        "led": self.led,
                        "status": 'fly',  # fly, land
                        "pose": {
                            "x": nav_point['x'], "y": nav_point['y'], "z": nav_point['z'],
                            "yaw": self.yaw
                        }
                    }


def checkCollisions(c, copters):
    # print("Checking")
    paths = []
    for i in copters:
        if i != c:
            try:
                paths.append(i.path[0])
            except:
                pass
    print('Enemies are going to', paths, 'And i go to', c.path[0])
    fact = c.path[0] in paths
    '''
    if fact:
        pass
    # print("\n\n\nSome collisions!!!\n\n\n")
    
    else:
        # print("Everything is ok, but let me check")
        for i in copters:
            if i != c:
                if get_d(c, i) < dangerous_threshold:
                    if get_d_to_point(i, i.path[0]) < get_d_to_point(c, c.path[0]):
                        pass
    '''
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
        return atan2((o['x'] - n['x']), (o['y'] - n['y'])) - pi / 2
    except:
        return -pi / 2
