import paho.mqtt.client as mqtt
from random import randint
from time import sleep
import keyboard
class GameClient:
    def __init__(self, client_id, mqtt_broker="mqtt.eclipseprojects.io", game_topic="aaaaahhhh/djkjdkj/lobby", main=None) -> None:
        # self.raspberry = RaspBerry()
        # self.raspberry.button.when_pressed = self.send_tap
        self.mqtt_client = mqtt.Client(client_id=client_id)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(mqtt_broker, 1883, 60)
        self.mqtt_client.user_data_set(client_id)
        self.client_id = client_id
        self.game_topic = game_topic
        self.main = main
        self.started = False
        self.ended = False
        self.my_score = 0
        self.op_score = 0
        self.finish = 5
        self.penalty_counter = 3
        # self._draw_nr = randint(0, 10000)
        self._draw_nr = int(client_id)

    def on_connect(self, client:mqtt.Client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.mqtt_client.subscribe(self.game_topic)
        self.mqtt_client.subscribe(self.game_topic+"/status")
        self.mqtt_client.subscribe(self.game_topic+"/status/score")
        self.mqtt_client.subscribe(self.game_topic+"/status/draw")
        self.mqtt_client.subscribe(self.game_topic+"/tap")
        self.mqtt_client.message_callback_add(self.game_topic+"/status", self.on_status)
        self.mqtt_client.message_callback_add(self.game_topic+"/status/score", self.on_score)
        self.mqtt_client.message_callback_add(self.game_topic+"/status/draw", self.on_draw)
        self.mqtt_client.message_callback_add(self.game_topic+"/tap", self.on_tap)
        self._draw_main()
        print("listening on status")

    def _draw_main(self):
        print("sending draw nr: ", self._draw_nr)
        self._publish(self.game_topic+"/status/draw", self._draw_nr)

    def on_draw(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        _id = self._get_id(message)
        _message = self._get_message(message)
        if self.client_id == _id:
            return
        try:
            nr = int(_message)
        except Exception as e:
            print("woops: ", e)
            return
        if self._draw_nr >= nr:
            self.main = True
            self.mqtt_client.unsubscribe(self.game_topic+"/status/draw")
            print("im main")
        else:
            self.main = False
            self.mqtt_client.unsubscribe(self.game_topic+"/status/draw")
            print("im not main")
        print("sending one last time my draw nr")
        self._draw_main()
        

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        _id = self._get_id(message)
        _message = self._get_message(message)
        print(f"{_message}", end="\r")

    def on_tap(self, client, userdata, message):
        # print("on_tap: ", message.payload)
        _id = self._get_id(message)
        if not self.started:
            # you are main and opponent tapped
            if self.main and (self.client_id != _id):
                self.op_score -= 1
            # you are main and you tapped
            elif self.main and (self.client_id == _id):
                self.my_score -= 1

            self.penalty_counter -= 1
            if self.penalty_counter <= 0:
                print("you lose")
                self._publish(self.game_topic+"/status", "b4begin")
            else:
                print("not started, dont try to tap before game begins again !")
                print(f"penalties left: {self.penalty_counter}")
            return
        if self.main:
            _id = self._get_id(message)
            if _id == self.client_id:
                self.my_score += 1
            else:
                self.op_score += 1
            self.send_score()

    def on_status(self, client, userdata, message):
        # print("on_status: ", message.payload)
        _id = self._get_id(message)
        _message = self._get_message(message)
        if _message == "start":
            if self.started:
                print("not started")
                return
            # you are main and you started the game
            if self.main and (self.client_id == _id):
                self.started = True
            # you are not main and main started game
            elif not self.main and (self.client_id != _id):
                self.started = True
            print("")
            print("START!")
        if _message == "end":
            print("game ended, press enter to exit")
            self.end_game()
            # exit()
        if _message == "b4begin":
            print(f"{_id} tapped to often before game began and lost")
            self.end_game()

    def on_score(self, client, userdata, message):
        _id = self._get_id(message)
        _message = self._get_message(message)
        _type, score = _message.split(";")
        if _type == "score":
            main, not_main = score.split(",")
            if not self.main and (self.client_id != _id):
                try:
                    self.my_score = int(not_main)
                    self.op_score = int(main)
                except Exception as e:
                    print("OOOooops: ", e)
            self.update()

    def _get_id(self, message):
        return bytes.decode(message.payload).split(":")[0]

    def _get_message(self, message):
        return bytes.decode(message.payload).split(":")[1]

    def start(self):
        if self.main:
            # print("press enter to start...")
            input("press enter to start...")
            self.start_cd()
        else:
            print("waiting for main client to start")

    def start_cd(self):
        keyboard.add_hotkey("enter", self.send_tap)
        cd = 1/3
        blank = " "*50
        self._publish(self.game_topic, "GET READY!\n")
        sleep(1)
        for i in range(3):
            nr = str(i+1)
            for dot in range(4):
                countdown = nr + "." * dot
                self._publish(self.game_topic, countdown + blank)
                if self.ended:
                    return
                sleep(cd)
        self._publish(self.game_topic+"/status", "start")
        keyboard.remove_hotkey("enter")

    def _publish(self, topic, message):
        self.mqtt_client.publish(topic, self.client_id+":"+str(message))

    def send_tap(self):
        self._publish(self.game_topic+"/tap", "tap")

    def send_score(self):
        score = f"score;{self.my_score},{self.op_score}"
        self._publish(self.game_topic+"/status/score", score)

    def update(self):
        print(f"my score: {self.my_score} | my opponent: {self.op_score}" )
        if self.my_score > 0:
            # self.raspberry.led1.on()
            # print("led 1 on")
            pass
        if self.my_score >= self.finish/2:
            # self.raspberry.led2.on()
            # print("led 2 on")
            pass
        if self.my_score >= self.finish:
            # self.raspberry.led3.on()
            # print("led 3 on")
            print("you won")
            if self.main:
                self.end_game()
        if self.op_score >= self.finish:
            print("you lost")
            if self.main:
                self.end_game()
        
    def end_game(self):
        # print("send end")
        self._publish(self.game_topic+"/status", "end")
        self.mqtt_client.unsubscribe(self.game_topic+"/status")
        self.ended = True

if __name__ == '__main__':
    my_client_id = input("your id: ")
    keep_score_inp = input("main ?")
    if keep_score_inp == "y":
        main = True
    else:
        main = False

    gclient = GameClient(my_client_id, main=main)
    print("i am keeping score: ", main)

    gclient.mqtt_client.loop_start()
    # gclient.publish(lobby_topic, "available")
    gclient.start()

    while True:
        if gclient.started:
            sleep(3)
            gclient.send_tap()