import paho.mqtt.client as mqtt
from random import randint
from time import sleep
import keyboard
from dataclasses import dataclass

@dataclass
class Topic:
    lobby: str
    status: str
    score: str
    draw: str
    tap: str

class GameClient:
    """Client that establishes MQTT connection and manages game logic and its state."""
    def __init__(self, client_id, mqtt_broker="mqtt.eclipseprojects.io", game_lobby="", main=None) -> None:
        """
        `client_id`: Your clients name.

        `mqtt_broker`: URL to the broker. By default uses Eclipses' broker "mqtt.eclipseprojects.io"
        which is accessible from the internet and everyone.

        `game_lobby`: Name of the lobby to meet the other client. 
        Both clients should have the same game_lobby to be able to play against eachother.

        `main`: Determines if this client is main or sub.
        Main client keeps the score for both clients and handles status updates.
        If `None` both clients will determine main/sub automatically.
        Your and your opponents client can't have the same type.
        """
        # self.raspberry = RaspBerry()
        # self.raspberry.button.when_pressed = self.send_tap
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
        self.penalty_counter = 5
        # self._draw_nr = randint(0, 10000)
        self._draw_nr = int(client_id)
    
    def _publish(self, topic, message):
        """Attaches your `client_id` before sending a message to the specified topic."""
        self.mqtt_client.publish(topic, self.client_id+":"+str(message))

    def _get_id(self, message):
        """Convenient method to get `client_id` from message."""
        return bytes.decode(message.payload).split(":")[0]

    def _get_message(self, message):
        """Convenient method to get `message` String from message."""
        return bytes.decode(message.payload).split(":")[1]

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        """Callback function when a message arrives at `topic.lobby`."""
        _id = self._get_id(message)
        _message = self._get_message(message)
        print(f"{_message}", end="\r")

    def on_connect(self, client:mqtt.Client, userdata, flags, rc):
        """Callback function when this client connects to the broker."""
        print("Connected with result code "+str(rc))
        self.mqtt_client.subscribe(self.topic.lobby)
        self.mqtt_client.subscribe(self.topic.draw)
        self.mqtt_client.message_callback_add(self.topic.draw, self.on_draw)
        
        print("You are in lobby: ", self.topic.lobby)
        self._draw_main()
        # print("listening on status")

    def on_disconnect(self, client, userdata, rc):
        """Callback function when this client disconnects cleanly from the broker."""
        print("Disconnected")

    def _draw_main(self):
        """Sends `self._draw_nr` to `topic.draw` to compare with the other client 
        to negotiate the main and sub client."""
        # print("sending draw nr: ", self._draw_nr)
        self._publish(self.topic.draw, self._draw_nr)

    def on_draw(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        """Callback function when other client sends its own `self._draw_nr`.

        The biggest number will be the main client and keep the score or
        send relevant status updates to synchronize both clients."""

        _id = self._get_id(message)
        _message = self._get_message(message)
        if self.client_id == _id:
            return
        try:
            nr = int(_message)
        except Exception as e:
            print("Ooops: ", e)
            return
        if self._draw_nr >= nr:
            self.main = True
            # print("im main")
        else:
            self.main = False
            # print("im not main")
        self.mqtt_client.unsubscribe(self.topic.draw)
        self.mqtt_client.message_callback_remove(self.topic.draw)
        # print("sending one last time my draw nr")
        self._draw_main()
        self.mqtt_client.subscribe(self.topic.status)
        self.mqtt_client.subscribe(self.topic.score)
        self.mqtt_client.subscribe(self.topic.tap)
        self.mqtt_client.message_callback_add(self.topic.status, self.on_status)
        self.mqtt_client.message_callback_add(self.topic.score, self.on_score)
        self.mqtt_client.message_callback_add(self.topic.tap, self.on_tap)
    
    def start(self):
        """Main client method. If main/sub clients are determined, this will start the game."""
        if self.main:
            print("Tap key is 'S'")
            print("Start game by tapping 'S'")
            keyboard.wait("s")
            keyboard.add_hotkey("s", self.send_tap)
            self._start_countdown()
        else:
            print("Tap key is 'D'")
            keyboard.add_hotkey("d", self.send_tap)
            print("Waiting for other client to start the game. Be ready.")

    def _start_countdown(self):
        """Main client method. Starts the countdown for both clients."""
        cd = 1/3
        blank = " "*50
        self._publish(self.topic.lobby, "GET READY!\n")
        sleep(1)
        for i in range(3):
            nr = str(3-i)
            for dot in range(4):
                countdown = f" {nr} {'.'*dot}"
                self._publish(self.topic.lobby, countdown + blank)
                if self.ended:
                    return
                sleep(cd)
        self._publish(self.topic.status, "start")

    def on_status(self, client, userdata, message):
        """Callback function for status updates. Listening on `topic.status`"""
        # print("on_status: ", message.payload)
        _id = self._get_id(message)
        _message = self._get_message(message)
        if _message == "start":
            # you are main client and you started the game
            if self.main and (self.client_id == _id):
                self.started = True
            # you are sub client and main client started game
            elif not self.main and (self.client_id != _id):
                self.started = True
            print("")
            print("START!")
        if _message == "end":
            self.end_game()
        if _message == "b4begin":
            print(f"Client '{_id}' tapped to often before game started and lost.")
            self.end_game()
    
    def on_tap(self, client, userdata, message):
        """Callback function for receiving 'tap' messages when clients are pushing buttons."""
        # print("on_tap: ", message.payload)
        _id = self._get_id(message)
        if not self.started:
            # you are main client and opponent tapped
            if self.main and (self.client_id != _id):
                self.op_score -= 1
            # you are main client and you tapped
            elif self.main and (self.client_id == _id):
                self.my_score -= 1
            
            # no penalties for other clients actions
            if self.client_id == _id:
                self._handle_penalty()
            return
        # main client keeps score for both clients
        if self.main:
            _id = self._get_id(message)
            if _id == self.client_id:
                self.my_score += 1
            else:
                self.op_score += 1
            self.send_score()

    def _handle_penalty(self):
        """Method to decrease score, if client taps before game begins."""
        self.penalty_counter -= 1
        if self.penalty_counter <= 0:
            print("you lose")
            self._publish(self.topic.status, "b4begin")
        else:
            print("DON'T TAP BEFORE COUNTER! -1 POINT!")
            print(f"Penalties left: {self.penalty_counter}")

    def on_score(self, client, userdata, message):
        """Callback function to handle score updates from `topic.score`."""
        _id = self._get_id(message)
        _message = self._get_message(message)
        _type, score = _message.split(";")
        if _type == "score":
            main, not_main = score.split(",")
            # you are sub client and score update comes from main client
            if not self.main and (self.client_id != _id):
                try:
                    self.my_score = int(not_main)
                    self.op_score = int(main)
                except Exception as e:
                    print("OOOooops: ", e)
            self.update()

    def send_tap(self):
        """Convenient function to send 'tap' messages to `topic.tap`."""
        self._publish(self.topic.tap, "tap")

    def send_score(self):
        """Main client function to send score update messages to `topic.score`.
        
        Format: `score;<main_client_score>,<sub_client_score>`.
        Example: `score;1,4`
        """
        score = f"score;{self.my_score},{self.op_score}"
        self._publish(self.topic.score, score)

    def update(self):
        """Determines the current state of this client based on `self.my_core`.
        
        Ends the game if finish is reached.
        """
        print(f"My score: {self.my_score:02} | Opponents score: {self.op_score:02}" )
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
            print("You win!")
            self.end_game()
        elif self.op_score >= self.finish:
            print("You lose!")
            self.end_game()
        
    def end_game(self):
        """Ends game by sending `end` status to `topic.status´ and then disconnects."""
        self._publish(self.topic.status, "end")
        self.mqtt_client.unsubscribe(self.topic.status)
        self.ended = True
        self.mqtt_client.disconnect()
        print("Game over")