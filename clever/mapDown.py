import requests as r
import os
import consts
from time import sleep
import rospy


def map_down():
    while not rospy.is_shutdown():
        try:
            input_data = r.get(consts.SERVER_IP + '/static/map.txt')
        except r.exceptions.ConnectionError:
            sleep(5)
            continue
        if input_data.status_code == 200:
            path = consts.CLEVER_PATH + 'aruco_pose/map/map.txt'

            with open(path, 'r') as tempData:
                # TODO: make dict and check
                data = tempData.read()
                data = data.replace('\r', '').split('\n')

                idata = input_data.text
                idata = idata.replace('\r', '').split('\n')

                if data != idata:
                    print('Map is incorrect. Using map from server.')
                    with open(path, 'wb') as f:
                        f.write(input_data.content)
                    os.system("sudo systemctl restart clever")
                    print('Restart clever.service')
                    sleep(30)
                else:
                    print('Map is correct. Starting...')
            break
        else:
            sleep(5)
