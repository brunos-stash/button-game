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
if gclient.main:
    keyboard.add_hotkey("s", gclient.send_tap)
    # keyboard.add_hotkey("enter", gclient.start_cd)
else:
    keyboard.add_hotkey("d", gclient.send_tap)
while True:
    if gclient.ended:
        break
    sleep(0.02)