from simple import GameClient, sleep
# from led import GameLED
from random import randint

# topic = input("choose a lobby name to play against eachother: ")
topic = "ok"
# my_client_id = str(randint(0, 10000))
my_client_id = input("my id:")
gclient = GameClient(my_client_id, game_lobby=topic, main=None)
gclient.mqtt_client.loop_start()

timeout = 10
sleep(1)
# print()
for i in range(timeout):
    if gclient.main is not None:
        break
    wait_text = "Waiting for other client in lobby"
    dots = "." * (i%4)
    text = f"{wait_text}{dots:4} {i+1:02}s / {timeout:02}s"
    print(text, end="\r")
    sleep(1)
    if gclient.main is not None:
        break
print()
if gclient.main is None:
    print()
    exit("Timeout reached")

gclient.start()

while True:
    if gclient.ended:
        break
    sleep(0.02)