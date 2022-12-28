from simple import GameClient, sleep
# from led import GameLED

# client = mqtt.Client()
my_client_id = input("your id: ")
main_inp = input("main ?")
if main_inp == "y":
    main = True
else:
    main = False

gclient = GameClient(my_client_id, main=main)
print("i am main client: ", main)

gclient.mqtt_client.loop_start()
# gclient.publish(lobby_topic, "available")
gclient.start()

while True:
    if gclient.started:
        inp = input("")
        # gclient.send_tap()
        gclient.mqtt_client.publish(gclient.game_topic+"/tap", gclient.client_id+": "+inp)
    sleep(0.1)