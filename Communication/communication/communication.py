import requests
import json
import ast
import time
import socket
import tqdm
import os
import math
import pickle
import sys
import cv2
import numpy as np


#########GLOBAL##########
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024
MAX_LENGTH_R = 65540
MAX_LENGTH_T = 65000
#########GLOBAL##########


class Server:
    """
    Savaşan İHA yarismasi icin sunucuyla haberlesmeyi saglicak olan sinif.
    Yarisma sunucusuna veri gonderimi ve alimi yapilabilir.
    """
    def __init__(self,url):
        self.url = url
    def print_status(self,code):
        if code == 200:
            print("Istek Basarili ! <200>")
        elif code == 204:
            print("Gonderilen paketin Formati Yanlıs ! <204>")
        elif code == 400:
            print("Istek hatali veya gecersiz ! <400>")
        elif code == 401:
            print("Kimliksiz erisim denemesi ! <401>") # Oturum ac
        elif code == 403:
            print("Yetkisiz erisim denemesi ! <403>")
        elif code == 404:
            print("Gecersiz URL ! <404>")
        elif code == 500:
            print("Sunucu ici hata ! <500>")
    def log_in(self):
        log_in_url = self.url + "api/giris"
        with open('log_in.json') as f:
            log_in_params = json.load(f)

        r = requests.post(log_in_url,data=json.dumps(log_in_params))
        r = r.json()['message']
        print(r)
    def get_server_time(self):
        """
        Burada gerekli modifikasyonların daha sonra yapilmasi gerekmektedir.
        Cunku 'GET /api/sunucusaati' sorgusu server tarafından verilecek bir json formatıdır.
        Gelistirme asamasında API elde edilemediginden server_time bir dict degisken olarak
        deneme amaclı kullanılmıstır.
        :return:
        """
        server_time_url = self.url + "api/sunucusaati"
        r = requests.get(server_time_url)
        self.print_status(r.status_code)
        server_time = r.text # Yarisma esnasinda bu sekilde kullanılmali. ret <str>
        # server_time =  ast.literal_eval("{ 'saat': 6, 'dakika': 9,'saniye': 2,'milisaniye': 61}")
        # Test amacli bu sekilde kullanildi. Ornek bir server_time verisi.

        return server_time # Kendi bilgisayarini bu zamanla kalibre et

    def post_telemetry_data(self):
        """
        Telemetri paketinde bulunması gereken veriler ve açıklamaları telemetri paketi verileri başlığında açıklanmıştır.
        Örnek TelemetriVerisi başlığında örneği belirtilen JSON verisi api/telemetri_gonder adresine post edilmelidir.
        Bu postun cevabı olarak takımlar sunucu saati ile birlikte diğer yarışmacıların konum bilgilerini
        alabilecekler. Bu konum bilgilerinin içinde konum bilgisinin sunucu saati ile arasındaki zaman
        farkı da milisaniye türünden verilecektir.

        Hava aracının bilgilerini anlık olarak sunucuya göndermek
        ve diğer takımların bilgilerini almak için kullanılır.
        :return:
        """
        telem_data_url = self.url + "api/telemetri_gonder"
        with open('telemetry_data_sample.json') as f:
            telem_data = json.load(f)

        r = requests.post(telem_data_url,data=json.dumps(telem_data))
        self.print_status(r.status_code)
        self.response = r.text # Bu degisken POST sorgusundan donen cevabı icerir. Yarismada bu satir kullanilcaktir. ret <str>

        # With open kismi yarismada silinecek. Kodun test edilmesi icin ornek-
        # telemetry_data_response_sample.json dosyasi kullanılıyor simdilik.
        # with open('telemetry_data_response_sample.json') as f:
        #     self.response = json.load(f)  # Test amacli bu sekilde kullanildi. Ornek bir response verisi.



    @property
    def other_teams_info(self):
        return self.response

    def post_locking_info(self):
        locking_info_url = self.url + "api/kilitlenme_bilgisi"
        with open('locking_info_sample.json') as f:
            locking_info = json.load(f)
        r = requests.post(locking_info_url,data=json.dumps(locking_info))
        self.print_status(r.status_code)

    def log_out(self):
        log_out_url = self.url + "api/cikis"
        r = requests.get(log_out_url)
        r = r.json()['message']
        print(r)

class Receiver_TCP:
    '''
        Transmitter_TCP ile baglanti kuracak olan sinif.Transmitter'dan dosya alirken bu sinifi kullanın.
    '''

    def __init__(self,PORT=5001):
        '''

        :param PORT: Hangi porttan baglanmak istediginizi girin.Varsayilan port 5001'dir.
        '''
        self.HOST = "0.0.0.0"
        self.PORT = PORT
        self.ADDR = (self.HOST, self.PORT)

        try:
            # TCP socket
            self.s = socket.socket()
            self.s.bind(self.ADDR)
        except socket.error:
            print("[SOCKET CREATION ERROR]")

    def wait_connection(self):
        '''
            Transmitter'in baglanmasini bekle.
        :return:
        '''
        self.s.listen(5)
        print(f"[*] Listening {self.HOST}:{self.PORT}")

        # accept connection if there is any
        self.client_socket, self.address = self.s.accept()
        # if below code is executed, that means the sender is connected
        print(f"[+] {self.address} is connected.")

    def receive_file(self, keep_open=False):
        '''
            Dosya alimi icin kullanilcak metod.
        :param keep_open: Dosya gonderiminden sonra port kapatilsin mi ? TRUE/FALSE
        :return:
        '''
        received = self.client_socket.recv(BUFFER_SIZE).decode("utf-8")
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)

        progress = tqdm.tqdm(range(int(filesize)), f"Receiving {filename}", unit="B", unit_scale=True,
                             unit_divisor=1024)

        f = open("./files/" + filename, "wb")
        received_size = 0
        while (received_size <= int(filesize)):
            received = self.client_socket.recv(BUFFER_SIZE)
            f.write(received)
            progress.update(len(received))
            received_size += BUFFER_SIZE

        f.close()

        if not keep_open:
            # close the client socket
            self.client_socket.close()
            # close the server socket
            self.s.close()

    def receive_message(self, keep_open=False):
        '''
            Mesaj alimi icin kullanilcak metod
        :param keep_open: Dosya gonderiminden sonra port kapatilsin mi ? TRUE/FALSE
        :return: Gelen mesaj.
        '''
        msg = self.client_socket.recv(BUFFER_SIZE).decode("utf-8")
        if not keep_open:
            self.client_socket.close()
            self.s.close()
        return msg

    def close_all(self):
        '''
            Acik olan tum portlari kapar.
        :return:
        '''
        # close the client socket
        self.client_socket.close()
        # close the server socket
        self.s.close()


class Transmitter_TCP:
    '''
        Receiver_TCP ile baglanti kuracak olan sinif.Receiver'a dosya gonderirken bu sinifi kullanin.
    '''
    def __init__(self, RECEIVER_IP="192.168.1.5",PORT=5001):
        '''
        :param RECEIVER_IP: Receiver'ın IP adresini girin.
        :param PORT: Hangi porttan baglanmak istediginizi girin.Varsayilan port 5001'dir.
        '''
        self.RECEIVER_IP = RECEIVER_IP
        self.PORT = PORT
        self.ADDR = (self.RECEIVER_IP, self.PORT)

        try:
            self.s = socket.socket()  # default(AFI_NET,SOCK_STREAM)
        except socket.error:
            print("[SOCKET CREATION ERROR]")

    def connect_to_receiver(self):
        '''
        Transmitter'in receivere baglanmasi icin gerekli olan metod.
        :return:
        '''
        try:
            print(f"[+] Connecting to {self.RECEIVER_IP}:{self.PORT}")
            self.s.connect(self.ADDR)
            print("[+] Connected.")
        except:
            print("[RECEIVER IS NOT ACTIVE]")
            self.s.close()
            exit(1)

    def send_file(self, file_path, keep_open=False):
        '''
            Dosya gondermek icin kullanilcak metod.
        :param file_path: Dosya adini girin. Full path olarak da verebilirsiniz.
        :param keep_open: Dosya gonderiminden sonra port kapatilsin mi ? TRUE/FALSE
        :return:
        '''
        file_name = file_path.split("/")[-1]
        filesize = os.path.getsize(file_path)

        progress = tqdm.tqdm(range(filesize), f"Sending {file_path}", unit="B", unit_scale=True, unit_divisor=1024)
        self.s.send(f"{file_name}{SEPARATOR}{filesize}".encode())
        time.sleep(0.1)  # Hız. Silme

        f = open(file_path, "rb")
        readed_size = 0
        while (readed_size <= filesize):
            data = f.read(BUFFER_SIZE)
            self.s.send(data)
            progress.update(len(data))
            readed_size += BUFFER_SIZE

        f.close()
        time.sleep(0.4)  # Hız. Silme

        if not keep_open:
            # close the socket
            self.s.close()

    def send_message(self, msg="Hello World !", keep_open=False):
        '''
            Mesaj gondermek icin kullanılcak olan metod.
        :param msg: String mesaj.
        :param keep_open: Mesaj gonderiminden sonra port kapatilsin mi ? TRUE/FALSE
        :return:
        '''
        time.sleep(0.1)
        self.s.send(msg.encode())
        time.sleep(0.4)
        print("[*] Message is sent")
        if not keep_open:
            self.s.close()

    def close_all(self):
        '''
            Acik olan tum portlari kapar.
        :return:
        '''
        # close the socket
        self.s.close()

class Receiver_UDP:

    def __init__(self,PORT=6060):
        self.HOST = "0.0.0.0"
        self.PORT = PORT
        self.ADDR = (self.HOST, self.PORT)

        self.frame_info = None
        self.buffer = None
        self.frame = None

        try:
            # TCP socket
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.bind(self.ADDR)
            print(f"[*] Listening {self.HOST}:{self.PORT}")

        except socket.error:
            print("[SOCKET CREATION ERROR]")

    def receive_stream(self,record=False):
        if record:
            out = cv2.VideoWriter('output.mp4', -1, 20.0, (640, 480))
        while True:
            data, address = self.s.recvfrom(MAX_LENGTH_R)

            if len(data) < 100:
                try:
                    self.frame_info = pickle.loads(data)
                except:
                    continue
                if self.frame_info:
                    nums_of_packs = self.frame_info["packs"]

                    for i in range(nums_of_packs):
                        data, address = self.s.recvfrom(MAX_LENGTH_R)

                        if i == 0:
                            self.buffer = data
                        else:
                            self.buffer += data

                    self.frame = np.frombuffer(self.buffer, dtype=np.uint8)
                    self.frame = self.frame.reshape(self.frame.shape[0], 1)

                    self.frame = cv2.imdecode(self.frame, cv2.IMREAD_COLOR)
                    if record:
                        out.write(self.frame)
                    self.frame = cv2.flip(self.frame, 1)

                    if self.frame is not None and type(self.frame) == np.ndarray:
                        cv2.imshow("Live", self.frame)
                        if cv2.waitKey(1) == ord('q'):
                            break
                        if cv2.waitKey(1) == 27:
                            break

class Transmitter_UDP:
    def __init__(self, RECEIVER_IP="192.168.1.3",PORT=6060):
        self.RECEIVER_IP = RECEIVER_IP
        self.PORT = PORT
        self.ADDR = (self.RECEIVER_IP, self.PORT)

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # default(AFI_NET,SOCK_STREAM)
        except socket.error:
            print("[SOCKET CREATION ERROR]")

    def send_stream(self,frame,ret):
        if ret:
            # compress frame
            retval, buffer = cv2.imencode(".jpg", frame)

            if retval:
                # convert to byte array
                buffer = buffer.tobytes()
                # get size of the frame
                buffer_size = len(buffer)

                num_of_packs = 1
                if buffer_size > MAX_LENGTH_T:
                    num_of_packs = math.ceil(buffer_size / MAX_LENGTH_T)

                frame_info = {"packs": num_of_packs}

                # send the number of packs to be expected
                print(f"PACK[{num_of_packs}]")
                self.s.sendto(pickle.dumps(frame_info), self.ADDR)

                left = 0
                right = MAX_LENGTH_T

                for i in range(num_of_packs):
                    # truncate data to send
                    data = buffer[left:right]
                    left = right
                    right += MAX_LENGTH_T

                    # send the frames accordingly
                    self.s.sendto(data, self.ADDR)

if __name__ == "__main__":
    exit(1)

#####VIDEO_STREAMING###########
    """
    r = Receiver_UDP()
    r.receive_stream(record=True)
    """   
    
    """
    t = Transmitter_UDP(RECEIVER_IP="192.168.1.3")
    cap = cv2.VideoCapture(0)


    while True:

        ret, frame = cap.read()
        t.send_stream(frame,ret)
    """
#####VIDEO_STREAMING###########



 #####TCP PART ##################
    """
    r = Receiver_TCP()
    r.wait_connection()
    msg = r.receive_message(keep_open=True)
    """
    
    
    
    """
    t = Transmitter_TCP(RECEIVER_IP="192.168.1.3") # Alici bilgisayarin IP'si
    t.connect_to_receiver()
    t.send_message(msg="Hello World !",keep_open=True) 
    """
#####TCP PART ##################

#####SERVER################
    """ 
    svr = Server("http://127.0.0.1:5000/")
    svr.log_in()
    while True:
        print("----------------------------------")
        server_time = svr.get_server_time()
        print("Sunucu Saati :",server_time)
        print("----------------------------------")
        svr.post_telemetry_data()
        print("----------------------------------")
        svr.post_locking_info()
        print("----------------------------------")
        print(svr.other_teams_info)
        print("----------------------------------")
        time.sleep(0.5)
    svr.log_out() 
    """
#####SERVER################


