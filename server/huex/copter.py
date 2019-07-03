import random


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
        self.commands = []

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
            "nextp": self.toNewTelem()
        }

    def toNewTelem(self):
        if len(self.commands) == 0:
            return {
                "led": self.led,
                "status": self.status,
                "pose": {
                    "x": self.x, "y": self.y, "z": self.z,
                    "yaw": self.yaw
                }
            }
        else:
            return self.commands[len(self.commands) - 1]
       