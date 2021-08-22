from  communication import Transmitter_UDP
import cv2

t = Transmitter_UDP(RECEIVER_IP="192.168.1.3")
cap = cv2.VideoCapture(0)


while True:

    ret, frame = cap.read()
    t.send_stream(frame,ret)
