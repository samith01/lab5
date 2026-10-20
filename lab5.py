# lab5.py - runs on the Pico
# Times 15 s with the DS3231 RTC. Press SW1 to take the start reading,
# press again after about 15 s to take the end reading. Each elapsed
# time is appended to log.txt, one value per line.
from machine import Pin, I2C
import time

# I2C1 bus to the DS3231 RTC (SDA = GP14, SCL = GP15)
i2c = I2C(1, sda=Pin(14), scl=Pin(15))

# Push button on GP13, pulled down, so the pin reads 1 while pressed
SW1 = Pin(13, Pin.IN, Pin.PULL_DOWN)

# Append mode, so results from earlier runs are kept
log = open("log.txt", "a")

try:
    while True:
        print("press button to start")
        # Wait for the press, then for the release
        # 0.05 s sleeps debounce the button
        while SW1.value() == 0:
            pass
        time.sleep(0.05)
        while SW1.value() == 1:
            pass
        time.sleep(0.05)

        # Read the RTC seconds register (0x00 at address 0x68)
        # seconds are BCD: 0x45 = 45 s (high nibble 4 = tens, low nibble 5 = ones)
        raw = i2c.readfrom_mem(0x68, 0x00, 1)[0]
        start = (raw >> 4) * 10 + (raw & 0x0F)

        print("count 15 seconds, press button again")
        # Wait for the second press and release, same debounce as above
        while SW1.value() == 0:
            pass
        time.sleep(0.05)
        while SW1.value() == 1:
            pass
        time.sleep(0.05)

        # Read the RTC seconds again
        raw = i2c.readfrom_mem(0x68, 0x00, 1)[0]
        end = (raw >> 4) * 10 + (raw & 0x0F)

        # RTC seconds wrap 59 -> 0, so modulo 60 gives elapsed seconds
        elapsed = (end - start) % 60
        print(elapsed)
        log.write("{}\n".format(elapsed))
        log.flush()

except KeyboardInterrupt:
    # Ctrl+C in Thonny stops the loop cleanly
    pass

finally:
    # Runs on every exit so the log file is always closed
    log.close()
    print("log saved")
