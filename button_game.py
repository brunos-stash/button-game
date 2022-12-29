from simple import GameClient, sleep
# from led import GameLED
import keyboard
from random import randint

my_client_id = str(randint(0, 10000))
gclient = GameClient(my_client_id, main=None)
gclient.mqtt_client.loop_start()

for i in range(10):
    sleep(1)
    if gclient.main is not None:
        break

gclient.start()

while True:
    if gclient.ended:
        break
    sleep(0.02)