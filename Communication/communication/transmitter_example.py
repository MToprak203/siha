from communication import Transmitter_TCP
from datetime import datetime

t = Transmitter_TCP(RECEIVER_IP="192.168.1.3") # Alici bilgisayarin IP'si
t.connect_to_receiver()


for i in range(10):
    now = datetime.now()
    t.send_message(msg="Hello World !",keep_open=True)
    print(f"Sended at [{now.hour}:{now.minute}:{now.second}]")

t.close_all()