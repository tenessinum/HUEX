import requests as r
q = r.get('http://192.168.1.206:8000/static/map.txt')
print(q.text)
with open('/home/pi/catkin_ws/src/clever/aruco_pose/map/map.txt', 'wb') as f:
    f.write(q.content)