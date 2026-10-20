# drift.py - runs on the Pico
# Compares the DS3231 RTC seconds with the Pico's own millisecond timer.
# Each time the RTC seconds change, it logs the RTC total, the Pico elapsed
# ms, and the drift between them to drift_log.txt.
from machine import Pin, I2C
import time

# I2C1 bus to the DS3231 RTC (SDA = GP14, SCL = GP15)
i2c = I2C(1, sda=Pin(14), scl=Pin(15))

# read current RTC seconds (BCD -> int)
# seconds are BCD: 0x45 = 45 s (high nibble 4 = tens, low nibble 5 = ones)
raw = i2c.readfrom_mem(0x68, 0x00, 1)[0]
last_rtc = (raw >> 4) * 10 + (raw & 0x0F)

# wait for the first RTC second tick, start Pico timer on that tick
while True:
    raw = i2c.readfrom_mem(0x68, 0x00, 1)[0]
    now = (raw >> 4) * 10 + (raw & 0x0F)
    if now != last_rtc:
        break
    time.sleep(0.005)
last_rtc = now
start_ms = time.ticks_ms()
rtc_total = 0  # RTC seconds since start

# Append mode, so results from earlier runs are kept
log = open("drift_log.txt", "a")
log.write("rtc_s pico_ms drift_ms\n")

try:
    while True:
        raw = i2c.readfrom_mem(0x68, 0x00, 1)[0]
        now = (raw >> 4) * 10 + (raw & 0x0F)
        if now != last_rtc:
            # RTC ticked: count seconds, compare to Pico elapsed ms
            # modulo 60 handles the wrap 59 -> 0
            rtc_total += (now - last_rtc) % 60
            last_rtc = now
            pico_ms = time.ticks_diff(time.ticks_ms(), start_ms)
            drift_ms = pico_ms - rtc_total * 1000  # + means Pico runs slow vs RTC
            print(rtc_total, pico_ms, drift_ms)
            log.write("{} {} {}\n".format(rtc_total, pico_ms, drift_ms))
            log.flush()
        # Short sleep so the loop does not hog the CPU and still catches each tick
        time.sleep(0.005)
except KeyboardInterrupt:
    # Ctrl+C in Thonny stops the loop cleanly
    pass
finally:
    # Runs on every exit so the log file is always closed
    log.close()
    print("log saved")
