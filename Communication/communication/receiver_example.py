from communication import Receiver_TCP
from datetime import datetime

r = Receiver_TCP()
r.wait_connection()


for i in range(10):
    now = datetime.now()
    msg = r.receive_message(keep_open=True)
    print("Received Message :",msg," "*5,f"Received at [{now.hour}:{now.minute}:{now.second}]")

r.close_all()