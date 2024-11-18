import asyncio, neopixel, time
from machine import Pin
import time
from networking import Networking

RED = (100, 0, 0)
ORANGE = (100, 65, 0)
BLUE = (0, 0, 100)
WHITE = (100, 100, 100)
GREEN = (0, 128, 0)
OFF = (0, 0, 0)

#Initialise
networking = Networking()
recipient_mac = b'\xFF\xFF\xFF\xFF\xFF\xFF' #This mac sends to all

class Dragon:
    def __init__(self, playerCount = 4):
        self.button = Pin('GPIO20', Pin.IN)
        self.led = neopixel.NeoPixel(Pin(28),1)
        self.cooldown = 0
        self.totalGametime = 300 #5 minute timer 
        self.scorched = False #Boolean when all wizards have been scorched
        self.wizards = {
        }
        self.msg = ''
        self.incomingMac = b'\x00\x00\x00\x00\x00\x00'
        self.playerCount = playerCount


    def receive(self):
        print("Receive")
        for mac, message, rtime in networking.aen.return_messages(): #You can directly iterate over the function
            self.msg = message
            self.incomingMac = mac

    async def listen_ID(self):
        
        while True:

            if self.scorched:
                break

            # Receive wizard id
            networking.aen.irq(self.receive())

            if self.incomingMac != None:
                self.wizards[self.incomingMac] = 1

            # Check if all wizards are hit
            if len(self.wizards) == self.playerCount:
                self.scorched = True

            self.msg = ''

            await asyncio.sleep(0.1)

    async def breath_fire(self):
        prevButton = 0
        message =  'breathingFire'
        while True:
            # Conditional to Breath Fire if button is pressed and not on cooldown
            if self.button != prevButton and prevButton and not self.cooldown:
                networking.aen.echo(recipient_mac, message)
                self.cooldown = 1
            prevButton = self.button
            await asyncio.sleep(0.05)

    async def manage_fire(self):
        while True:
            # Begin 15 second cooldown
            if self.cooldown:
                await asyncio.sleep(15) 
                self.cooldown = 0

    async def neoPixel(self):
        while True:
            
            # Blink orange to indicate cooldown
            if self.cooldown:
                self.led[0] = ORANGE
                await asyncio.sleep(0.25)
                self.led[0] = OFF
                await asyncio.sleep(0.25)

            # Show white to indicate game in progress
            self.led[0] = WHITE
            await asyncio.sleep(0)
    
    async def timer(self):
        #Timer decrementing till 10 minutes has gone by
        while self.totalGametime > 0:
            minutes, seconds = divmod(self.totalGametime, 60)
            print(f"Time remaining: {minutes:02d}:{seconds:02d}", end='\r')
            await asyncio.sleep(.1)
            self.totalGametime -= 1

    async def gameOver(self):
        while True:
            if self.scorched:
                self.led[0] = GREEN #Scorch tagged everyone else
            elif self.totalGametime == 0:
                self.led[0] = RED #Wizards outlasted the timer
            await asyncio.sleep(.01)

    

    async def main(self):

        task1 = self.breath_fire()
        task2 = self.manage_fire()
        task3 = self.neoPixel()
        task4 = self.timer()
        task5 = self.gameOver()

        asyncio.gather(task1, task2, task3, task4, task5)


