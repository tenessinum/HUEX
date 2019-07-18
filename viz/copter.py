import rospy
from clever import srv
import math
import consts
import json
import requests as r
from flask import Flask, Response, render_template, redirect


PARAMS_NAME = ('x', 'y', 'z', 'yaw', 'mode', 'cell_voltage','pitch','roll')
get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry, persistent=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lorem ipsum'

@app.route("/data")
def send_telemetry(frame_id='aruco_map'):
    global telemetry, params
    telemetry = get_telemetry(frame_id=frame_id)
    params = {}
    for p in PARAMS_NAME:
        par = getattr(telemetry, p)
        if type(par) == float:
            par = round(par, 3)
        params[p] = par
    return json.dumps(params)

app.run(host="192.168.1.103", port=8081)

