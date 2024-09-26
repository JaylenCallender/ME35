import time
from Tufts_ble import Sniff, Yell
from Human import Human
import asyncio

THREASHOLD = -40
john = Human(zombie=1, ID= 8)

#scans bluetooth in the area 
c = Sniff('!', verbose = True)
c.scan(0)   # 0ms = scans forever 

async def run():
    global THREASHOLD
    '''
    Loop for Human. Checks for messages from zombies and updates status
    in the human class.
    '''
    currTime = 0
    while not john.zombie:
        john.check_health()
        latest = c.last
        # print(c.rssi)
        if latest:
            c.last='' # clear the flag for the next advertisement
            if latest[1:].isdigit() :  # Count only if number
                message = int(latest[1:])
                if c.rssi > THREASHOLD and message != john.ID:
                    currTime = time.time_ns() // 1000000
                    if john.timeFirstHit[message - 1] == 0:
                        # Set timeFirstHit
                        john.timeFirstHit[message - 1] = currTime
                        john.timeLastHit[message - 1] = currTime
                    else:
                        # Check if zombie left range
                        print(currTime - john.timeLastHit[message - 1])
                        if currTime - john.timeLastHit[message - 1] < 1000:

                            john.timeLastHit[message - 1] = currTime
                        # If zombie is still in range, check if it has been 3 seconds
                        else:
                            john.timeFirstHit[message - 1] = 0
                            john.timeLastHit[message - 1] = 0
                        
                        if john.timeLastHit[message - 1] - john.timeFirstHit[message - 1] >= 3000:
                            print(f'\n\n\nHIT\n\n\n')
                            john.hitCounter[message - 1] += 1
                            john.timeLastHit[message - 1] = 0
                            john.timeFirstHit[message - 1] = 0

        await asyncio.sleep(0.1)

    '''
    Loop for Zombie. Broadcasts the zombie ID number.
    '''
    p = Yell()
    print(f'Zombie: {john.ID}')
    while john.zombie:
        p.advertise(f'!{john.ID}')
        await asyncio.sleep(0.1)
        p.stop_advertising() 

async def main():
    asyncio.create_task(run())
    asyncio.create_task(john.light())
    asyncio.create_task(john.buzz())
    while True:
        await asyncio.sleep(0.01)
    
asyncio.run(main())