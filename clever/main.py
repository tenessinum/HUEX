from __future__ import print_function
import rospy
from clever import srv
from std_srvs.srv import Trigger
from mavros_msgs.srv import CommandBool
from threading import Thread
import requests as r
import math


def get_distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)


SPEED = 0.8

PARAMS_NAME = ('x', 'y', 'z', 'yaw', 'mode', 'cell_voltage')

rospy.init_node('flight')
get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
set_position = rospy.ServiceProxy('set_position', srv.SetPosition)
land = rospy.ServiceProxy('land', Trigger)
arming = rospy.ServiceProxy('mavros/cmd/arming', CommandBool)

# globals
telemetry = False
flight_now = False
last_pose = False
fly_thread = Thread()
interrupt = False


def send_telemetry(frame_id='aruco_map'):
    global telemetry
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
    v = r.get('http://192.168.1.168:8000/post', params)
    # print('sent')
    # print(v.text)
    return v.json()


def take_off(z=1.5, speed=SPEED):
    print('Taking off')
    navigate(x=0, y=0, z=z, speed=speed, frame_id='body', auto_arm=True)
    rospy.sleep(2)
    # print('Aruco')
    # navigate(z=z, speed=speed, yaw=float('nan'), frame_id='aruco_map')
    # rospy.sleep(1)


def navigate_wait(x, y, z, speed, yaw=float('nan'), frame_id='aruco_map', tolerance=0.2, timeout=10):
    global telemetry, interrupt
    navigate(x=x, y=y, z=z, speed=speed, yaw=yaw, frame_id=frame_id)
    print('start')
    while not interrupt:
        telem = telemetry
        # print(telem)
        if get_distance(x, y, z, telem.x, telem.y, telem.z) < tolerance:
            set_position(x=x, y=y, z=z, yaw=yaw, frame_id=frame_id)
            break
    else:
        interrupt = False
        print('interrupted')
        set_position(x=telemetry.x, y=telemetry.y, z=telemetry.z, yaw=float('nan'), frame_id=frame_id)
    print('ready')


def land_to(x, y, z, speed, yaw=float('nan'), frame_id='aruco_map', tolerance=0.2):
    global telemetry, interrupt
    navigate(x=x, y=y, z=z, speed=speed, yaw=yaw, frame_id=frame_id)
    print('start')
    while not interrupt:
        telem = telemetry
        # print(telem)
        if get_distance(x, y, z, telem.x, telem.y, telem.z) < tolerance:
            land()
            # set_position(x=x, y=y, z=z, yaw=yaw, frame_id=frame_id)
            break
    else:
        interrupt = False
        print('interrupted')
        set_position(x=telemetry.x, y=telemetry.y, z=telemetry.z, yaw=float('nan'), frame_id=frame_id)
    print('ready')


def fly(request, tgt=navigate_wait):
    global fly_thread, flight_now, last_pose
    if not fly_thread.is_alive():
        for n in request['pose']:
            request['pose'][n] = round(float(request['pose'][n]), 3)

        if request['pose'] != last_pose:
            last_pose = request['pose']

            if request['pose']['z'] <= 0:
                request['pose']['z'] = get_telemetry(frame_id='aruco_map').z

            print('Navigating to', request['pose'])
            fly_thread = Thread(target=tgt,
                                kwargs={'x': request['pose']['x'], 'y': request['pose']['y'],
                                        'z': request['pose']['z'], 'speed': 0.3, 'yaw': float('nan'),
                                        'frame_id': 'aruco_map'})
            fly_thread.daemon = True
            fly_thread.start()
            # navigate_wait(x=request['pose']['x'], y=request['pose']['y'], z=request['pose']['z'], speed=SPEED,
            #               yaw=float('nan'), frame_id='aruco_map')
        else:
            print('pose equals')
    else:
        print('alive')


while True:
    try:
        result = send_telemetry()
        if result['status'] == 'take_off' and not flight_now:
            take_off()
            flight_now = True
        if result['status'] == 'land' and flight_now:
            print('Landing')
            # if fly_thread.is_alive():
            #     interrupt = True
            if fly_thread.is_alive():
                interrupt = True
            fly(result, tgt=land_to)
            flight_now = False
        if result['status'] == 'fly':
            if flight_now:
                fly(result)
            else:
                take_off()
                flight_now = True
    except r.exceptions.ConnectionError:
        print('Server fallen down, sleep 2 secs.')
    except KeyboardInterrupt:
        break
