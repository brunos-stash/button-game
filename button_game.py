from simple import GameClient, sleep
# from led import GameLED

my_client_id = input("your id: ")
gclient = GameClient(my_client_id, main=None)
gclient.mqtt_client.loop_start()

for i in range(10):
    sleep(1)
    if gclient.main is not None:
        break

gclient.start()

while True:
    inp = input("")
    gclient.mqtt_client.publish(gclient.game_topic+"/tap", gclient.client_id+": "+inp)