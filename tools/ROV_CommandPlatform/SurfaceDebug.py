from Joystick import *
import threading
import cv2
import time
import socket
import numpy as np
import sys
import logging
import struct

REMOTE_IP = '192.168.137.100'
HOST_IP = '192.168.137.254'
REMOTE_PORT = 8010
HOST_PORT = 9999

# UDP
# udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# udp_socket.bind(("", HOST_PORT))


recv_data = '0:0:0:0:0'


def command_send(s, cmd):
    send_data = struct.pack("%dB" % (len(cmd)), *cmd)
    s.sendto(send_data, (HOST_IP, HOST_PORT))
    time.sleep(0.02)


def message_recv(s):
    recvData = s.recv(1024).decode()
    # time.sleep(0.05)
    return recvData


def send_msg(udp_socket, dest_ip, dest_port, f_b, l_r, u_d1, u_d2, servo_angle, servo_claw):
    """发送消息"""
    # 获取要发送的内容
    x = str(f_b)
    y = str(l_r)
    z1 = str(u_d1)
    z2 = str(u_d2)
    angle = str(servo_angle)
    claw = str(servo_claw)
    x = x.rjust(3,'0') #0补齐四位
    y = y.rjust(3,'0')
    z1 = z1.rjust(3,'0')
    z2 = z2.rjust(3,'0')
    angle = angle.rjust(3,'0')
    claw = claw.rjust(3,'0')
    send_data = x + ':' + y + ':' + z1 + ':' + z2 + ':' + angle + ':' + claw
    udp_socket.sendto(send_data.encode(), (dest_ip, dest_port))
    send_data = ''
    time.sleep(0.02)


def recv_msg(s,):
    """接收数据"""
    recvData = s.recv(1024).decode()
    time.sleep(0.05)
    return recvData
    

class Control:
    def __init__(self):
        self.url = 'http://' + REMOTE_IP + ':' + REMOTE_PORT
        # TCP
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((HOST_IP, HOST_PORT))
    #     self.servo_angle = 100
    #     self.servo_claw = 90
    #     logging.basicConfig(level=logging.DEBUG,
    #                 format='%(asctime)s|%(levelname)s|%(message)s',
    #                 datefmt='%d-%b-%H:%M:%S',
    #                 filename='data.log',
    #                 filemode='w')


    # def Open(self):
    #     """接收视频流"""
    #     self.cap = cv2.VideoCapture(self.url)
    #     self.cap.set(3, 1280)
    #     self.cap.set(4, 720)
    #     self.frameRate = self.cap.get(cv2.CAP_PROP_FPS)
    #     th = threading.Thread(target=self.Display)
    #     th.setDaemon(True)
    #     th.start()

    # def Display(self):
    #     """显示界面"""
    #     global recv_data
    #     fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    #     sz = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
    #     int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    #     fps = 10
    #     video_out = cv2.VideoWriter()
    #     video_out.open('./output.mp4',fourcc,fps,sz,True)
    #     cv2.namedWindow('image',cv2.WINDOW_FREERATIO)
    #     cv2.resizeWindow("image", 1280, 720)


    #     while self.cap.isOpened():
    #         success, frame = self.cap.read()
            
    #         if frame is None:
    #             tmp_img = np.zeros([480,640,3],np.uint8)
    #             cv2.putText(tmp_img,"NO VIDEO", (200, 300),cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 3)
    #             self.cap = cv2.VideoCapture(self.url)
    #             if self.cap.isOpened():
    #                 success, frame = self.cap.read()
    #             else:
    #                 frame = tmp_img
    #         data= recv_data.split(":")
    #         #logging.info("sensor_data: roll:{} pitch:{} yaw:{} depth:{} temprature:{}".format(str(data[0]),str(data[1]),str(data[2]),str(data[3]),str(data[4])))
    #         if(len(data) > 1):
    #             cv2.putText(frame,"roll: "+str(data[0]),(10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
    #             cv2.putText(frame,"pitch: "+str(data[1]),(10, 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
    #             cv2.putText(frame,"yaw: "+str(data[2]),(10, 100), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
    #             #1100
    #             cv2.putText(frame,"depth: "+str(data[3]),(600, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
    #             cv2.putText(frame,"temprature: "+str(data[4]),(600, 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

    #         frame = cv2.resize(frame,(1280,720))
    #         cv2.imshow('image', frame)
    #         cv2.waitKey(33)
    #         video_out.write(frame)
    #         if cv2.waitKey(1) & 0xFF == ord('q'):
    #             video_out.release()
    #             logging.info("stop recorder")
    #             print("结束录制")
    #             exit()
    #         if cv2.waitKey(1) & 0xFF == ord('w'):
    #             self.cap = cv2.VideoCapture(self.url)
    #             logging.error("video offline")
    #     self.cap.release()

    def send_controldata(self):
        """发指令"""
        global recv_data
        value = get_value()
        cnt = 0
        while True:
            temp_value = next(value)
            cnt = cnt + 1
            
            # 机械臂舵机角度
            # if(self.servo_claw > 70 and self.servo_claw < 176):
            #     self.servo_claw += int(temp_value[15][0])*2
            # elif(self.servo_claw == 70):
            #     if(int(temp_value[15][0])<0):
            #         self.servo_claw = 70
            #     else:
            #         self.servo_claw += int(temp_value[15][0])*2
            # elif(self.servo_claw == 176):
            #     if(int(temp_value[15][0])>0):
            #         self.servo_claw = 176
            #     else:
            #         self.servo_claw += int(temp_value[15][0])*2
            # else:
            #     pass

            # if(self.servo_claw > 69 and self.servo_claw < 177):
            #     if(temp_value[2]<-0.4):
            #         self.servo_claw += 3
            #     elif(temp_value[2]>0.4):
            #         self.servo_claw -= 3
            #     else:
            #         pass
            # elif(self.servo_claw == 69):
            #     if(temp_value[2]>0.4):
            #         self.servo_claw = 69
            #     elif(temp_value[2]<-0.4):
            #         self.servo_claw += 3
            #     else:
            #         pass
            # elif(self.servo_claw == 177):
            #     if(temp_value[2]<-0.4):
            #         self.servo_claw = 177
            #     elif(temp_value[2]>0.4):
            #         self.servo_claw -= 3
            #     else:
            #         pass
            # else:
            #     pass
            #机械臂舵机角度
            # if(self.servo_angle > 40 and self.servo_angle < 180):
            #     self.servo_angle -= int(temp_value[9])
            #     self.servo_angle += int(temp_value[10])
            # elif(self.servo_angle == 40):
            #     self.servo_angle += int(temp_value[10])
            # else:
            #     self.servo_angle -= int(temp_value[9])
            
            
            # 推进器PWM
            L = 0
            R = 0
            x = int(num_map(temp_value[0],-1,1,500,2500))
            y = int(num_map(temp_value[1],1,-1,500,2500))
            z = int(num_map(temp_value[3],1,-1,500,2500))
            if x>=1500 and y>=1500 and x>=y :   #1
                L = x
                R = y-x+1500
            elif x>=1500 and y>1500 and x<y :   #2
                L = y
                R = y-x+1500
            elif x<1500 and y>1500 and x+y>=3000:   #3
                L = x+y-1500
                R = y
            elif x<1500 and y>1500 and x+y<3000:   #4
                L = x+y-1500
                R = 3000-x
            elif x<=1500 and y<=1500 and x<y :   #5
                L = x
                R = y-x+1500
            elif x<=1500 and y<1500 and x>=y :   #6
                L = y
                R = y-x+1500
            elif x>1500 and y<1500 and x+y<3000:   #7
                L = x+y-1500
                R = y
            elif x>1500 and y<1500 and x+y>=3000:   #8
                L = x+y-1500
                R = 3000-x
            else:
                L = 1500
                R = 1500
            
            L1 = int(num_map(L,500,2500,76,110))
            R1 = int(num_map(R,500,2500,110,76))
            z1 = int(num_map(z,500,2500,76,110))
            z2 = int(num_map(z,500,2500,110,76))
            

            L1 = int(num_map(L,500,2500,108,84))
            R1 = int(num_map(R,500,2500,81,105))
            z1 = int(num_map(z,500,2500,105,81))
            z2 = int(num_map(z,500,2500,105,81))


            # send_msg(udp_socket, HOST, PORT, L1 , R1, z1, z2, self.servo_angle,self.servo_claw)
            print("send_data: L:{} R:{} z1:{} z2:{} Angle:{} claw:{}".format(L1,R1,z1,z2,self.servo_angle,self.servo_claw))
            recv_data = recv_msg(udp_socket)
            print(recv_data)
            data = recv_data.split(":")
            # if(countime == 30):
            #     logging.info("send_data: L:{} R:{} z1:{} z2:{} Angle:{} claw:{}".format(L1,R1,z1,z2,self.servo_angle,self.servo_claw))
            #     logging.info("sensor_data: roll:{} pitch:{} yaw:{} depth:{} temprature:{}".format(str(data[0]),str(data[1]),str(data[2]),str(data[3]),str(data[4])))
            #     countime = 0
            



if __name__ == "__main__":
    control = Control()
    # control.Open()
    th = threading.Thread(target=control.send_controldata)
    th.start()
