import cv2


class Ssd:
    CLASSES = {}
    CLASSES_LIST = []

    def __init__(self, pb_path="ssd_mobilenet_v2/frozen_inference_graph.pb",
                 pbtxt_path="ssd_mobilenet_v2/graph.pbtxt",
                 coco_names_path="ssd_mobilenet_v2/coco.names"):

        self.read_coco(coco_names_path)
        self.net = cv2.dnn.readNetFromTensorflow(pb_path, pbtxt_path)

    def read_coco(self, coco_names_path):

        with open(coco_names_path, "r") as f:
            Ssd.CLASSES_LIST = [i.strip() for i in f.readlines()]
            classes_index = [i for i in range(1, 81)]
            for key in Ssd.CLASSES_LIST:
                for value in classes_index:
                    Ssd.CLASSES[key] = value
                    classes_index.remove(value)
                    break
            del classes_index

    def predict(self, img, object_name='aeroplane'):
        object_list = []
        rows, cols, channels = img.shape
        self.net.setInput(cv2.dnn.blobFromImage(
            img, size=(300, 300), swapRB=True, crop=False))
        networkOutput = self.net.forward()
        for detection in networkOutput[0, 0]:
            score = float(detection[2])
            if score > 0.3:
                if Ssd.CLASSES_LIST[int(detection[1] - 1) % 80] == object_name:
                    x_min = int(detection[3] * cols)
                    y_min = int(detection[4] * rows)
                    x_max = int(detection[5] * cols)
                    y_max = int(detection[6] * rows)
                    object_list.append([x_min, y_min, x_max - x_min, y_max - y_min])

        return object_list
