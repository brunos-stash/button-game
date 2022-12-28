import paho.mqtt.client as mqtt
from time import sleep
import re, random
from raspberry import RaspBerry

class GameClient:
    def __init__(self, player_id, mqtt_broker="mqtt.eclipseprojects.io") -> None:
        # self.raspberry = RaspBerry()
        # self.raspberry.button.when_pressed = self.send_tap
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(mqtt_broker, 1883, 60)
        self.msg = None
        self.player_id = player_id
        self.topic = "aaaaahhhh/djkjdkj/doo"
        self.searching = True
        self.waiting_accept = False
        self.ready = False
        self.reset = False

        self.opponent = None
        self.own_score = 0
        self.opponent_score = 0
        self.finish = 5

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.mqtt_client.subscribe(self.topic)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        self.msg = msg
    
        # ignore own messages
        if self.is_own(msg):
            return
        print(msg.topic+" "+str(msg.payload))
        if self.searching:
            if self.is_offer(msg):
                self.request_match()
            elif self.is_request(msg):
                self.accept_match()
        elif self.waiting_accept:
            if self.is_accept(msg):
                self.accept_match()
#         elif self.ready:
#             print(f"{self.player_id} ready confirmed")
#             self.start_game()
#         elif self.is_opponent_point(msg):
#             self.opponent_score += 1
#             print("opponent score", self.opponent_score)
        # in case something different
#         else:
#             print(msg.topic+" "+str(msg.payload))
#             self.opponent_score += 1
        
        if self.is_opponent_point(msg):
            self.opponent_score += 1
            print("opponent score", self.opponent_score)
            self.check_game()
        if self.is_reset(msg):
            self.reset()
    
    def is_own(self, msg):
        try:
            if self.player_id == int(re.search(br"^id(\d)", msg.payload).group(1)):
                return True
            else:
                return False
        except:
            return False
    
    def is_offer(self, msg):
        try:
            opponent = int(re.search(br"^id(\d)s\d", msg.payload).group(1))
            self.opponent = opponent
            self.searching = False
            self.waiting_accept = True
            print("found offer: ", self.opponent)
            return True
        except:
            return False
    
    def is_request(self, msg):
        try:
            request = int(re.search(br"^id\dr(\d)", msg.payload).group(1))
            if request == self.player_id:
                self.searching = False
                o = re.search(br"^id(\d)", msg.payload).group(1)
                print(f"Found request {o}")
                return True
        except:
            return False   
    
    def is_accept(self, msg):
        try:
            self.opponent = int(re.search(br"^id(\d)a", msg.payload).group(1))
            self.searching = False
            return True
        except:
            return False

    def is_opponent_point(self, msg):
        try:
            opponent = int(re.search(br"^id(\d)t", msg.payload).group(1))
#             print("opponent",opponent)
#             print("self.opponent",self.opponent)
            if self.opponent == opponent:
                return True
        except:
            return False
        
    def is_reset(self, msg):
        try:
            self.opponent = int(re.search(br"^id(\d)reset", msg.payload).group(1))
            return True
        except:
            return False
    # s<own player id>: Broadcasting your own ID
    # r<opponent id>: Requesting game with found opponent. 
    #   0 = no opponent found
    # 
    def broadcast_status(self):
        status = "id"+str(self.player_id)
        status += "s"+str(self.player_id)
        self.mqtt_client.publish(self.topic, status)
        print(f"status: {status}")

    def request_match(self):
        status = "id"+str(self.player_id)
        status += "r"+str(self.opponent)
        print(status)
        self.mqtt_client.publish(self.topic, status)

    def accept_match(self):
        print("accepting")
        status = f"id{self.player_id}a"
        self.ready = True
        self.waiting_accept = False
        print(status)
        self.mqtt_client.publish(self.topic, status)
        print(f"{self.player_id} ready")

    def start_game(self):
        # create separate topic
        pass

    def send_tap(self):
        self.mqtt_client.publish(self.topic, f"id{self.player_id}t")
        self.own_score += 1
        self.check_game()

    # def check_game(self):
    #     if self.own_score > 0:
    #         # self.raspberry.led1.on()
    #     if self.own_score >= self.finish/2:
    #         # self.raspberry.led2.on()
    #     if self.own_score >= self.finish:
    #         # self.raspberry.led3.on()
    #         print("you won")
    #         self.end_game()
    #     if self.opponent_score >= self.finish:
    #         print("you lost")
    #         self.end_game()
            
    def reset(self):
        if not self.reset:
            self.mqtt_client.publish(self.topic, f"id{self.player_id}reset")
            self.reset = True
    
    def end_game(self):
        self.searching = True
        self.waiting_accept = False
        self.ready = False
        self.reset = False
        self.msg = None
        self.opponent = None
        self.own_score = 0
        self.opponent_score = 0
        # self.raspberry.end()
        exit()
#         sleep(random.randint(0,10)/10)
#         self.start_matchmaking()
    
    def start_matchmaking(self):
        print("Matchmaking started")
        for i in range(12):
            if self.searching:
                self.broadcast_status()
            if self.waiting_accept:
                print("waiting accept")
            if self.ready:
                print(f"{self.player_id} ready")
                break
            # else:
                # print("waiting for start")
            sleep(10)
# 
# if __name__ == "__main__":
#     # Blocking call that processes network traffic, dispatches callbacks and
#     # handles reconnecting.
#     # Other loop*() functions are available that give a threaded interface and a
#     # manual interface.
#     client = mqtt.Client()
#     game_client = GameClient(int(input("your id: ")),client)
#     game_client.mqtt_client.loop_start()
#     game_client.start_matchmaking()
# #     for i in range(12):
# #         if game_client.searching:
# #             game_client.broadcast_status()
# #         if game_client.waiting_accept:
# #             print("waiting accept")
# #         if game_client.ready:
# #             print(f"{game_client.player_id} ready")
# #             break
# #         # else:
# #             # print("waiting for start")
# #         sleep(10)
#         
#     while True:
#         sleep(0.1)
#         pass
#         