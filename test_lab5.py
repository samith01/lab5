# test_lab5.py - runs on the PC, no Pico needed
# Fakes the machine and time modules, then runs lab5.py against them.
# Checks BCD decoding, the 59 -> 0 wrap, and that log.txt is appended to.
import contextlib
import io
import os
import runpy
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

LAB_DIR = Path(__file__).resolve().parent


class FakePin:
    IN = 0
    PULL_DOWN = 1
    button_values = []  # values returned by SW1.value(), in order

    def __init__(self, *args, **kwargs):
        pass

    def value(self):
        if not FakePin.button_values:
            # Out of scripted presses: stop the game loop like Ctrl+C does
            raise KeyboardInterrupt
        return FakePin.button_values.pop(0)


class FakeI2C:
    rtc_seconds = []  # raw BCD seconds bytes returned by readfrom_mem, in order

    def __init__(self, *args, **kwargs):
        pass

    def readfrom_mem(self, addr, memaddr, nbytes):
        return bytes([FakeI2C.rtc_seconds.pop(0)])


def run_lab(button_values, rtc_seconds):
    # Each trial needs 4 button reads: press, release, press, release
    FakePin.button_values = list(button_values)
    FakeI2C.rtc_seconds = list(rtc_seconds)
    fake_machine = types.SimpleNamespace(Pin=FakePin, I2C=FakeI2C)
    fake_time = types.SimpleNamespace(sleep=lambda s: None)
    with mock.patch.dict("sys.modules", {"machine": fake_machine, "time": fake_time}):
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(LAB_DIR / "lab5.py"))


class TestLab5(unittest.TestCase):
    def setUp(self):
        # Run in a temp folder so the real log.txt is never touched
        self.old_cwd = os.getcwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.tmp.cleanup()

    def read_log(self):
        with open("log.txt") as f:
            return f.read()

    def test_single_trial(self):
        # BCD 0x10 = 10 s, BCD 0x25 = 25 s -> 15 s elapsed
        run_lab([1, 0, 1, 0], [0x10, 0x25])
        self.assertEqual(self.read_log(), "15\n")

    def test_bcd_tens_digit(self):
        # BCD 0x40 = 40 s, BCD 0x55 = 55 s -> 15 s elapsed
        run_lab([1, 0, 1, 0], [0x40, 0x55])
        self.assertEqual(self.read_log(), "15\n")

    def test_wrap_past_59(self):
        # 58 s -> 13 s crosses the minute: (13 - 58) % 60 = 15
        run_lab([1, 0, 1, 0], [0x58, 0x13])
        self.assertEqual(self.read_log(), "15\n")

    def test_wrap_on_59(self):
        # 59 s -> 14 s: (14 - 59) % 60 = 15
        run_lab([1, 0, 1, 0], [0x59, 0x14])
        self.assertEqual(self.read_log(), "15\n")

    def test_append_keeps_old_lines(self):
        # Existing log.txt entries must survive a new run
        with open("log.txt", "w") as f:
            f.write("9\n")
        run_lab([1, 0, 1, 0, 1, 0, 1, 0], [0x00, 0x15, 0x30, 0x45])
        self.assertEqual(self.read_log(), "9\n15\n15\n")


if __name__ == "__main__":
    unittest.main()
