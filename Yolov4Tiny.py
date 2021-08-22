import numpy as np
import cv2
import os
import time


class Model:
    
    def __init__(self,WEIGHTS_PATH,CONFIG_PATH,LABELS_PATH):
        self.WEIGHTS_PATH = WEIGHTS_PATH
        self.CONFIG_PATH = CONFIG_PATH
        self.LABELS_PATH = LABELS_PATH
        
        self.LABELS = []
        self.USE_GPU = True
        
        
        
        try:
            with open(self.LABELS_PATH, "r") as f:
                for line in f.readlines():
                    self.LABELS.append(line.strip("\n"))  # her bir class adından '\n' i sildik
            print("LABELS :",self.LABELS)
            self.__colors = np.random.randint(0, 255, size=(len(self.LABELS), 3), dtype='uint8')
        except:
            print("[LOAD LABELS ERROR]")
            exit(1)
    
    def load_yolo(self):
        
        self.net = cv2.dnn.readNet(self.WEIGHTS_PATH, self.CONFIG_PATH)  # load YOLO algorithm.
        
        if self.USE_GPU:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            print('Using GPU')
        else:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            print('Using CPU')
        
        self.layer_names = self.net.getLayerNames()
        
        print(f"Layers Names [{len(self.layer_names)}] :", self.layer_names)  # CNN modelinin katmanları

        self.output_layers = []  # Output layerlarin isimleri
        for i in range(len(self.layer_names)):
            if i + 1 in self.net.getUnconnectedOutLayers():  # Output layerlarin indisini doner
                self.output_layers.append(self.layer_names[i])
                
        print("Output Layers : ", self.output_layers)
        
        print("[WAIT] Model is loading...")
    
    def __extract_boxes_confidences_classids(self,outputs, confidence, width, height):
        boxes = []
        confidences = []
        classIDs = []

        for output in outputs:
            for detection in output:            
                # Extract the scores, classid, and the confidence of the prediction
                scores = detection[5:]
                classID = np.argmax(scores)
                conf = scores[classID]
                
                # Consider only the predictions that are above the confidence threshold
                if conf > confidence:
                    # Scale the bounding box back to the size of the image
                    box = detection[0:4] * np.array([width, height, width, height])
                    centerX, centerY, w, h = box.astype('int')

                    # Use the center coordinates, width and height to get the coordinates of the top left corner
                    x = int(centerX - (w / 2))
                    y = int(centerY - (h / 2))

                    boxes.append([x, y, int(w), int(h)])
                    confidences.append(float(conf))
                    classIDs.append(classID)

        return boxes, confidences, classIDs
        
    def make_prediction(self, image, confidence=0.5, threshold=0.3):
        height, width = image.shape[:2]
        
        # Create a blob and pass it through the model
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)

        # Extract bounding boxes, confidences and classIDs
        boxes, confidences, classIDs = self.__extract_boxes_confidences_classids(outputs, confidence, width, height)

        # Apply Non-Max Suppression
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, confidence, threshold)

        return boxes, confidences, classIDs, idxs
    
    def draw_bounding_boxes(self,image, boxes, confidences, classIDs, idxs):
        if len(idxs) > 0:
            for i in idxs.flatten():
                # extract bounding box coordinates
                x, y = boxes[i][0], boxes[i][1]
                w, h = boxes[i][2], boxes[i][3]

                # draw the bounding box and label on the image
                color = (0,0,255)#[int(c) for c in self.__colors[classIDs[i]]]
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                text = "{}: {:.4f}".format(self.LABELS[classIDs[i]], confidences[i])
                cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return image
    
    

if __name__ == "__main__":
    img = cv2.imread("./test_images/image7.jpg")
    model = Model("./model/yolov4-tiny-custom_best.weights","./model/yolov4-tiny-custom.cfg","./model/obj.names")
    model.load_yolo()
    boxes, confidences, classIDs, idxs = model.make_prediction(img)
    print(boxes,confidences,classIDs)
    img = model.draw_bounding_boxes(img,boxes,confidences,classIDs,idxs)
    
    cv2.imshow("window",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows() 
