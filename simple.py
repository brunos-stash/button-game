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
        self.finish = 5

    def on_connect(self, client:mqtt.Client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.mqtt_client.subscribe(self.game_topic)
        self.mqtt_client.subscribe(self.game_topic+"/status")
        self.mqtt_client.subscribe(self.game_topic+"/tap")
        self.mqtt_client.message_callback_add(self.game_topic+"/status", self.on_status)
        self.mqtt_client.message_callback_add(self.game_topic+"/tap", self.on_tap)
        print("listening on status")


    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        _id = self._get_id(message)
        _message = self._get_message(message)
        if  self.client_id == _id:
            return
        print(f"on_message: {_id}: {_message}")
        
        if not self.started:
            if _message == "start":
                self.started = True
        # else:
        #     if self.keep_score:
        #         self.op_score += 1
        #         self.update()

    def on_tap(self, client, userdata, message):
        if self.keep_score:
            _id = self._get_id(message)
            if _id == self.client_id:
                self.my_score += 1
            else:
                self.op_score += 1
            self.update()

    def on_status(self, client, userdata, message):
        print("on_status: ", message.payload)
        if not self.keep_score:
            pass
    
    def _get_id(message):
        return bytes.decode(message.payload).split(":")[0]

    def _get_message(message):
        return bytes.decode(message.payload).split(":")[1]

    def start(self):
        if self.keep_score:
            input("start ?")
            # self.mqtt_client.publish(self.game_topic, self.client_id+":start")
            self._publish(self.game_topic+"/status", "start")
            self.started = True
        else:
            print("waiting for other to start")

    def _publish(self, topic, message):
        self.mqtt_client.publish(topic, self.client_id+":"+message)

    def send_tap(self):
        if self.keep_score:
            self.my_score += 1
        self._publish(self.game_topic+"/tap", "tap")

    def update(self):
        print(f"score: {self.mqtt_client._client_id}={self.my_score}, :{self.op_score}")
        if self.my_score > 0:
            # self.raspberry.led1.on()
            print("led 1 on")
        if self.my_score >= self.finish/2:
            # self.raspberry.led2.on()
            print("led 2 on")
        if self.my_score >= self.finish:
            # self.raspberry.led3.on()
            print("led 3 on")
            print("you won")
            if self.keep_score:
                self.end_game()
        if self.op_score >= self.finish:
            print("you lost")
            if self.keep_score:
                self.end_game()
        

    def end_game(self):
        print("game ended.")

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