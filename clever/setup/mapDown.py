import requests as r
import os

def map_down:
    inputData = r.get('http://192.168.43.128:8000/static/map.txt')
    path = '/home/pi/catkin_ws/src/clever/aruco_pose/map/map.txt'

    with open(path, 'r') as tempData: #/home/pi/catkin_ws/src/clever/aruco_pose/map/map.txt

        print('Map loaded in drone now')
        print(tempData.read())

        if (inputData.content != tempData.read()):

            print('Map update required')
            print('Update? [Y/n]')

            ans = raw_input()

            if ((ans == "Y") or (ans == "y")):

                with open(path, 'w') as f:
                	f.write(inputData.content)
                os.system("sudo systemctl restart clever") 
            elif ((ans == "N") or (ans == "n")):

                pass
            else:

                pass
