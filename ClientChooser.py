from simple import Topic, mqtt, keyboard, sleep

class GameClient:
    def __init__(self, client_id, mqtt_broker="mqtt.eclipseprojects.io", game_lobby="", main=None) -> None:
        self.topic = Topic
        self.mqtt_client = mqtt.Client(client_id=client_id)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.connect(mqtt_broker, 1883, 60)
        self.mqtt_client.user_data_set(client_id)
        self.client_id = client_id
        self.topic.lobby = "aaaaahhhh/djkjdkj/lobby/"+game_lobby
        self.topic.tap = self.topic.lobby + "/tap"
        self.topic.status = self.topic.lobby + "/status"
        self.topic.score = self.topic.status + "/score"
        self.topic.draw = self.topic.status + "/draw"
        self.main = main
        self.started = False
        self.ended = False
        self.my_score = 0
        self.op_score = 0
        self.finish = 5
        self.penalty_counter = 3
        # self._draw_nr = randint(0, 10000)
        self._draw_nr = int(client_id)
        # self.client = MainClient(client_id, mqtt_broker=mqtt_broker, game_lobby=game_lobby, main=main)

    def on_disconnect(self, client, userdata, rc):
        print("im disconnecting")

    def on_connect(self, client:mqtt.Client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.mqtt_client.subscribe(self.topic.lobby)
        self.mqtt_client.subscribe(self.topic.draw)
        self.mqtt_client.message_callback_add(self.topic.draw, self.on_draw)
        
        print("You are in lobby: ", self.topic.lobby)
        # self._draw_main()
        print("listening on status")

    # def _draw_main(self):
    #     print("sending draw nr: ", self._draw_nr)
    #     self._publish(self.topic.draw, self._draw_nr)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        _id = self._get_id(message)
        _message = self._get_message(message)
        print(f"{_message}", end="\r")
    
    def _get_id(self, message):
        return bytes.decode(message.payload).split(":")[0]

    def _get_message(self, message):
        return bytes.decode(message.payload).split(":")[1]

    def _publish(self, topic, message):
        self.mqtt_client.publish(topic, self.client_id+":"+str(message))

    def send_tap(self):
        self._publish(self.topic.tap, "tap")

    def send_score(self):
        score = f"score;{self.my_score},{self.op_score}"
        self._publish(self.topic.score, score)

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
            self.end_game()
        elif self.op_score >= self.finish:
            print("you lost")
            self.end_game()
        
    def end_game(self):
        self._publish(self.topic.status, "end")
        self.mqtt_client.unsubscribe(self.topic.status)
        self.ended = True
        self.mqtt_client.disconnect()
        print("game ended")

    def on_status(self):
        pass
    def on_tap(self):
        pass
    def on_score(self):
        pass

class ClientChooser(GameClient):
    def __init__(self, client_id, mqtt_broker="mqtt.eclipseprojects.io", game_lobby="", main=None) -> None:
        super().__init__(client_id, mqtt_broker, game_lobby, main)
        self.client = None

    def on_connect(self, client:mqtt.Client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.mqtt_client.subscribe(self.topic.lobby)
        self.mqtt_client.subscribe(self.topic.draw)
        self.mqtt_client.message_callback_add(self.topic.draw, self.on_draw)
        
        print("You are in lobby: ", self.topic.lobby)
        self._draw_main()
        print("listening on status")

    def _draw_main(self):
        print("sending draw nr: ", self._draw_nr)
        self._publish(self.topic.draw, self._draw_nr)

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
            print("im main")
            self.client = MainClient(self.client_id, game_lobby=self.topic.lobby, main=True)
        else:
            self.main = False
            print("im not main")
            self.client = SubClient(self.client_id, game_lobby=self.topic.lobby, main=False)

        self.mqtt_client.unsubscribe(self.topic.draw)
        self.mqtt_client.message_callback_remove(self.topic.draw)
        print("sending one last time my draw nr")
        self._draw_main()
        # print(self.client)

class MainClient(GameClient):
    def __init__(self, client_id, mqtt_broker="mqtt.eclipseprojects.io", game_lobby="", main=None) -> None:
        super().__init__(client_id, mqtt_broker, game_lobby, main)
        self.main = True
        # self.mqtt_client = client
        # self.mqtt_client.subscribe(self.topic.status)
        # self.mqtt_client.subscribe(self.topic.score)
        # self.mqtt_client.subscribe(self.topic.tap)
        # self.mqtt_client.message_callback_add(self.topic.status, self.on_status)
        # self.mqtt_client.message_callback_add(self.topic.score, self.on_score)
        # self.mqtt_client.message_callback_add(self.topic.tap, self.on_tap)
    # def start():
    #     pass
    # def start_cd():
    #     pass
    # def on_draw():
    #     pass
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
            self.end_game()
            # exit()
        if _message == "b4begin":
            print(f"{_id} tapped to often before game began and lost")
            self.end_game()
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
            
            if self.client_id != _id:
                return

            self.penalty_counter -= 1
            if self.penalty_counter <= 0:
                print("you lose")
                self._publish(self.topic.status, "b4begin")
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
    def start(self):
        if self.main:
            print("your key is S")
            print("start game by tapping S")
            keyboard.wait("s")
            keyboard.add_hotkey("s", self.send_tap)
            self.start_cd()
        else:
            print("your key is D")
            keyboard.add_hotkey("d", self.send_tap)
            print("waiting for main client to start")
    def start_cd(self):
        cd = 1/3
        blank = " "*50
        self._publish(self.topic.lobby, "GET READY!\n")
        sleep(1)
        for i in range(3):
            nr = str(3-i)
            for dot in range(4):
                countdown = nr + "." * dot
                self._publish(self.topic.lobby, countdown + blank)
                if self.ended:
                    return
                sleep(cd)
        self._publish(self.topic.status, "start")

class SubClient(GameClient):
    def __init__(self, client_id, mqtt_broker="mqtt.eclipseprojects.io", game_lobby="", main=None) -> None:
        super().__init__(client_id, mqtt_broker, game_lobby, main)
        self.main = False
        # self.mqtt_client = client
        # self.mqtt_client.subscribe(self.topic.status)
        # self.mqtt_client.subscribe(self.topic.score)
        # self.mqtt_client.subscribe(self.topic.tap)
        # self.mqtt_client.message_callback_add(self.topic.status, self.on_status)
        # self.mqtt_client.message_callback_add(self.topic.score, self.on_score)
        # self.mqtt_client.message_callback_add(self.topic.tap, self.on_tap)
    # def start():
    #     pass
    # def on_draw():
    #     pass
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
            self.end_game()
            # exit()
        if _message == "b4begin":
            print(f"{_id} tapped to often before game began and lost")
            self.end_game()
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
            
            if self.client_id != _id:
                return

            self.penalty_counter -= 1
            if self.penalty_counter <= 0:
                print("you lose")
                self._publish(self.topic.status, "b4begin")
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
    def start(self):
        if self.main:
            print("your key is S")
            print("start game by tapping S")
            keyboard.wait("s")
            keyboard.add_hotkey("s", self.send_tap)
            self.start_cd()
        else:
            print("your key is D")
            keyboard.add_hotkey("d", self.send_tap)
            print("waiting for main client to start")
