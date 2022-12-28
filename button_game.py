from simple import GameClient, sleep
# from led import GameLED

# client = mqtt.Client()
my_client_id = input("your id: ")
keep_score_inp = input("main ?")
if keep_score_inp == "y":
    keep_score = True
else:
    keep_score = False

gclient = GameClient(my_client_id, keep_score=keep_score)
print("i am keeping score: ", keep_score)

gclient.mqtt_client.loop_start()
# gclient.publish(lobby_topic, "available")
gclient.start()

while True:
    if gclient.started:
        inp = input("type input: ")
        # gclient.send_tap()
        gclient.mqtt_client.publish(gclient.game_topic+"/tap", gclient.client_id+": "+inp)
    sleep(0.1)