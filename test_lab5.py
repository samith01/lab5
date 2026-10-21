# test_lab5.py - runs on the PC, no Pico needed
# lab5.py imports machine and time, which only exist on the Pico.
# So we replace them with fake versions, run lab5.py, and check log.txt.
import os
import runpy
import sys
import tempfile
import types
import unittest


class FakePin:
    # Constants that lab5.py uses when it creates a Pin
    IN = 0
    PULL_DOWN = 1

    # Button readings for the test, taken in order
    button_values = []

    def __init__(self, *args, **kwargs):
        pass

    def value(self):
        # When no readings are left, stop the game like Ctrl+C does
        if not FakePin.button_values:
            raise KeyboardInterrupt
        return FakePin.button_values.pop(0)


class FakeI2C:
    # Raw RTC seconds bytes (BCD), returned in order
    rtc_values = []

    def __init__(self, *args, **kwargs):
        pass

    def readfrom_mem(self, addr, memaddr, nbytes):
        # lab5.py asks for 1 byte, so return a 1-byte bytes object
        return bytes([FakeI2C.rtc_values.pop(0)])


def run_lab5(button_values, rtc_values):
    # Set up the fake readings
    FakePin.button_values = list(button_values)
    FakeI2C.rtc_values = list(rtc_values)

    # Put the fake modules in place of the real ones
    sys.modules["machine"] = types.SimpleNamespace(Pin=FakePin, I2C=FakeI2C)
    sys.modules["time"] = types.SimpleNamespace(sleep=lambda seconds: None)

    # Run lab5.py. It prints a lot, so hide the output here.
    runpy.run_path("lab5.py")


class TestLab5(unittest.TestCase):
    def setUp(self):
        # Work in a temporary folder so the real log.txt is not changed
        self.old_folder = os.getcwd()
        self.temp = tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)

        # Copy lab5.py into the temp folder so runpy can find it
        with open(os.path.join(self.old_folder, "lab5.py")) as f:
            code = f.read()
        with open("lab5.py", "w") as f:
            f.write(code)

    def tearDown(self):
        os.chdir(self.old_folder)
        self.temp.cleanup()

    def read_log(self):
        with open("log.txt") as f:
            return f.read()

    def test_one_trial(self):
        # Press, release, press, release = one trial
        # Start reading: 10 seconds (BCD 0x10). End reading: 25 seconds (BCD 0x25).
        # Elapsed time: 25 - 10 = 15
        run_lab5([1, 0, 1, 0], [0x10, 0x25])
        self.assertEqual(self.read_log(), "15\n")

    def test_tens_digit_in_bcd(self):
        # BCD 0x40 is 40 seconds, BCD 0x55 is 55 seconds
        # Elapsed time: 55 - 40 = 15
        run_lab5([1, 0, 1, 0], [0x40, 0x55])
        self.assertEqual(self.read_log(), "15\n")

    def test_wrap_past_one_minute(self):
        # Start at 58 s, end at 13 s (the minute rolled over)
        # Elapsed time: (13 - 58) % 60 = 15
        run_lab5([1, 0, 1, 0], [0x58, 0x13])
        self.assertEqual(self.read_log(), "15\n")

    def test_log_is_appended(self):
        # An old line is already in log.txt
        with open("log.txt", "w") as f:
            f.write("9\n")

        # Two trials, each 15 s
        run_lab5([1, 0, 1, 0, 1, 0, 1, 0], [0x00, 0x15, 0x30, 0x45])

        # The old line is still there, and the new lines are added after it
        self.assertEqual(self.read_log(), "9\n15\n15\n")


if __name__ == "__main__":
    unittest.main()
