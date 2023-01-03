# Button Game

# Install

For Raspberry

    sudo pip3 install -r requirements.txt

# Goal
Get 30 `taps` faster than your opponent to win. To tap you push the button.

# How to play
It can be played with `keyboard` or assembled `RaspberyPi`.

1. Agree with the other player on a `topic name` to set your unique lobby.

2. Change `mode` to `Mode.raspberry` if you're using Raspberry Pi inside `game.py`

```python
client = GameClient(my_client_id, game_lobby=topic, mode=Mode.raspberry)
```

3. Start game.

```bash    
sudo python3 game.py
```

4. Follow instructions
4. **TAP**
6. ?
7. Enjoy

# Clients
There are 2 client types. `Main` and `Sub`.

The `Main` client is responsible for:
  - keeping score
  - starting the game
  - sending relevant status messages to both clients to synchronize

# Game phases
## 1. Connection
Before connecting your client, you need the same topic name as the other player.
Both clients then connect to the open `mqtt.eclipseprojects.io` broker over the internet and wait for the other client. Then begins the main/sub negotiation.

## 2. Main / Sub negotiation
Both clients negotiate their type automatically. It works as follows:
1. Roll a random number between 0 and 10000
2. Send their number to the `status/draw` topic
3. Compare their own number with the other one
4. The client with the bigger number will become `Main` and the other one `Sub`

## 3. Starting game
Both clients wait for the main client to send `start` message to `status` topic. 
When the player with the main client pushes the button, the client will start a countdown from 3 to 0.

After it reaches 0, both players can start tapping. But players can start tapping before the countdown reaches 0 and get a penalty (negative points).

## 4. Keeping score
Both clients send their taps via the `send_tap()` function to the `tap` topic. The main client counts each taps for each client and sends back a status message to the `status/score` topic. 

Both clients read that score message and update their internal scores to determine their standing.

## 5. Ending game
The `update()` function evaluates the clients own state and if the amount of taps reaches the `finish` amount, it:
  - sends `end` message to the `status` topic to inform the other client
  - sets its own `self.ended` state to true
  - disconnects from broker