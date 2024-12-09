import time
from machine import Pin
from gpio_lcd import GpioLcd
relay_pin = 19  

lcd = GpioLcd(rs_pin=Pin(27), 
               enable_pin=Pin(25),
               d4_pin=Pin(33),
               d5_pin=Pin(32),
               d6_pin=Pin(21),
               d7_pin=Pin(22),
               num_lines=4, 
               num_columns=20)


#keypad dimensioner
NUM_ROWS = 4
NUM_COLS = 4

#GPIO pins til keypad
ROW_PINS = [18, 12, 14, 26]   
COLUMN_PINS = [15, 2, 4, 13]


#layout ti keypad 4x4
KEYMAP = ['1', '2', '3', 'A',
          '4', '5', '6', 'B',
          '7', '8', '9', 'C',
          '*', '0', '#', 'D']

class Keypad:
    def __init__(self):
        # keypad pins IN OUT registering 
        self.row_pins = [Pin(pin, Pin.OUT) for pin in ROW_PINS]
        self.col_pins = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in COLUMN_PINS]

    def get_key(self):
        for r in range(NUM_ROWS):
            for row in self.row_pins:
                row.value(1)  # register pin tryk til lav
            self.row_pins[r].value(0)  # register ikke pin tryk til høj

            for c in range(NUM_COLS):
                if not self.col_pins[c].value():  # hvis pin er lav, key er trykket 
                    while not self.col_pins[c].value():  # vent til key er slippet
                        pass  # Busy wait until the key is released
                    return KEYMAP[r * NUM_COLS + c]  # Retuner den trykket bkey
        return None

# Initialize keypad
keypad = Keypad()
# Initialize relay for solenoid control
solenoid_relay = Pin(relay_pin, Pin.OUT)
solenoid_relay.value(0)  # Ensure solenoid is off at startup

def get_key_with_debounce(keypad):
    pressed_key = None
    debounce_time = 0.3  
    last_key = None
    last_pressed_time = 0

    while True:
        key = keypad.get_key()  # Get den trykket key i shell

        if key is not None and key != last_key:  # ny key er trykket
            current_time = time.ticks_ms()
            if current_time - last_pressed_time > debounce_time * 1000:  # Check debounce
                last_pressed_time = current_time
                last_key = key
                return key  # Returner valid key i shell
        time.sleep(0.01)  # Small delay CPU usage

# Definer kodeord
PASSWORD = "1234"  # kodeord
attempted_password = ""

# loop
while True:
    key = get_key_with_debounce(keypad)
    if key is not None:
        print(f"Key pressed: {key}")
        attempted_password += key  # tilføj trykket key til attempted password
        print(f"Attempted Password: {attempted_password}")  # Print forsøget password
        lcd.clear()
        lcd.putstr(f" {attempted_password}")  # Show entered keys on LCD
        lcd.move_to(0,0)
        

        # Check om input er samme længde som password
        if len(attempted_password) == len(PASSWORD):
            if attempted_password == PASSWORD:
                print("Bicycle Unlocked!")
                lcd.clear()
                lcd.putstr("Bicycle Unlocked!")
                solenoid_relay.value(1)  # Activate the solenoid
                #time.sleep(5)  # Keep the solenoid active for 5 seconds
                #solenoid_relay.value(0)  # Deactivate the solenoid
                attempted_password = ""  # Reset forsøget password
            else:
                print("Access Denied! Try Again.")
                lcd.clear()
                lcd.putstr("wrong kode!")
                attempted_password = ""  # Reset to give another chance