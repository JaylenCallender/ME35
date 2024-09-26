import asyncio
import neopixel
from machine import Pin, PWM

class Human:
    # Initializing all variables
    def __init__(self, zombie = 0, ID = 0):
        self.zombie = zombie
        self.ID = ID
        self.timeFirstHit = [0] * 13
        self.hitCounter = [0] * 13
        self.timeLastHit = [0] * 13
        self.led = neopixel.NeoPixel(Pin(28),1)
        self.buzzer = PWM(Pin('GPIO18', Pin.OUT))
        self.buzzer.freq(260)

    # Checks if the human has been hit enough to become a zombie
    # and sets ID to the group that has infected the human
    def check_health(self):
        for i in range(len(self.hitCounter)):
            if self.hitCounter[i] >= 3:
                self.zombie = 1
                self.ID = i + 1
                break
    
    # Control of the neopixel dimming in and out when either a human or zombie 
    # in the respected color of red being zombie and green being human
    async def light(self):
        while True:
            for i in range(255):
                if not self.zombie:
                    self.led[0] = (0, i, 0)
                elif self.zombie:
                    self.led[0] = (i, 0, 0)
                self.led.write()
                await asyncio.sleep(0.01)

            for i in range(255, 0, -1):
                if not self.zombie:
                    self.led[0] = (0, i, 0)
                elif self.zombie:
                    self.led[0] = (i, 0, 0)
                self.led.write()
                await asyncio.sleep(0.01)
            await asyncio.sleep(0)

    #When the human becomes a zombie the microcontroller will have a buzzing noise
    async def buzz(self):
        while True:
            while self.zombie:
                self.buzzer.freq(220)
                self.buzzer.duty_u16(10000)
                await asyncio.sleep(0)
            await asyncio.sleep(0)
