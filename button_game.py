from simple import GameClient, sleep, MainClient, SubClient
# from led import GameLED
from random import randint
from ClientChooser import ClientChooser
# topic = input("choose a lobby name to play against eachother: ")
topic = "ok"
my_client_id = str(randint(0, 10000))
gclient = ClientChooser(my_client_id, game_lobby=topic, main=None)
gclient.mqtt_client.loop_start()
new_client = None
while True:
    new_client = gclient.client
    if new_client:
        break
    sleep(1)
print("found new client ", new_client)
new_client.start()
# for i in range(10):
#     if gclient.main is not None:
#         break
#     print("waiting for other client...")
#     sleep(1)
# if gclient.main is None:
#     exit("timeout")

# gclient.start()

while True:
    if new_client.ended:
        break
    sleep(0.02)