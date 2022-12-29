from gpiozero import LED, Button
from time import sleep
# from mqtt_client import mqtt, GameClient

class RaspBerry:
    def __init__(self) -> None:
        self.led1 = LED(17)
        self.led2 = LED(18)
        self.led3 = LED(19)
        self.button = Button(12, bounce_time = 1/60)
        self.button.hold_time = 2

    # Schaltet alle LEDs an
    def ledson(self):
        self.led1.on()
        self.led2.on()
        self.led3.on()

    # Schaltet alle LEDs aus
    def ledsoff(self):
        self.led1.off()
        self.led2.off()
        self.led3.off()

    # Zeigt den Spielstart an
    def begin_blink(self):
        self.led1.on()
        sleep(1)
        self.led2.on()
        sleep(1)
        self.led3.on()
        sleep(1)
        self.ledsoff()

    # Zeigt das Ende des Spiels an
    def end(self):
        self.led1.on()
        sleep(0.3)
        self.led1.off()
        self.led2.on()
        sleep(0.3)
        self.led2.off()
        self.led3.on()
        sleep(0.3)
        self.led3.off()
        pass

    # L�sst alle LEDs 3 mal kurz blinken
    def reset_blink(self):
        n = 4
        on_time = 0.1
        off_time = 0.1
        self.led1.blink(on_time=on_time, off_time=off_time, n=n)
        self.led2.blink(on_time=on_time, off_time=off_time, n=n)
        self.led3.blink(on_time=on_time, off_time=off_time, n=n)