#!/usr/bin/env python
# license removed for brevity
import rospy
from led.msg import LedModeColor
from time import clock


def talker():
    pub = rospy.Publisher('ledtopic', LedModeColor, queue_size=10)
    rospy.init_node('ledpub', anonymous=True)
    message = LedModeColor()
    message.color.r = 0
    message.color.g = 0
    message.color.b = 0
    message.mode = 'off'
    pub.publish(message)



talker()

