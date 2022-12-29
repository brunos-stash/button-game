from simple import GameClient, sleep
# from led import GameLED
from random import randint

topic = input("choose a lobby name to play against eachother: ")
my_client_id = str(randint(0, 10000))
gclient = GameClient(my_client_id, game_lobby=topic, main=None)
gclient.mqtt_client.loop_start()

for i in range(10):
    sleep(1)
    if gclient.main is not None:
        break
if gclient.main is None:
    exit("timeout")

gclient.start()

while True:
    if gclient.ended:
        break
    sleep(0.02)