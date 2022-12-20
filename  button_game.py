from mqtt_client import GameClient, sleep
# from led import GameLED

# client = mqtt.Client()
game_client = GameClient(int(input("your id: ")))
game_client.mqtt_client.loop_start()
game_client.start_matchmaking()
    
while True:
    sleep(0.1)
    pass