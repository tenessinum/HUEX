import pygame
from pygame.locals import *
import urllib.request
import json
from OpenGL.GL import *
from OpenGL.GLU import *

ECHELON_HEIGHT = 1.5
COPTER_IP = "192.168.1.103"


class Camera():
    def __init__(self, pose, orientation):
        self.x, self.y, self.z = pose
        self.p, self.r, self.yw = orientation
        self.goto(self.x, self.y, self.z, self.p, self.r, self.yw)

    def goto(self, x, y, z, pitch, roll, yaw):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotatef(pitch, 1, 0, 0)
        glRotatef(yaw, 0, 1, 0)
        glRotatef(roll, 0, 0, 1)
        glTranslatef(-x, -y, -z)

    def move(self):
        pose = json.loads(urllib.request.urlopen('http://192.168.1.103:8081/data').read())
        self.x = pose['x']
        self.y = pose['y']
        self.z = pose['z']
        self.p = pose['pitch'] * 56 + 180
        self.yw = pose['roll'] * 56 + 180
        self.r = -pose['yaw'] * 56 - 90
        print("r: " + str(self.r), self.yw, sep=" || yw: ")
        self.goto(self.x, self.y, self.z, self.p, self.r, self.yw)

    def update(self):
        self.goto(self.x, self.y, self.z, self.p, self.r, self.yw)


def Grid(size):
    z=0
    glLineWidth(1)
    glColor3f(0.4, 0.4, 0.4)
    glBegin(GL_LINES)
    for x in range(-9,10):
        for y in range(-5,10):
            x*=size
            y*=size
            glVertex3f(x, y, z)
            glVertex3f(x + size, y, z)

            glVertex3f(x + size, y, z)
            glVertex3f(x + size, y + size, z)

            glVertex3f(x + size, y + size, z)
            glVertex3f(x, y + size, z)

            glVertex3f(x, y + size, z)
            glVertex3f(x, y, z)

    glEnd()


def Origin():
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)

    glVertex3f(0, 0, 0)
    glVertex3f(0.5, 0, 0)

    glVertex3f(0, 0, 0)
    glVertex3f(0, 0.5, 0)

    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 0.5)
    glEnd()


def Cube(pose, size, color):
    nx, ny, nz = pose
    pitch, roll, yaw = 0,0,0
    rgb = []
    for val in (color[1:3], color[3:5], color[5:7]):
        val = int(val, 16)
        rgb.append(val / 255)
    x, y, z = (-size / 2, -size / 2, -size / 2)

    glPushMatrix()
    glTranslatef(nx, ny, nz)
    glRotatef(pitch, 1, 0, 0)
    glRotatef(yaw, 0, 1, 0)
    glRotatef(roll, 0, 0, 1)

    glColor3f(rgb[0], rgb[1], rgb[2])
    glLineWidth(10)
    glBegin(GL_LINES)

    glVertex3f(x, y, z)
    glVertex3f(x + size, y, z)

    glVertex3f(x + size, y, z)
    glVertex3f(x + size, y + size, z)

    glVertex3f(x + size, y + size, z)
    glVertex3f(x, y + size, z)

    glVertex3f(x, y + size, z)
    glVertex3f(x, y, z)
    ###
    glVertex3f(x, y, z + size)
    glVertex3f(x + size, y, z + size)

    glVertex3f(x + size, y, z + size)
    glVertex3f(x + size, y + size, z + size)

    glVertex3f(x + size, y + size, z + size)
    glVertex3f(x, y + size, z + size)

    glVertex3f(x, y + size, z + size)
    glVertex3f(x, y, z + size)
    ###
    glVertex3f(x, y, z)
    glVertex3f(x, y, z + size)

    glVertex3f(x + size, y, z)
    glVertex3f(x + size, y, z + size)

    glVertex3f(x + size, y + size, z)
    glVertex3f(x + size, y + size, z + size)

    glVertex3f(x, y + size, z)
    glVertex3f(x, y + size, z + size)

    glEnd()
    glPopMatrix()


def Triangle():
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 1, 0)
    glVertex3f(1, 0, 0)
    glEnd()


def Marker(pose, size):
    x, y, z = pose
    glColor3f(0.4, 0.4, 0.4)
    glBegin(GL_POLYGON)

    glVertex3f(x, y, z)
    glVertex3f(x + size, y, z)

    glVertex3f(x + size, y, z)
    glVertex3f(x + size, y + size, z)

    glVertex3f(x + size, y + size, z)
    glVertex3f(x, y + size, z)

    glVertex3f(x, y + size, z)
    glVertex3f(x, y, z)

    glEnd()


def load_markers():
    markers = []
    map = str(urllib.request.urlopen('http://192.168.1.149:8000/static/map.txt').read())[2:].split("\\n")[:-1]
    #map = open("map.txt").read().split("\n")
    print(map)
    for marker in list(map):
        markers.append(list(marker.split(" "))[1:])
    print(markers)
    return markers


def load_roads(path):
    #data = json.loads(open(path).read())
    data = json.loads(urllib.request.urlopen('http://192.168.1.149:8000/static/roads.json').read())
    points, roads = data["points"], data["lines"]
    return points, roads


def Road(x1, y1, z1, x2, y2, z2):
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(3)
    glBegin(GL_LINES)
    glVertex3f(x1, y1, z1)
    glVertex3f(x2, y2, z2)
    glEnd()


def get_positions():
    copters = json.loads(urllib.request.urlopen('http://192.168.1.149:8000/get').read())["drones"]
    poses = []
    for copter in copters:
        data = [copter["pose"]]
        data.append(copter["led"])
        data.append(copter["status"])
        poses.append(data)
    return poses


def main():
    pygame.init()
    display = (1200, 700)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | OPENGLBLIT)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, (display[0] / display[1]), 0.1, 50.0)
    glEnable(GL_DEPTH_TEST)
    points, roads = load_roads("roads.json")
    print(points)
    markers = load_markers()
    cam = Camera((0, 0, 3), (-90, 0, 0))
    cam.goto(-0.30000000000000004, -4.000000000000002, 3, -75, 0, 0)
    i = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_w]:
                    cam.y += .1
                elif pygame.key.get_pressed()[pygame.K_s]:
                    cam.y -= .1
                elif pygame.key.get_pressed()[pygame.K_d]:
                    cam.x += .1
                elif pygame.key.get_pressed()[pygame.K_a]:
                    cam.x -= .1

                if pygame.key.get_pressed()[pygame.K_UP]:
                    cam.p += 3
                elif pygame.key.get_pressed()[pygame.K_DOWN]:
                    cam.p -= 3
                elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                    cam.r += 3
                elif pygame.key.get_pressed()[pygame.K_LEFT]:
                    cam.r -= 3
                elif pygame.key.get_pressed()[pygame.K_q]:
                    cam.z -= 0.1
                elif pygame.key.get_pressed()[pygame.K_e]:
                    cam.z += 0.1
                elif pygame.key.get_pressed()[pygame.K_h]:
                    file = open("pose" + str(i) + ".txt", "w")
                    data = (cam.x, cam.y, cam.z, cam.p, cam.r, cam.yw)
                    print("Saved!")
                    print(data)
                    for val in data:
                        file.write(str(val) + " ")
                        i += 1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        cam.update()
        # cam.move()

        for marker in markers:
            x, y, size = tuple(map(float, (marker[1], marker[2], marker[0])))
            Marker((x, y, 0.01), size)

        for point in points:
            Cube((point['x'], point['y'],ECHELON_HEIGHT),0.05,"#ffffff")
        for point in points:
            Cube((point['x'], point['y'],ECHELON_HEIGHT+1),0.05,"#ffffff")

        for road in roads:
            x1, y1, z1 = points[road["1"]]["x"], points[road["1"]]["y"], ECHELON_HEIGHT
            x2, y2, z2 = points[road["2"]]["x"], points[road["2"]]["y"], ECHELON_HEIGHT
            Road(x1, y1, z1, x2, y2, z2)
        for road in roads:
            x1, y1, z1 = points[road["1"]]["x"], points[road["1"]]["y"], ECHELON_HEIGHT + 1
            x2, y2, z2 = points[road["2"]]["x"], points[road["2"]]["y"], ECHELON_HEIGHT + 1
            Road(x1, y1, z1, x2, y2, z2)

        for pose in get_positions():
            if pose[2] == "fly":
                Cube((pose[0]["x"],pose[0]["y"],pose[0]["z"]), 0.3,pose[1])
            else:
                Cube((pose[0]["x"], pose[0]["y"], 0), 0.3, pose[1])

        #Cube((4, 4, 0, i, i, i), 0.3, "#ffffff")
        Origin()
        Grid(1)
        i += 1
        pygame.display.flip()
        pygame.time.wait(10)


main()
