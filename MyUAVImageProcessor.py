from Tools.MyTime import MyTime
from mobilenet2_model import Ssd as AIModel
from Tools import ScreenSettings as Settings
import cv2
import time
import math

process_result_package = {
    "available_object": False,
    "locking_inprogress": False,
    "locked_successfully": False,
    "target_proper_to_track": False,
    "collision_possible": False,
    "target": None,
    "lock_time": None,
    "target_movement_x_msg": "",
    "target_movement_x_value": 0,
    "target_movement_y_msg": "",
    "target_movement_y_value": 0,
    "target_movement_z_msg": "",
    "target_movement_z_value": 0,
}


def draw_box(img, box, color, thick):
    x = int(box[0])
    y = int(box[1])
    w = int(box[2])
    h = int(box[3])
    cv2.rectangle(img, (x, y), (x + w, y + h), color, thick)


# Iha bu mesajları kullanarak bilgisayarla iletişim kuracak.
# Bu mesajların olduğu yerlerde büyük ihtimalle bilgisayara gönderilmesi gereken
# veya işlenmesi gereken önemli veriler de olacak.

def NoAvailableObject(): return "There is No Available Object."


def NotInTheArea(): return "Target is not in The Locking Area."


def LockingMayBegin(): return "Locking is able to begin."


def LockedSuccessfully(): return "Locked Successfully!"


def LockingUnsuccessful(): return "Unsuccessful Locking"


def ScreenTurnedOf(): return "Screen Turned Off"


class Screen:
    def __init__(self):
        self.screen = cv2.VideoCapture(Settings.v_path)
        self.frame = None
        self.timer = None
        self.screen_turn_on = True

    # Kamera çalışıyorsa True, çalışmıyorsa False döner.
    def update_screen(self):
        screen_available, img = self.screen.read()
        if screen_available:
            self.timer = time.time()
            self.frame = cv2.resize(img, (Settings.cam_width, Settings.cam_height), interpolation=cv2.INTER_AREA)
        return screen_available

    # Frame gösterilir. 'esc' ye basılırsa kamera kapatılır.
    def display_screen(self, display_speed=1):
        draw_box(self.frame, Settings.target_hit_area, (255, 0, 150), 2)
        print("FPS: ", 1 / (time.time() - self.timer))
        cv2.imshow("Camera", self.frame)
        if cv2.waitKey(display_speed) & 0xFF == 27:
            self.turnoff_screen()
            return True
        return False

    def turnoff_screen(self):
        cv2.destroyAllWindows()
        self.screen.release()
        self.screen_turn_on = False


class ObjectDetector:
    def __init__(self):
        self.model = AIModel()

    # Frame'deki objeler bulunur ve bunlar mor çerçeve içinde ve değil şeklinde ayrılır.
    # Obje türüne göre en yakın obje döner. Mor alanda olan ve olmayan olarak 2 obje türü var.
    # Mor çerçevede obje varsa direkt o dönülür, yoksa mor çerçeve dışındaki alanda obje varsa o dönülür.
    # İkisinde de obje yoksa None döner.
    def detect_object(self, frame):
        objects = self.model.predict(frame, 'aeroplane')
        if len(objects) == 0:
            return None, False
        return find_significant_obj(objects)


# Kameradaki kilitlenmeye en uygun objeyi döner.
def find_significant_obj(objects):
    n_objects = []  # mor alan dışındaki objeler
    h_objects = []  # mor alandaki objeler
    target_found = False

    for obj in objects:
        if obj[2] <= Settings.min_target_width or obj[3] <= Settings.min_target_height:
            continue
        if obj[0] < Settings.hit_area_points[0] or obj[1] < Settings.hit_area_points[1]:
            n_objects.append(obj)
            continue
        if obj[0] + obj[2] > Settings.hit_area_points[2] or obj[1] + obj[3] > Settings.hit_area_points[3]:
            n_objects.append(obj)
            continue
        h_objects.append(obj)

    if len(h_objects) > 0:
        target_found = True
        return find_closest(h_objects), target_found
    if len(n_objects) > 0:
        return find_closest(n_objects), target_found
    return None, target_found


def find_closest(objects):
    biggest_area = -1
    closest_obj = None
    for obj in objects:
        if obj[2] * obj[3] > biggest_area:
            biggest_area = obj[2] * obj[3]
            closest_obj = obj
    return closest_obj


class ObjectDetectionProcessor:
    def __init__(self):
        self.object_detector = ObjectDetector()

    def process(self, frame):

        target, target_is_in_area = self.object_detector.detect_object(frame)
        object_is_available = False
        locking_is_available = False

        if target is None:
            process_result_package["msg"] = NoAvailableObject()
            return object_is_available, locking_is_available, target

        object_is_available = True

        if not target_is_in_area:
            process_result_package["msg"] = NotInTheArea()
            return object_is_available, locking_is_available, target

        locking_is_available = True
        process_result_package["msg"] = LockingMayBegin()
        return object_is_available, locking_is_available, target


# Kamera üzerindeki verilere göre kilitlenme işlemini yapan yapı.
class Locker:
    def __init__(self):
        self.timer = None
        self.is_locked = False  # "Kilitlenme başarılı mı?" verisini tutar.
        self.locking_is_inprogress = False  # "Şu anda kilitlenme gerçekleşiyor mu?" verisini tutar.

    def begin_locking(self):
        self.timer = time.time()
        self.is_locked = False
        self.locking_is_inprogress = True

    # 4 saniye boyunca kilitleniyorsa kilitlenme tamamlanacak.
    def locking(self):
        if time.time() - self.timer >= 4:
            self.is_locked = True

    def end_locking(self):
        self.is_locked = False
        self.locking_is_inprogress = False


class LockingProcessor:
    def __init__(self):
        self.locker = Locker()
        self.begin_time = MyTime()
        self.end_time = MyTime()

    def process(self):

        if self.locker.locking_is_inprogress:
            self.locker.locking()

            if self.locker.is_locked:
                self.end_time.update_without_package()
                self.locker.end_locking()
                process_result_package["msg"] = LockedSuccessfully()
                return True, {"begin": self.begin_time, "end": self.end_time}

            return self.locker.is_locked, None

        self.begin_time.update_without_package()
        self.locker.begin_locking()
        return self.locker.is_locked, None


class TargetWatchingProcessor:
    def __init__(self):
        self.object_detection_processor = ObjectDetectionProcessor()
        self.locking_processor = LockingProcessor()
        self.locking_is_completed = False

    def process(self, frame):

        object_is_available, locking_is_available, target = self.object_detection_processor.process(frame)

        process_result_package["available_object"] = object_is_available
        process_result_package["locking_inprogress"] = locking_is_available

        if locking_is_available:
            draw_box(frame, target, (0, 0, 255), 2)
            self.locking_is_completed, lock_times = self.locking_processor.process()
            process_result_package["locked_successfully"] = self.locking_is_completed
            process_result_package["lock_time"] = lock_times
            return target

        # Eğer kilitlenme esnasında kilitlenmeye mani olan bir şey varsa bu kısım çalışır ve kilitlenmeyi sıfırlar.
        if self.locking_processor.locker.locking_is_inprogress:
            process_result_package["msg"] = LockingUnsuccessful()
            self.locking_processor.locker.end_locking()
            process_result_package["locking_inprogress"] = self.locking_processor.locker.locking_is_inprogress

        if object_is_available:
            draw_box(frame, target, (255, 255, 0), 2)
        return target


def isTargetProperToTrack(previous_target, current_target, max_location_change=50, is_target_locked_before=False):
    # Eğer kameradaki hedef ihanın dönmesi için çok hızlıysa onu takip etmemesi için bir fonksiyon.
    # 'max_location_change' in denenip en uygun değerin verilmesi gerekiyor.
    # Ayrıca eğer hedef daha önceden kilitlenildiyse de False döner. Böylece boşa takip edilmesine yardımcı olur.
    # Ama yine de bir şekilde kilitlenirse kilitlenme verisini göndermeden 'process_result_package' dan
    # takip için uygun olup olmadığı kontrol edilebilir.

    if previous_target is None:
        return False

    location_change = math.sqrt(
        (current_target[0] - previous_target[0]) ** 2 + (current_target[1] - previous_target[1]) ** 2)

    if location_change <= max_location_change and not is_target_locked_before:
        return True
    return False


def targetMovingAway(previous_target, current_target, dangerous_area_difference=300):
    # Hedefin frameler arasındaki alan değişimiyle uzaklaşıyor mu yakınlaşıyor mu ne kadar farkla bunu yapıyor onu
    # hesaplayan fonksiyon. 'process_result_package["target_movement_x_value"]' ile x ekseninde ne kadar hız değişmesi
    # gerektiğini hesaplayabiliriz. 'process_result_package["target_movement_x_msg"]' durum mesajı veriyor. Dursun belki
    # bir işe yarar. Eğer değişim çok fazlaysa çarpışma olabilir o yüzden de 'process_result_package["collision_possible"]'
    # var. Bu da hareket fonksiyonlarında kaçınmak için bi fonksiyon yazılmasında kullanılabilir.

    if not previous_target:
        return

    prev_target_area = previous_target[2] * previous_target[3]
    curr_target_area = current_target[2] * current_target[3]
    area_difference = curr_target_area - prev_target_area

    process_result_package["target_movement_x_value"] = area_difference

    if area_difference == 0:
        process_result_package["target_movement_x_msg"] = "no_difference"
    elif area_difference <= 0:
        process_result_package["target_movement_x_msg"] = "moving_away"
    else:
        process_result_package["target_movement_x_msg"] = "closing"

    if area_difference >= dangerous_area_difference:
        process_result_package["collision_possible"] = True

    process_result_package["collision_possible"] = False


def targetRelativePosition(target):
    # Hedefin ekrandaki konumuna göre hareket komutlarındaki y ve z velocitylerinin ne kadar hızlı ve hangi yönde
    # olacaklarını hesaplayabiliriz.

    target_center_x = target[0] + target[2] / 2
    target_center_y = target[1] + target[3] / 2

    target_movement_y_value = Settings.center_point[0] - target_center_x
    target_movement_z_value = Settings.center_point[1] - target_center_y

    if target_center_x is Settings.center_point[0]:
        process_result_package["target_movement_y_msg"] = "0"
    elif target_center_x >= Settings.center_point[0]:
        process_result_package["target_movement_y_msg"] = "+y"
    else:
        process_result_package["target_movement_y_msg"] = "-y"

    process_result_package["target_movement_y_value"] = target_movement_y_value

    if target_center_y is Settings.center_point[1]:
        process_result_package["target_movement_z_msg"] = "0"
    elif target_center_y >= Settings.center_point[1]:
        process_result_package["target_movement_z_msg"] = "+z"
    else:
        process_result_package["target_movement_z_msg"] = "-z"

    process_result_package["target_movement_z_value"] = target_movement_z_value


# serverdan gelen verilere göre kamera ile takip, hareket gibi işlemleri yapan yapı
class MyUAVImageProcessor:
    def __init__(self):
        self.screen = Screen()
        self.target_watching_processor = TargetWatchingProcessor()
        self.begin_process = True  # bilgisayardan gelecek olan görüntü işlemeyi başlat booleanı
        self.previous_target = None
        self.current_target = None

    def process(self):
        # Hazırlanan 'process_result_package' burada bilgisayara gönderilmeli. Aynı zamanda gelen bir target varsa,
        # ne olur ne olmaz kontrol etmekte fayda var, görüntüdeki konumunun bizim ihaya olan uzaklıklarını hesaplamayıp
        # bu uzaklıklarla hareket kodlarındaki takip fonksiyonuna ne yöne gitmesi gerektiğini söylememiz gerekiyor.
        # Bu kısımda sadece target'ı [x, y, w, h] olarak dönüyoruz. Hesaplamaları bilgisayarda ya da hareket kodlarında
        # yaparız.

        target = self.target_watching_processor.process(self.screen.frame)

        if target:
            self.current_target = target
            process_result_package["target_proper_to_track"] = isTargetProperToTrack(self.previous_target,
                                                                                     self.current_target,
                                                                                     max_location_change=50)  # Değişmeli
            targetMovingAway(self.previous_target,
                             self.current_target,
                             dangerous_area_difference=300)  # Değişmeli

            targetRelativePosition(target)
            self.previous_target = target
            process_result_package["target"] = target

    def display_screen(self):
        while self.screen.update_screen():
            if self.begin_process:
                self.process()
            print(process_result_package)
            self.screen.display_screen()


image_processor = MyUAVImageProcessor()
image_processor.display_screen()
# eğer kod eklemek istersen 'image_processor.display_screen' fonksiyonuna ekle. While'dan dolayı ulaşamazsın.
