# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from sensor_msgs.msg import Joy

import pygame
from pygame.locals import *
import time
import sys


class keyboardController:
    def __init__(self):
        #ノード初期設定、10fpsのタイマー付きパブリッシャー
        rospy.init_node('keyboard_con_node', anonymous=True)
        self.twist_pub = rospy.Publisher('cmd_vel', Twist, queue_size=1000)
        rospy.Timer(rospy.Duration(0.1), self.timerCallback)
	self.teleop_sub = rospy.Subscriber('joy', Joy, self.callback)

        #ボタン関係の初期化
        self.current_button = -1
        self.joystickx = 0
        self.joysticky = 0

        # ボタンのカウントと速度の係数
	self.veloc_x = 0
        self.button_cnt = 0
        self.coff_linearx = 1 # gain for velocity x
        self.coff_angularz = 1.5 # gain for steering

        #MAX値設定
#        self.linear_max = 1.6
	self.linear_max = 3.0
        self.linear_min = -0.6

        twist = Twist()
        twist.linear.x = 0.0
        twist.linear.y = 0.0
        twist.linear.z = 0.0
        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = 0.0
        self.twist_pub.publish(twist)
        
        # pygameに初期化
        pygame.init()
        pgscreen=pygame.display.set_mode((1, 1))
        pygame.display.set_caption('keyboardcon')

        #コントロール方法表示
        #print 
        #print 'キーボード操作用'
        #print 'Aで左、Dで右にステアリング、Lで前進、Mで後退、離すと停止'
        #print 

    def callback(self, data):
	if data.buttons[2] == 1:
            self.current_button = 1 # Push o button
	elif data.buttons[1] == 1:
            self.current_button = 0 # Push x button
	elif data.buttons[2] == 0:
            self.current_button = -1 # No button press

	# L3 stick
	self.joystickx = float(data.axes[0]) # L3 stick (left/right)


    def timerCallback(self, event):
        #メッセージ初期化
        twist = Twist()
        
        # イベント処理
        pygame.event.pump()
        pressed = pygame.key.get_pressed()

        #押下の有無判断用カウンタ
        #cnt = 0

        #終了処理
        if pressed[K_ESCAPE] :
            pygame.quit()
            sys.exit()

        #ステアリング検出
        #if pressed[K_a] :
        #    self.joystickx -= 1
        #    cnt += 1
        #    self.button_cnt += 1
        #    if self.joystickx < -1:
        #        self.joystickx = -1
        #if pressed[K_d] :
        #    self.joystickx += 1
        #    cnt += 1
        #    self.button_cnt += 1
        #    if self.joystickx > 1:
        #        self.joystickx = 1
        #if cnt == 0:
        #    self.joystickx = 0
        #cnt = 0

        #アクセル、バック検出
        #if pressed[K_l] :
        #    self.current_button = 1
        #    cnt += 1
        #    self.button_cnt += 1
        #if pressed[K_m] :
        #    self.current_button = 0
        #    cnt += 1
        #    self.button_cnt += 1
        #if cnt == 0:
        #    self.current_button = -1
        #cnt = 0

        # 実際の値変更
        #   未入力時の処理
        if self.current_button == -1: # slow down
            if abs(self.veloc_x) < 0.1 :
                self.veloc_x = 0
            if self.veloc_x > 0 :
                self.veloc_x -= 0.2
            elif self.veloc_x < 0 :
                self.veloc_x += 0.2
            else :
                self.veloc_x = 0
        
        #   ボタン入力時の処理
        if self.current_button==0: # Press backward button
            if self.veloc_x > self.linear_min :
                self.veloc_x -= 0.2
            else :
                self.veloc_x = self.linear_min
	    if self.veloc_x > 0:
		print 'now braking'
            else:
		print 'go backward'

        elif self.current_button==1: # Press forward button
            print 'go foward'
            if self.veloc_x < self.linear_max :
                self.veloc_x += 0.2
            else :
                self.veloc_x = self.linear_max
	else:
            print 

        # cmd_velのPublish
        twist.linear.x  = self.veloc_x * self.coff_linearx
        twist.angular.z = self.joystickx * self.coff_angularz
	print 'current_button:' + str(self.current_button)
        print 'linear x:' + str(self.veloc_x) + ', angular z:' + str(self.joystickx)
        self.twist_pub.publish(twist)


if __name__ == '__main__':
    try:
        kc = keyboardController()
        rospy.spin()
    except pygame.error:
        print 'コントローラが見つかりませんでした。'
    except rospy.ROSInterruptException: pass
