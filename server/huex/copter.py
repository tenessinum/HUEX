import random
from json import load

threshold = 0.2  # meters


def get_distance(x1, y1, z1, x2, y2, z2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5


class Clever:
    def __init__(self, ip):
        r = lambda: random.randint(0, 255)
        self.led = '#%02X%02X%02X' % (r(), r(), r())
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
        if len(self.commands) == 0:
            return {
                "led": self.led,
                "status": self.status,
                "pose": {
                    "x": self.x, "y": self.y, "z": self.z,
                    "yaw": self.yaw
                }
            }
        elif len(self.commands) == 1:
            return self.commands[0]
        else:
            '''nav_point = self.commands[0]
            dist = get_distance(nav_point['pose']['x'], nav_point['pose']['y'], nav_point['pose']['z'], self.x, self.y,
                                self.z)
            if (dist < threshold or (
                    self.status == 'land' and self.commands[0]['status'] == 'land')) and not checkCollisions(self,
                                                                                                             copters):
                self.from_to['f'] = self.path.pop(0)
                try:
                    self.from_to['t'] = self.path[0]
                except:
                    self.from_to['t'] = self.from_to['f']
                self.commands.pop(0)

            if self.commands[0]['status'] == 'land':
                self.from_to = {'f': -1, 't': -1}
            return self.commands[0]'''
            if not self.path:
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

                    n = int(self.path[len(self.path) - 1][:-1])
                    nav_point = file_data['points'][n]
                    nav_point['z'] = 0
                    if self.path[len(self.path) - 1] == '0':
                        nav_point['z'] = 1.5
                    elif self.path[len(self.path) - 1] == '1':
                        nav_point['z'] = 2.5

                    dist = get_distance(nav_point['x'], nav_point['y'], nav_point['z'], self.x, self.y, self.z)
                    if (dist < threshold or (
                            self.status == 'land' and self.commands[0]['status'] == 'land')) and not checkCollisions(
                        self,
                        copters):
                        return {
                            "led": self.led,
                            "status": 'fly',  # fly, land
                            "pose": {
                                "x": nav_point['x'], "y": nav_point['z'], "z": nav_point['z'],
                                "yaw": self.yaw
                            }
                        }
                    else:
                        return {
                            "led": self.led,
                            "status": 'fly',  # fly, land
                            "pose": {
                                "x": self.x, "y": self.y, "z": self.z,
                                "yaw": self.yaw
                            }
                        }


def checkCollisions(c, copters):
    paths = []
    for i in copters:
        if i != c:
            try:
                paths.append(i.path[0])
            except:
                pass

    fact = c.path[0] in paths
    if fact:
        print("Some collisions")

    return fact
