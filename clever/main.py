from __future__ import print_function
import rospy
from clever import srv
from std_srvs.srv import Trigger
from mavros_msgs.srv import CommandBool
from threading import Thread
import requests as r
import math
from mapDown import map_down
import consts
from led.msg import LedModeColor


def get_distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)


SPEED = 0.5
land_voltage = 3.5

PARAMS_NAME = ('x', 'y', 'z', 'yaw', 'mode', 'cell_voltage', 'armed')

pub = rospy.Publisher('ledtopic', LedModeColor, queue_size=10)
rospy.init_node('flight')
get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry, persistent=True)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
set_position = rospy.ServiceProxy('set_position', srv.SetPosition)
land = rospy.ServiceProxy('land', Trigger)
arming = rospy.ServiceProxy('mavros/cmd/arming', CommandBool)

# globals
telemetry = False
flight_now = False
last_pose = False
fly_thread = Thread()
land_thread = Thread()
interrupt = False
connected = False
params = False


def send_telemetry(frame_id='aruco_map'):
    global telemetry, params
    # print('start')
    telemetry = get_telemetry(frame_id=frame_id)
    # print('got')
    params = {}
    for p in PARAMS_NAME:
        par = getattr(telemetry, p)
        if type(par) == float:
            par = round(par, 3)
        params[p] = par
    # print(params)
    v = r.get(consts.SERVER_IP + '/post', params)
    try:
        # print(v.text)
        # print('sent')
        # print(v.text)
        return v.json()
    except ValueError:
        print(v.text)
        return None



def take_off(z=1.5, speed=0.8):
    global last_pose
    print('Taking off')
    navigate(x=0, y=0, z=z, speed=speed, frame_id='body', auto_arm=True)
    rospy.sleep(2)
    last_pose = False
    # print('Aruco')
    # navigate(z=z, speed=speed, yaw=float('nan'), frame_id='aruco_map')
    # rospy.sleep(1)


def navigate_wait(x, y, z, speed=SPEED, yaw=float('nan'), frame_id='aruco_map', tolerance=0.2, timeout=10):
    global telemetry, interrupt
    navigate(x=x, y=y, z=z, speed=speed, yaw=yaw, frame_id=frame_id)
    print('start')
    while not interrupt:
        telem = telemetry
        # print(params)
        if get_distance(x, y, z, telem.x, telem.y, telem.z) < tolerance:
            set_position(x=x, y=y, z=z, yaw=yaw, frame_id=frame_id)
            break
    else:
        interrupt = False
        print('interrupted')
        set_position(x=telemetry.x, y=telemetry.y, z=telemetry.z, yaw=float('nan'), frame_id=frame_id)
    print('ready')


def land_to(x, y, z, speed=SPEED, yaw=float('nan'), frame_id='aruco_map', tolerance=0.2): # deprecated
    global telemetry, interrupt, flight_now
    navigate(x=x, y=y, z=z, speed=speed, yaw=yaw, frame_id=frame_id)
    print('start')
    while not interrupt:
        telem = telemetry
        # print(telem)
        if not telemetry.armed:
            flight_now = False
            break
        if get_distance(x, y, z, telem.x, telem.y, telem.z) < tolerance:
            land()
            while telemetry.armed:
                rospy.sleep(0.3)
            rospy.sleep(1)
            flight_now = False
            # set_position(x=x, y=y, z=z, yaw=yaw, frame_id=frame_id)
            break
    else:
        interrupt = False
        print('interrupted')
        set_position(x=telemetry.x, y=telemetry.y, z=telemetry.z, yaw=float('nan'), frame_id=frame_id)
    print('landtoready')


def new_land():
    global telemetry, interrupt, last_pose

    if telemetry.armed:
        land()
        while telemetry.armed:
            # print('land armed', telemetry.armed)
            rospy.sleep(0.3)
        rospy.sleep(1)
    print('land stopped')


def fly(request, tgt=navigate_wait):
    global fly_thread, last_pose
    if not fly_thread.is_alive():
        for n in request['pose']:
            request['pose'][n] = round(float(request['pose'][n]), 3)

        if request['pose'] != last_pose:
            last_pose = request['pose']

            if request['pose']['z'] <= 0:
                request['pose']['z'] = get_telemetry(frame_id='aruco_map').z

            print('Navigating from', params)
            print('Navigating to', request['pose'], tgt)

            fly_thread = Thread(target=tgt,
                                kwargs={'x': request['pose']['x'], 'y': request['pose']['y'],
                                        'z': request['pose']['z'], 'speed': SPEED, 'yaw': request['pose']['yaw'],
                                        'frame_id': 'aruco_map'})
            fly_thread.daemon = True
            fly_thread.start()
            # navigate_wait(x=request['pose']['x'], y=request['pose']['y'], z=request['pose']['z'], speed=SPEED,
            #               yaw=float('nan'), frame_id='aruco_map')
        else:
            print('pose equals')
    else:
        print('alive')


def force_land(ans=""):
    global interrupt
    if fly_thread.is_alive():
        interrupt = True
    print("Force land. " + ans)
    color = hex_to_rgb('#FF8000')
    to_led(*color, mode='blink')
    land()
    quit()


def hex_to_rgb(input_hex):
    input_hex = input_hex.replace("#", '')
    return int(input_hex[:2], 16), int(input_hex[2:4], 16), int(input_hex[4:], 16)


def to_led(r,g,b,mode):
    global pub
    message = LedModeColor()
    message.color.r = r
    message.color.g = g
    message.color.b = b
    message.mode = mode
    pub.publish(message)


rospy.sleep(10)
map_down()

while not rospy.is_shutdown():
    try:

        result = send_telemetry()
        if result is None:
            result = oldresult

        if result['status'] == 'take_off' and not telemetry.armed:
            # led.mode = "blink"
            take_off()
            # led.mode = "off"
        if result['status'] == 'land' and telemetry.armed:
            print('Landing')
            if fly_thread.is_alive():
                interrupt = True
                rospy.sleep(1)
                interrupt = False

            if not land_thread.is_alive():
                land_thread = Thread(target=new_land)
                land_thread.daemon = True
                land_thread.start()
                print('thread started')
            else:
                print('alive')
        if result['status'] == 'fly':
            if not land_thread.is_alive():
                if telemetry.cell_voltage <= land_voltage:
                    force_land("Low voltage")
                else:
                    if telemetry.armed:
                        fly(result)
                    else:
                        take_off()
        if result['status'] == 'force_land':
            force_land()

        color = hex_to_rgb(result['led'])
        to_led(*color, mode='fill')
        # led.mode = 'fill'
        # colors = hex_to_rgb(result['led'])
        # led.r = colors[0]
        # led.g = colors[1]
        # led.b = colors[2]
        oldresult = result.copy()

    except r.exceptions.ConnectionError:
        connected = False
        to_led(255, 0, 0, 'blink')

        print('Server fallen down, sleep 2 secs.')
