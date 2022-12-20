import paho.mqtt.client as mqtt
from time import sleep

class GameClient:
    def __init__(self, client_id, mqtt_broker="mqtt.eclipseprojects.io", game_topic="aaaaahhhh/djkjdkj/lobby", keep_score=False) -> None:
        # self.raspberry = RaspBerry()
        # self.raspberry.button.when_pressed = self.send_tap
        self.mqtt_client = mqtt.Client(client_id=client_id)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(mqtt_broker, 1883, 60)
        self.mqtt_client.user_data_set(client_id)
        self.client_id = client_id
        self.game_topic = game_topic
        self.keep_score = keep_score
        self.started = False
        self.my_score = 0
        self.op_score = 0

    def on_connect(self, client:mqtt.Client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.mqtt_client.subscribe(self.game_topic)

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        _id, _message = bytes.decode(msg.payload).split(":")
        if  self.client_id == _id:
            return
        print(f"{_id}: {_message}")
        # print("_id:", _id)
        
        if not self.started:
            if _message == "start":
                self.started = True
        else:
            if self.keep_score:
                self.op_score += 1
                print(f"score: {self.mqtt_client._client_id}={self.my_score}, {client._client_id}:{self.op_score}")
    
    def start(self):
        if self.keep_score:
            input("start ?")
            self.mqtt_client.publish(self.game_topic, self.client_id+":start")
            self.started = True
        else:
            print("waiting for other to start")

    def send_tap(self):
        if self.keep_score:
            self.my_score += 1
        self.mqtt_client.publish(self.game_topic, self.client_id+":tap")

if __name__ == '__main__':
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
            sleep(3)
            gclient.send_tap()