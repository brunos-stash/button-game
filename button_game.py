from simple import GameClient, sleep
# from led import GameLED
import keyboard

my_client_id = input("your id: ")
gclient = GameClient(my_client_id, main=None)
gclient.mqtt_client.loop_start()

for i in range(10):
    sleep(1)
    if gclient.main is not None:
        break

gclient.start()
if gclient.main:
    keyboard.add_hotkey("s", gclient.send_tap)
    keyboard.add_hotkey("enter", gclient.start_cd)
else:
    keyboard.add_hotkey("d", gclient.send_tap)

keyboard.wait()

# while True:

#     inp = input("")
#     gclient.mqtt_client.publish(gclient.game_topic+"/tap", gclient.client_id+": "+inp)