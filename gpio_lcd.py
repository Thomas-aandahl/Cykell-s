from machine import Pin
from utime import sleep_us
from lcd_api import LcdApi

class GpioLcd(LcdApi):
    def __init__(self, rs_pin, enable_pin, d4_pin, d5_pin, d6_pin, d7_pin,
                 backlight_pin=None, num_lines=2, num_columns=16):
        self.rs_pin = Pin(rs_pin, Pin.OUT)
        self.enable_pin = Pin(enable_pin, Pin.OUT)
        self.d4_pin = Pin(d4_pin, Pin.OUT)
        self.d5_pin = Pin(d5_pin, Pin.OUT)
        self.d6_pin = Pin(d6_pin, Pin.OUT)
        self.d7_pin = Pin(d7_pin, Pin.OUT)
        self.backlight_pin = Pin(backlight_pin, Pin.OUT) if backlight_pin is not None else None
        super().__init__(num_lines, num_columns)

    def hal_write_command(self, cmd):
        self.rs_pin.value(0)  # Command mode
        self.hal_write_4bits(cmd >> 4)
        self.hal_write_4bits(cmd)

    def hal_write_data(self, data):
        self.rs_pin.value(1)  # Data mode
        self.hal_write_4bits(data >> 4)
        self.hal_write_4bits(data)

    def hal_write_4bits(self, nibble):
        self.d4_pin.value(nibble & 0x01)
        self.d5_pin.value(nibble & 0x02)
        self.d6_pin.value(nibble & 0x04)
        self.d7_pin.value(nibble & 0x08)
        self.hal_pulse_enable()

    def hal_pulse_enable(self):
        self.enable_pin.value(0)
        sleep_us(1)
        self.enable_pin.value(1)
        sleep_us(1)
        self.enable_pin.value(0)
        sleep_us(100)

    def hal_backlight_on(self):
        if self.backlight_pin:
            self.backlight_pin.value(1)

    def hal_backlight_off(self):
        if self.backlight_pin:
            self.backlight_pin.value(0)
