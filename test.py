import paho.mqtt.client as mqtt
from time import sleep

lobby_topic = "aaaaahhhh/djkjdkj/lobby"
client_id = input("your id: ")
rec_request_topic = f"{lobby_topic}/{client_id}/request"
rec_accept_topic = f"{lobby_topic}/{client_id}/accept"
# rec_accept_topic = f"{lobby_topic}/{client_id}/accept"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client:mqtt.Client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(lobby_topic)
    client.subscribe(rec_request_topic)
    client.subscribe(rec_accept_topic)
    # client.subscribe(rec_accept_topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    print(msg.topic+" "+str(msg.payload))
    if msg.payload == b"available":
        print(client._client_id + " is available.")
        input("send request ?")
        client.publish(f"aaaaahhhh/djkjdkj/lobby/{client._client_id}/request", "request")

    if msg.topic == rec_request_topic:
        print(client._client_id + " requested.")
        input("accept ?")
        # Send a request to the other client
        client.publish(f"aaaaahhhh/djkjdkj/lobby/{client._client_id}/accept", "accept")
        print("send request to ",msg.topic)
        # Wait for an accept message
        while True:
            # message = msg.payload
            print("received message ", msg.payload)
            if msg.payload == b"accept" and client._client_id == client_id:
                break
            sleep(1)
    
    if msg.topic == rec_accept_topic:
        print(client._client_id + " accepted.")
        input("start ?")
        

client = mqtt.Client(client_id=client_id)
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt.eclipseprojects.io", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
# client.loop_start()
# client.publish(lobby_topic, "available")
client.publish("aaaaahhhh/djkjdkj/lobby/a/request", "request")
client.loop_forever()


# while True:
#     sleep(5)
#     # When the client is ready to start a session with another client, it can
#     # send a broadcast message with its own client_id
#     client.publish(topic, "available")
#     print("send message")