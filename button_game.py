from simple import GameClient, sleep, Mode

def wait_for_other_client(timeout=30):
    """`timeout`: How long to wait for other client in seconds."""
    sleep(1)
    for i in range(timeout):
        if client.main is not None:
            print()
            return True
        wait_text = "Waiting for other client in lobby"
        dots = "." * (i%4)
        text = f"{wait_text}{dots:4} {i+1:02}s / {timeout:02}s"
        print(text, end="\r")
        sleep(1)
        if client.main is not None:
            print()
            return True
    print()
    return False

if __name__ == "__main__":
    topic = input("Choose a lobby name to play against eachother: ")
    my_client_id = input("Your name: ")
    client = GameClient(my_client_id, game_lobby=topic, mode=Mode.key)
    # client = GameClient(my_client_id, game_lobby=topic, mode=Mode.raspberry)
    client.mqtt_client.loop_start()

    if wait_for_other_client():
        client.start()
    else:
        print()
        exit("Timeout reached")

    while True:
        if client.ended:
            break
        sleep(1)