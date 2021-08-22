from uav import MyUAV
from interface import HUD
import threading
from Yolov4Tiny import Model
from Camera import Recorder

import numpy as np
import cv2
import time
import datetime


def func(frame, o_params): # o_paramsa (x, y, w, h) şeklinde tuple girin.
    # mor çerçeve için çözünürlük gerekiyor. Değiştirirsiniz başka çözünürlükler için.
    t = datetime.datetime.now()
    clock = f"Zaman : {t.hour}-{t.minute}-{t.second}-{int(t.microsecond/1000)}"
    cam_width = frame.shape[1]
    cam_height = frame.shape[0]
    center_detected_object = [o_params[0]+int(o_params[2]/2),o_params[1]+int(o_params[3]/2)]
    center_frame = [int(frame.shape[1]/2),int(frame.shape[0]/2)]

    mor_alan_params = (int(cam_width / 4), int(cam_height / 10), int(cam_width / 2), int(cam_height * 4 / 5))
    renk = (255, 0, 150)
    kalinlik = 2
    cv2.rectangle(frame, (mor_alan_params[0], mor_alan_params[1]), (mor_alan_params[0] + mor_alan_params[2], mor_alan_params[1] + mor_alan_params[3]), renk, kalinlik)
    image = cv2.line(frame, center_frame, center_detected_object, [255,255,255], kalinlik)
    cv2.putText(frame, clock, (cam_width-190,20), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, [0,0,0], 1, cv2.LINE_AA)
    cv2.putText(frame, "Kilitlenme : ", (cam_width-190,40), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, [0,0,0], 1, cv2.LINE_AA)

    def xy_check():
        if mor_alan_params[0] <= o_params[0] <= (mor_alan_params[0] + mor_alan_params[2]):
            if mor_alan_params[1] <= o_params[1] <= (mor_alan_params[1] + mor_alan_params[3]):
                return True
        return False

    def in_area_check():
        if (o_params[0] + o_params[2]) > (mor_alan_params[0] + mor_alan_params[2]):
            if (o_params[1] + o_params[3]) > (mor_alan_params[1] + mor_alan_params[3]):
                return True
        return False

    if xy_check() or in_area_check():
        cv2.putText(frame, "1", (cam_width-100,40), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, [0,0,0], 1, cv2.LINE_AA)
    else:
        cv2.putText(frame, "0", (cam_width-100,40), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, [0,0,0], 1, cv2.LINE_AA)

    
def main(hud,myuav):
    cap = cv2.VideoCapture("./test3.mp4")
    model = Model("./model/yolov4-tiny-custom_best.weights","./model/yolov4-tiny-custom.cfg","./model/obj.names")
    model.USE_GPU = True
    model.load_yolo()
    rec = Recorder()
    begin_time = 0
    
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        print(frame.shape)
        _ = time.time()
        # Our operations on the frame come here
        boxes, confidences, classIDs, idxs = model.make_prediction(frame)
        frame = model.draw_bounding_boxes(frame,boxes,confidences,classIDs,idxs)
        #if len(boxes) != 0:
        #    func(frame, boxes[0])
        hud.update_HUD(myuav,frame,boxes)
        
        if myuav.is_lockable(): # 4 Saniyeden fazla mor cercevenin icinde kaldiysa kilitlenmistir.
            if time.time()-begin_time >= 4:
                myuav.lock_flag = True
                begin_time = time.time()
        else:
            myuav.lock_flag = False
            begin_time = time.time()
        
        print("FLAG = ",myuav.lock_flag)

        # Display the resulting frame
        cv2.imshow('frame',frame)
        rec.record(frame)
        print(f"FPS : {1/(time.time() - _)}")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
    rec.release_recorder()



if __name__ == "__main__":
    hud = HUD(854,480)
    myuav = MyUAV()
    main(hud,myuav)
    








