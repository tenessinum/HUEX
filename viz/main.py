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
        self.p = pose['pitch'] * 56 + 130
        self.yw = pose['roll'] * 56 + 180
        self.r = -pose['yaw'] * 56 - 90
        print("r: " + str(self.r), self.yw, sep=" || yw: ")
        self.goto(self.x, self.y, self.z, self.p, self.r, self.yw)
    def update(self):
        self.goto(self.x, self.y, self.z, self.p, self.r, self.yw)

def Cube(pose,size):
    x,y,z = pose
    glBegin(GL_POLYGON)
    glVertex3f(x, y, z)
    glVertex3f(x + size, y, z)

    glVertex3f(x + size, y, z)
    glVertex3f(x + size, y + size, z)

    glVertex3f(x + size, y + size, z)
    glVertex3f(x, y + size, z)

    glVertex3f(x, y + size, z)
    glVertex3f(x, y, z)
    ###
    glVertex3f(x, y, z+size)
    glVertex3f(x + size, y, z+size)

    glVertex3f(x + size, y, z+size)
    glVertex3f(x + size, y + size, z+size)

    glVertex3f(x + size, y + size, z+size)
    glVertex3f(x, y + size, z+size)

    glVertex3f(x, y + size, z+size)
    glVertex3f(x, y, z+size)
    ###
    glVertex3f(x, y, z)
    glVertex3f(x, y, z+size)

    glVertex3f(x+size, y, z)
    glVertex3f(x+size, y, z+size)

    glVertex3f(x+size, y+size, z)
    glVertex3f(x+size, y+size, z+size)

    glVertex3f(x, y + size, z)
    glVertex3f(x, y + size, z + size)

    glEnd()


def Triangle():
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 1, 0)
    glVertex3f(1, 0, 0)
    glEnd()


def Marker(pose, size):
    x, y, z = pose
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


def load_markers(path):
    markers = []
    map = urllib.request.urlopen('http://192.168.1.149:8000/static/map.txt').read()
    for marker in list(open(path).read().split("\n")):
        markers.append(list(marker.split(" ")))
    return markers


def load_roads(path):
    #data = json.loads(open(path).read())
    data = json.loads(urllib.request.urlopen('http://192.168.1.149:8000/static/roads.json').read())
    points, roads = data["points"], data["lines"]
    return points, roads


def Road(x1, y1, z1, x2, y2, z2):
    glBegin(GL_LINES)
    glVertex3f(x1, y1, z1)
    glVertex3f(x2, y2, z2)
    glEnd()

def get_positions():
    copters = json.loads(urllib.request.urlopen('http://192.168.1.149:8000/get').read())["drones"]
    poses = []
    for copter in copters:
        poses.append(copter["pose"])
    return poses

def main():
    pygame.init()
    display = (1200, 700)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | OPENGLBLIT)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, (display[0] / display[1]), 0.1, 50.0)


    points, roads = load_roads("roads.json")
    markers = load_markers("map.txt")
    cam = Camera((0, 0, 3), (-90, 0, 0))
    cam.goto(-1.463, -1.334, 2.665, 110.896, -149.304, 175.576)
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
                    file = open("pose"+str(i)+".txt", "w")
                    data=(cam.x,cam.y,cam.z,cam.p,cam.r,cam.yw)
                    print("Saved!")
                    print(data)
                    for val in data:
                        file.write(str(val)+" ")
                        i+=1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        cam.update()
        #cam.move()
        for marker in markers:
            x, y, size = tuple(map(float, (marker[2], marker[3], marker[1])))
            Marker((x, y, 0.0), size)
        for road in roads:
            x1, y1, z1 = points[road["1"]]["x"], points[road["1"]]["y"], ECHELON_HEIGHT
            x2, y2, z2 = points[road["2"]]["x"], points[road["2"]]["y"], ECHELON_HEIGHT
            Road(x1, y1, z1, x2, y2, z2)
        for road in roads:
            x1, y1, z1 = points[road["1"]]["x"], points[road["1"]]["y"], ECHELON_HEIGHT+1
            x2, y2, z2 = points[road["2"]]["x"], points[road["2"]]["y"], ECHELON_HEIGHT+1
            Road(x1, y1, z1, x2, y2, z2)
        for pose in get_positions():
            Cube((pose["x"],pose["y"],pose["z"]), 0.3)

        pygame.display.flip()
        pygame.time.wait(10)


main()
